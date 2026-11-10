from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any

from app.database import get_db
from app.models.user import User
from app.models.guest import ReservationModificationRequest
from app.models.reservation import ReservationRequest
from app.models.audit import EnvironmentSetting
from app.schemas.guest import (
    GuestProfileUpdate,
    ReservationModificationReviewRequest,
)
from app.services.guest_crm_service import guest_crm_service
from app.services.reservation_lifecycle_service import reservation_lifecycle_service
from app.utils.security import require_roles

router = APIRouter(prefix="/api/v1/crm", tags=["Unified Guest CRM & Administration"])

def get_current_env(db: Session) -> str:
    setting = db.query(EnvironmentSetting).order_by(EnvironmentSetting.id.desc()).first()
    return setting.active_environment if setting else "DEMO"

@router.get("/guests")
def list_guests(
    outlet_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    vip_only: Optional[bool] = Query(None),
    dietary: Optional[str] = Query(None),
    environment: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN", "MANAGER", "STAFF")),
    db: Session = Depends(get_db),
):
    """
    Search and filter unified guest CRM profiles.
    Strictly isolated by user role and assigned outlet.
    """
    actual_outlet_id = outlet_id if isinstance(outlet_id, int) else getattr(outlet_id, "default", None)
    actual_search = search if isinstance(search, str) else getattr(search, "default", None)
    actual_vip_only = vip_only if isinstance(vip_only, bool) else getattr(vip_only, "default", None)
    actual_dietary = dietary if isinstance(dietary, str) else getattr(dietary, "default", None)
    actual_environment = environment if isinstance(environment, str) else getattr(environment, "default", None)
    actual_skip = skip if isinstance(skip, int) else 0
    actual_limit = limit if isinstance(limit, int) else 50

    target_env = actual_environment or get_current_env(db)
    guests, total = guest_crm_service.list_guests(
        db=db,
        current_user=current_user,
        environment=target_env,
        outlet_id=actual_outlet_id,
        search=actual_search,
        vip_only=actual_vip_only,
        dietary=actual_dietary,
        skip=actual_skip,
        limit=actual_limit,
    )
    return {
        "guests": guests,
        "total": total,
        "skip": actual_skip,
        "limit": actual_limit,
    }

@router.get("/guests/{guest_id}")
def get_guest_profile(
    guest_id: int,
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN", "MANAGER", "STAFF")),
    db: Session = Depends(get_db),
):
    """
    Retrieve full guest profile, dining history, special preferences, and communication audit trail.
    """
    return guest_crm_service.get_guest_detail(db=db, guest_id=guest_id, current_user=current_user)

@router.patch("/guests/{guest_id}")
def update_guest_profile(
    guest_id: int,
    req: GuestProfileUpdate,
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN", "MANAGER", "STAFF")),
    db: Session = Depends(get_db),
):
    """
    Update guest dietary preferences, food allergies, special occasions, and internal staff notes.
    Role-based checks prevent Staff from toggling VIP status.
    """
    return guest_crm_service.update_guest_profile(
        db=db,
        guest_id=guest_id,
        req=req,
        current_user=current_user,
    )

@router.get("/modification-requests")
def list_modification_requests(
    status: Optional[str] = Query(None),
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN", "MANAGER")),
    db: Session = Depends(get_db),
):
    """
    List self-service modification requests submitted by guests.
    Allows managers to review large party size changes or table reallocation requests.
    """
    actual_status = status if isinstance(status, str) else getattr(status, "default", None)
    query = db.query(ReservationModificationRequest)
    if actual_status and actual_status != "ALL":
        query = query.filter(ReservationModificationRequest.status == actual_status)

    # Scoped by user outlet
    user_role = getattr(current_user, "role", "MANAGER")
    user_outlet = getattr(current_user, "outlet_id", None)
    if user_role == "MANAGER" and user_outlet:
        res_ids = db.query(ReservationRequest.id).filter(ReservationRequest.outlet_id == user_outlet).subquery()
        query = query.filter(ReservationModificationRequest.reservation_id.in_(res_ids))

    requests = query.order_by(ReservationModificationRequest.created_at.desc()).limit(100).all()
    return [
        {
            "id": r.id,
            "reservation_id": r.reservation_id,
            "reference_id": r.reference_id,
            "requested_by": r.requested_by,
            "old_date": r.old_date,
            "new_date": r.new_date,
            "old_time": r.old_time,
            "new_time": r.new_time,
            "old_guest_count": r.old_guest_count,
            "new_guest_count": r.new_guest_count,
            "old_special_requests": r.old_special_requests,
            "new_special_requests": r.new_special_requests,
            "status": r.status,
            "review_notes": r.review_notes,
            "reviewed_by_name": r.reviewed_by_name,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in requests
    ]

@router.post("/modification-requests/{request_id}/review")
def review_modification_request(
    request_id: int,
    req: ReservationModificationReviewRequest,
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN", "MANAGER")),
    db: Session = Depends(get_db),
):
    """
    Approve or reject a pending reservation modification request.
    If approved, automatically applies changes to reservation and notifies guest.
    """
    mod = db.query(ReservationModificationRequest).filter(ReservationModificationRequest.id == request_id).first()
    if not mod:
        raise HTTPException(status_code=404, detail="Modification request not found")

    res = db.query(ReservationRequest).filter(ReservationRequest.id == mod.reservation_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Associated reservation not found")

    user_role = getattr(current_user, "role", "MANAGER")
    user_outlet = getattr(current_user, "outlet_id", None)
    if user_role == "MANAGER" and user_outlet and res.outlet_id != user_outlet:
        raise HTTPException(status_code=403, detail="Cross-outlet modification review forbidden")

    user_name = getattr(current_user, "full_name", "Manager")
    user_id = getattr(current_user, "id", None)

    if req.action == "APPROVE":
        mod.status = "APPLIED"
        mod.review_notes = req.review_notes or "Approved by restaurant manager"
        mod.reviewed_by_user_id = user_id
        mod.reviewed_by_name = user_name

        # Apply updates to reservation
        res.reservation_date = mod.new_date
        res.reservation_time = mod.new_time
        res.guest_count = mod.new_guest_count
        if mod.new_special_requests is not None:
            res.special_requests = mod.new_special_requests

        reservation_lifecycle_service.transition_status(
            db=db,
            reservation_id=res.id,
            target_status="MODIFIED",
            actor_name=user_name,
            actor_role=user_role,
            user_id=user_id,
            notes=f"Manager approved modification request #{mod.id}: {req.review_notes or 'None'}",
            notify=True,
        )
    else:
        mod.status = "REJECTED"
        mod.review_notes = req.review_notes or "Rejected by restaurant manager"
        mod.reviewed_by_user_id = user_id
        mod.reviewed_by_name = user_name

        # Revert status to ACCEPTED
        reservation_lifecycle_service.transition_status(
            db=db,
            reservation_id=res.id,
            target_status="ACCEPTED",
            actor_name=user_name,
            actor_role=user_role,
            user_id=user_id,
            notes=f"Manager rejected modification request #{mod.id}: {req.review_notes or 'None'}",
            notify=True,
        )

    db.commit()
    db.refresh(mod)
    return {
        "status": mod.status,
        "message": f"Modification request #{mod.id} has been {mod.status.lower()}.",
        "request_id": mod.id,
    }
