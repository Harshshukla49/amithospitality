from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from typing import List, Optional
import io
import csv

from app.database import get_db
from app.models.reservation import ReservationRequest
from app.models.outlet import Outlet
from app.models.audit import EnvironmentSetting
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
    is_demo = active_env == "DEMO"

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
        status="NEW",
        internal_notes="DEMO SIMULATION" if is_demo else "Online concierge booking inquiry",
    )
    db.add(new_res)
    db.commit()
    db.refresh(new_res)
    return new_res

@router.get("", response_model=List[ReservationResponse])
def list_reservations(
    outlet_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    environment: Optional[str] = Query(None),
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN", "MANAGER", "STAFF")),
    db: Session = Depends(get_db),
):
    target_env = environment or get_current_env(db)
    query = db.query(ReservationRequest).filter(ReservationRequest.environment == target_env)

    if outlet_id:
        query = query.filter(ReservationRequest.outlet_id == outlet_id)
    if status and status != "ALL":
        query = query.filter(ReservationRequest.status == status)

    return query.order_by(ReservationRequest.created_at.desc()).all()

@router.patch("/{res_id}/status", response_model=ReservationResponse)
def update_reservation_status(
    res_id: int,
    status_update: ReservationStatusUpdate,
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN", "MANAGER", "STAFF")),
    db: Session = Depends(get_db),
):
    res = db.query(ReservationRequest).filter(ReservationRequest.id == res_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Reservation request not found")

    res.status = status_update.status
    if status_update.internal_notes:
        res.internal_notes = status_update.internal_notes
    res.assigned_staff_id = current_user.id

    db.commit()
    db.refresh(res)
    return res

@router.get("/export")
def export_reservations_csv(
    environment: Optional[str] = Query(None),
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN")),
    db: Session = Depends(get_db),
):
    target_env = environment or get_current_env(db)
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
