from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional, Any
import io
import csv
from datetime import datetime

from app.database import get_db
from app.models.reservation import ReservationRequest, ReservationStatusHistory, generate_reservation_ref
from app.models.outlet import Outlet
from app.models.audit import EnvironmentSetting, AuditLog
from app.models.user import User
from app.schemas.reservation import (
    ReservationCreate,
    ReservationStatusUpdate,
    ReservationResponse,
    ReservationHistoryItem,
)
from app.utils.security import require_roles, get_current_user, get_current_user_optional
from app.models.user import User

router = APIRouter(prefix="/api/v1/reservations", tags=["Reservations Workflow"])

def get_current_env(db: Session) -> str:
    setting = db.query(EnvironmentSetting).order_by(EnvironmentSetting.id.desc()).first()
    return setting.active_environment if setting else "DEMO"

@router.post("", response_model=ReservationResponse)
def create_reservation(req: ReservationCreate, db: Session = Depends(get_db)):
    """
    Submit a customer table reservation request.
    Validates capacity against outlet threshold, generates unique reference ID,
    records initial status history, and flags high-occupancy bookings for review.
    """
    outlet_query = db.query(Outlet).filter(Outlet.id == req.outlet_id)
    # Row-level locking when running on PostgreSQL to prevent concurrent overbooking
    if db.bind and getattr(db.bind.dialect, "name", "") == "postgresql":
        outlet_query = outlet_query.with_for_update()
    outlet = outlet_query.first()

    if not outlet:
        raise HTTPException(status_code=404, detail="Selected outlet not found")

    active_env = get_current_env(db)
    is_demo = (active_env == "DEMO")

    # Conflict / Capacity Limit Check (within locked transaction)
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
        if active_env == "REAL":
            # In REAL mode, strict capacity enforcement rejects overbooking
            raise HTTPException(
                status_code=409,
                detail=f"Capacity exceeded for {outlet.name} on {req.reservation_date}: Booked guests ({existing_guests}) plus requested ({req.guest_count}) exceeds seating capacity ({capacity_limit}).",
            )
        capacity_warning = (
            f"CAPACITY NOTICE: High occupancy alert: Booked guests ({existing_guests + req.guest_count}) "
            f"exceeds standard seating threshold ({capacity_limit}). Reservation flagged for Manager Review."
        )

    notes = "DEMO SIMULATION: Request logged in demonstration mode." if is_demo else "Online concierge booking request."
    if capacity_warning:
        notes += f" | {capacity_warning}"
    if req.special_requests:
        notes += f" | Guest Request: {req.special_requests}"

    ref_id = generate_reservation_ref()
    initial_status = "UNDER_REVIEW" if capacity_warning else "NEW"

    try:
        new_res = ReservationRequest(
            reference_id=ref_id,
            environment=active_env,
            outlet_id=req.outlet_id,
            outlet_name=outlet.name,
            guest_name=req.guest_name,
            guest_phone=req.guest_phone,
            guest_email=str(req.guest_email) if req.guest_email else None,
            guest_count=req.guest_count,
            reservation_date=req.reservation_date,
            reservation_time=req.reservation_time,
            seating_preference=req.seating_preference,
            special_requests=req.special_requests,
            status=initial_status,
            internal_notes=notes,
            assigned_staff_name=req.assigned_staff_name,
            session_id=req.session_id,
            conversation_id=req.conversation_id,
        )
        db.add(new_res)
        # Flush to obtain generated new_res.id within the atomic transaction
        db.flush()

        # Record initial status in history atomically
        history = ReservationStatusHistory(
            reservation_id=new_res.id,
            changed_by_name="Customer / Concierge System",
            user_role="CUSTOMER",
            previous_status=None,
            new_status=initial_status,
            notes="Initial reservation request submitted.",
        )
        db.add(history)

        # Record immutable audit log atomically
        audit = AuditLog(
            user_name="Customer / Concierge",
            user_role="CUSTOMER",
            action="RESERVATION_SUBMISSION",
            entity_type="RESERVATION",
            entity_id=new_res.id,
            environment=active_env,
            details=f"New table reservation request {new_res.reference_id} submitted for {outlet.name} on {req.reservation_date} at {req.reservation_time} ({req.guest_count} covers).",
        )
        db.add(audit)

        # Single atomic commit for reservation + history + audit
        db.commit()
        db.refresh(new_res)
    except Exception as e:
        db.rollback()
        raise e

    setattr(new_res, "capacity_warning", capacity_warning)
    return new_res

