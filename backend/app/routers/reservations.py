from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Any
import io
import csv

from app.database import get_db
from app.models.reservation import ReservationRequest
from app.models.outlet import Outlet
from app.models.audit import EnvironmentSetting, AuditLog
from app.models.user import User
from app.schemas.reservation import (
    ReservationCreate,
    ReservationStatusUpdate,
    ReservationResponse,
)
from app.utils.security import require_roles, get_current_user

router = APIRouter(prefix="/api/v1/reservations", tags=["Reservations Workflow"])

def get_current_env(db: Session) -> str:
    setting = db.query(EnvironmentSetting).order_by(EnvironmentSetting.id.desc()).first()
    return setting.active_environment if setting else "DEMO"

@router.post("", response_model=ReservationResponse)
def create_reservation(req: ReservationCreate, db: Session = Depends(get_db)):
    outlet = db.query(Outlet).filter(Outlet.id == req.outlet_id).first()
    if not outlet:
        raise HTTPException(status_code=404, detail="Outlet not found")

    active_env = get_current_env(db)
    is_demo = (active_env == "DEMO")

    # Conflict / Capacity Limit Check
    existing_guests = (
        db.query(func.sum(ReservationRequest.guest_count))
        .filter(
            ReservationRequest.outlet_id == req.outlet_id,
            ReservationRequest.reservation_date == req.reservation_date,
            ReservationRequest.environment == active_env,
            ReservationRequest.status.in_(["NEW", "PENDING", "UNDER_REVIEW", "ACCEPTED"]),
        )
        .scalar()
        or 0
    )

    capacity_warning = None
    capacity_limit = outlet.seating_capacity or 100
    if existing_guests + req.guest_count > capacity_limit:
        capacity_warning = (
            f"CAPACITY NOTICE: High occupancy alert: Booked guests ({existing_guests + req.guest_count}) "
            f"exceeds standard seating threshold ({capacity_limit}). Reservation flagged for Manager Review."
        )

    notes = "DEMO SIMULATION" if is_demo else "Online concierge booking request"
    if capacity_warning:
        notes += f" | {capacity_warning}"

    new_res = ReservationRequest(
        environment=active_env,
        outlet_id=req.outlet_id,
        outlet_name=outlet.name,
        guest_name=req.guest_name,
        guest_phone=req.guest_phone,
        guest_email=req.guest_email,
        guest_count=req.guest_count,
        reservation_date=req.reservation_date,
        reservation_time=req.reservation_time,
        seating_preference=req.seating_preference,
        special_requests=req.special_requests,
        status="UNDER_REVIEW" if capacity_warning else "NEW",
        internal_notes=notes,
    )
    db.add(new_res)
    db.commit()
    db.refresh(new_res)

    # Attach transient capacity warning for response
    setattr(new_res, "capacity_warning", capacity_warning)
    return new_res

@router.get("", response_model=List[ReservationResponse])
def list_reservations(
    outlet_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    environment: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    target_env = environment if isinstance(environment, str) else get_current_env(db)
    query = db.query(ReservationRequest).filter(ReservationRequest.environment == target_env)

    if outlet_id and isinstance(outlet_id, int):
        query = query.filter(ReservationRequest.outlet_id == outlet_id)
    if status and isinstance(status, str) and status != "ALL":
        query = query.filter(ReservationRequest.status == status)

    return query.order_by(ReservationRequest.created_at.desc()).all()

@router.patch("/{res_id}/status", response_model=ReservationResponse)
def update_reservation_status(
    res_id: int,
    status_update: ReservationStatusUpdate,
    current_user: Any = None,
    db: Session = Depends(get_db),
):
    res = db.query(ReservationRequest).filter(ReservationRequest.id == res_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Reservation request not found")

    old_status = res.status
    res.status = status_update.status
    if status_update.internal_notes:
        res.internal_notes = status_update.internal_notes

    # Create immutable audit log
    audit_user_name = current_user.full_name if (current_user and hasattr(current_user, "full_name")) else "Staff / Admin"
    audit_user_role = current_user.role if (current_user and hasattr(current_user, "role")) else "STAFF"
    audit = AuditLog(
        user_name=audit_user_name,
        user_role=audit_user_role,
        action="RESERVATION_STATUS_UPDATE",
        entity_type="RESERVATION",
        entity_id=res.id,
        environment=res.environment,
        details=f"Reservation #{res.id} for {res.guest_name} status updated: {old_status} -> {status_update.status}. Notes: {status_update.internal_notes or 'None'}",
    )
    db.add(audit)
    db.commit()
    db.refresh(res)
    return res

@router.get("/export")
def export_reservations_csv(
    environment: Optional[str] = Query(None),
    current_user: Any = None,
    db: Session = Depends(get_db),
):
    target_env = environment if isinstance(environment, str) else get_current_env(db)
    reservations = db.query(ReservationRequest).filter(ReservationRequest.environment == target_env).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Environment", "Outlet", "Guest Name", "Phone", "Email",
        "Party Size", "Date", "Time", "Seating", "Status", "Notes"
    ])

    for r in reservations:
        writer.writerow([
            r.id, r.environment, r.outlet_name, r.guest_name, r.guest_phone,
            r.guest_email or "", r.guest_count, r.reservation_date,
            r.reservation_time, r.seating_preference, r.status, r.internal_notes or ""
        ])

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=reservations_{target_env.lower()}.csv"},
    )