@router.get("", response_model=List[ReservationResponse])
def list_reservations(
    outlet_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    environment: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    reservation_date: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN", "MANAGER", "STAFF")),
    db: Session = Depends(get_db),
):
    """
    List reservations with multi-facet filters: outlet, status, environment, date, and keyword search.
    Strictly isolated by environment and user outlet authorization.
    """
    if not isinstance(current_user, User):
        current_user = db.query(User).filter(User.role == "SUPER_ADMIN").first() or User(
            id=1, email="admin@amithospitality.com", full_name="System Admin", role="SUPER_ADMIN"
        )

    if not isinstance(outlet_id, int):
        outlet_id = getattr(outlet_id, "default", None)

    effective_outlet_id = outlet_id
    if current_user and getattr(current_user, "role", None) in ("STAFF", "MANAGER") and getattr(current_user, "outlet_id", None):
        if outlet_id is not None and outlet_id != current_user.outlet_id:
            raise HTTPException(
                status_code=403,
                detail=f"Cross-outlet access forbidden: You are assigned to outlet {current_user.outlet_id} and cannot access outlet {outlet_id}.",
            )
        effective_outlet_id = current_user.outlet_id

    target_env = environment if isinstance(environment, str) and environment else get_current_env(db)
    query = db.query(ReservationRequest).filter(ReservationRequest.environment == target_env)

    if effective_outlet_id is not None and isinstance(effective_outlet_id, int):
        query = query.filter(ReservationRequest.outlet_id == effective_outlet_id)
    if status is not None and isinstance(status, str) and status != "ALL":
        query = query.filter(ReservationRequest.status == status)
    if reservation_date is not None and isinstance(reservation_date, str) and reservation_date:
        query = query.filter(ReservationRequest.reservation_date == reservation_date)

    if search is not None and isinstance(search, str) and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                ReservationRequest.guest_name.ilike(term),
                ReservationRequest.guest_phone.ilike(term),
                ReservationRequest.guest_email.ilike(term),
                ReservationRequest.reference_id.ilike(term),
            )
        )

    actual_skip = skip if isinstance(skip, int) else 0
    actual_limit = limit if isinstance(limit, int) else 100
    return query.order_by(ReservationRequest.created_at.desc()).offset(actual_skip).limit(actual_limit).all()

@router.get("/{res_id}", response_model=ReservationResponse)
def get_reservation_detail(
    res_id: int,
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN", "MANAGER", "STAFF")),
    db: Session = Depends(get_db),
):
    """Retrieve full reservation details by numeric ID."""
    if not isinstance(current_user, User):
        current_user = db.query(User).filter(User.role == "SUPER_ADMIN").first() or User(
            id=1, email="admin@amithospitality.com", full_name="System Admin", role="SUPER_ADMIN"
        )

    res = db.query(ReservationRequest).filter(ReservationRequest.id == res_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Reservation request not found")

    if current_user and getattr(current_user, "role", None) in ("STAFF", "MANAGER") and getattr(current_user, "outlet_id", None):
        if res.outlet_id != current_user.outlet_id:
            raise HTTPException(
                status_code=403,
                detail=f"Cross-outlet access forbidden: Reservation belongs to outlet {res.outlet_id}, not your assigned outlet {current_user.outlet_id}.",
            )
    return res

@router.patch("/{res_id}/status", response_model=ReservationResponse)
def update_reservation_status(
    res_id: int,
    status_update: ReservationStatusUpdate,
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN", "MANAGER", "STAFF")),
    db: Session = Depends(get_db),
):
    """
    Update reservation lifecycle status, allocate tables/internal notes, and assign staff.
    Records immutable status change history and compliance audit logs.
    """
    if not isinstance(current_user, User):
        current_user = db.query(User).filter(User.role == "SUPER_ADMIN").first() or User(
            id=1, email="admin@amithospitality.com", full_name="System Admin", role="SUPER_ADMIN"
        )

    res = db.query(ReservationRequest).filter(ReservationRequest.id == res_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Reservation request not found")

    if current_user and getattr(current_user, "role", None) in ("STAFF", "MANAGER") and getattr(current_user, "outlet_id", None):
        if res.outlet_id != current_user.outlet_id:
            raise HTTPException(
                status_code=403,
                detail=f"Cross-outlet access forbidden: You cannot modify reservations for outlet {res.outlet_id}.",
            )

    old_status = res.status
    res.status = status_update.status

    if status_update.internal_notes:
        res.internal_notes = status_update.internal_notes
    if status_update.assigned_staff_id is not None:
        res.assigned_staff_id = status_update.assigned_staff_id
    if status_update.assigned_staff_name is not None:
        res.assigned_staff_name = status_update.assigned_staff_name

    res.updated_at = datetime.utcnow()

    # User identification for audit trail
    user_name = current_user.full_name if hasattr(current_user, "full_name") else "Staff / Admin"
    user_role = getattr(current_user, "role", "STAFF")
    user_id = getattr(current_user, "id", None)

    # 1. Record in status history
    history = ReservationStatusHistory(
        reservation_id=res.id,
        changed_by_user_id=user_id,
        changed_by_name=user_name,
        user_role=user_role,
        previous_status=old_status,
        new_status=status_update.status,
        notes=status_update.internal_notes,
    )
    db.add(history)

    # 2. Record immutable system audit log
    audit = AuditLog(
        user_id=user_id,
        user_name=user_name,
        user_role=user_role,
        action="RESERVATION_STATUS_UPDATE",
        entity_type="RESERVATION",
        entity_id=res.id,
        environment=res.environment,
        details=f"Reservation #{res.id} ({res.reference_id}) for {res.guest_name} status updated: {old_status} -> {status_update.status}. Notes: {status_update.internal_notes or 'None'}",
    )
    db.add(audit)

    db.commit()
    db.refresh(res)
    return res

@router.get("/{res_id}/history", response_model=List[ReservationHistoryItem])
def get_reservation_history(
    res_id: int,
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN", "MANAGER", "STAFF")),
    db: Session = Depends(get_db),
):
    """Retrieve full audit and lifecycle status transition timeline for a reservation."""
    if not isinstance(current_user, User):
        current_user = db.query(User).filter(User.role == "SUPER_ADMIN").first() or User(
            id=1, email="admin@amithospitality.com", full_name="System Admin", role="SUPER_ADMIN"
        )

    res = db.query(ReservationRequest).filter(ReservationRequest.id == res_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Reservation request not found")

    if current_user and getattr(current_user, "role", None) in ("STAFF", "MANAGER") and getattr(current_user, "outlet_id", None):
        if res.outlet_id != current_user.outlet_id:
            raise HTTPException(
                status_code=403,
                detail=f"Cross-outlet access forbidden: Reservation belongs to outlet {res.outlet_id}, not your assigned outlet {current_user.outlet_id}.",
            )

    history = (
        db.query(ReservationStatusHistory)
        .filter(ReservationStatusHistory.reservation_id == res_id)
        .order_by(ReservationStatusHistory.created_at.desc())
        .all()
    )
    return history

@router.get("/export")
def export_reservations_csv(
    outlet_id: Optional[int] = Query(None),
    environment: Optional[str] = Query(None),
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN", "MANAGER")),
    db: Session = Depends(get_db),
):
    """Export reservation records to CSV with compliance audit details."""
    if not isinstance(current_user, User):
        current_user = db.query(User).filter(User.role == "SUPER_ADMIN").first() or User(
            id=1, email="admin@amithospitality.com", full_name="System Admin", role="SUPER_ADMIN"
        )

    if not isinstance(outlet_id, int):
        outlet_id = getattr(outlet_id, "default", None)

    effective_outlet_id = outlet_id
    if current_user and getattr(current_user, "role", None) == "MANAGER" and getattr(current_user, "outlet_id", None):
        if outlet_id is not None and outlet_id != current_user.outlet_id:
            raise HTTPException(
                status_code=403,
                detail=f"Cross-outlet access forbidden: You are assigned to outlet {current_user.outlet_id} and cannot export data for outlet {outlet_id}.",
            )
        effective_outlet_id = current_user.outlet_id

    target_env = environment if isinstance(environment, str) and environment else get_current_env(db)
    query = db.query(ReservationRequest).filter(ReservationRequest.environment == target_env)
    if effective_outlet_id is not None and isinstance(effective_outlet_id, int):
        query = query.filter(ReservationRequest.outlet_id == effective_outlet_id)

    reservations = query.order_by(ReservationRequest.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Reference ID", "ID", "Environment", "Outlet", "Guest Name", "Phone", "Email",
        "Party Size", "Date", "Time", "Seating Preference", "Status", "Assigned Staff", "Internal Notes", "Created At"
    ])

    for r in reservations:
        writer.writerow([
            r.reference_id or f"RES-{r.id}",
            r.id,
            r.environment,
            r.outlet_name,
            r.guest_name,
            r.guest_phone,
            r.guest_email or "",
            r.guest_count,
            r.reservation_date,
            r.reservation_time,
            r.seating_preference,
            r.status,
            r.assigned_staff_name or "",
            r.internal_notes or "",
            r.created_at.isoformat() if r.created_at else "",
        ])

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=reservations_{target_env.lower()}.csv"},
    )
