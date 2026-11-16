import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.reservation import ReservationRequest, ReservationStatusHistory
from app.models.audit import AuditLog
from app.services.notification_service import notification_service

logger = logging.getLogger("reservation_lifecycle_service")

# Explicit state transition map for luxury hospitality operations
# Enforces non-arbitrary transitions and protects terminal states
ALLOWED_TRANSITIONS: Dict[str, List[str]] = {
    "NEW": ["ACCEPTED", "CONFIRMED", "UNDER_REVIEW", "REJECTED", "CANCELLED", "MODIFIED"],
    "UNDER_REVIEW": ["NEW", "ACCEPTED", "CONFIRMED", "REJECTED", "CANCELLED", "MODIFIED"],
    "ACCEPTED": ["MODIFIED", "COMPLETED", "CANCELLED", "NO_SHOW", "UNDER_REVIEW"],
    "CONFIRMED": ["MODIFIED", "COMPLETED", "CANCELLED", "NO_SHOW", "UNDER_REVIEW"],
    "MODIFIED": ["ACCEPTED", "CONFIRMED", "COMPLETED", "CANCELLED", "NO_SHOW", "UNDER_REVIEW"],
    "COMPLETED": [],     # Terminal state
    "CANCELLED": [],     # Terminal state
    "REJECTED": [],      # Terminal state
    "NO_SHOW": [],       # Terminal state
}

class ReservationLifecycleService:
    """
    Hospitality Reservation Lifecycle State Machine & Audit Compliance Service.
    Enforces atomic state transitions, preserves audit logs, and coordinates notifications.
    """

    @staticmethod
    def is_valid_transition(current_status: str, target_status: str) -> bool:
        curr = (current_status or "NEW").upper()
        target = target_status.upper()
        if curr == target:
            return True  # Idempotent re-affirmation allowed
        allowed = ALLOWED_TRANSITIONS.get(curr, [])
        return target in allowed

    @staticmethod
    def transition_status(
        db: Session,
        reservation_id: int,
        target_status: str,
        actor_name: str,
        actor_role: str,
        user_id: Optional[int] = None,
        notes: Optional[str] = None,
        notify: bool = True,
    ) -> ReservationRequest:
        """
        Atomically transition reservation lifecycle state with validation,
        status history recording, and compliance audit trail.
        """
        res = db.query(ReservationRequest).filter(ReservationRequest.id == reservation_id).first()
        if not res:
            raise HTTPException(status_code=404, detail="Reservation request not found")

        curr_status = (res.status or "NEW").upper()
        next_status = target_status.upper()

        if not ReservationLifecycleService.is_valid_transition(curr_status, next_status):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid reservation lifecycle transition: Cannot change status from '{curr_status}' to '{next_status}'. "
                       f"Permitted transitions from '{curr_status}': {ALLOWED_TRANSITIONS.get(curr_status, []) or 'None (Terminal State)'}."
            )

        old_status = res.status
        res.status = next_status
        if notes:
            res.internal_notes = f"{res.internal_notes or ''} | {notes}".strip(" |")
        res.updated_at = datetime.utcnow()

        # 1. Record immutable status history entry
        history_entry = ReservationStatusHistory(
            reservation_id=res.id,
            changed_by_user_id=user_id,
            changed_by_name=actor_name,
            user_role=actor_role,
            previous_status=old_status,
            new_status=next_status,
            notes=notes or f"Transitioned from {old_status} to {next_status}",
        )
        db.add(history_entry)

        # 2. Record immutable system audit log
        audit = AuditLog(
            user_id=user_id,
            user_name=actor_name,
            user_role=actor_role,
            action="RESERVATION_LIFECYCLE_TRANSITION",
            entity_type="RESERVATION",
            entity_id=res.id,
            environment=res.environment,
            details=f"Reservation #{res.id} ({res.reference_id}) status transitioned: {old_status} -> {next_status} by {actor_name} ({actor_role}). Notes: {notes or 'None'}",
        )
        db.add(audit)

        db.commit()
        db.refresh(res)

        # 3. Recompute guest metrics if transitioning to or from COMPLETED
        if (next_status == "COMPLETED" or old_status == "COMPLETED") and res.guest_profile_id:
            try:
                from app.services.guest_crm_service import guest_crm_service
                guest_crm_service.recompute_guest_metrics(db, res.guest_profile_id)
            except Exception as ex:
                logger.warning(f"Notice recomputing guest metrics: {ex}")

        # 4. Notification dispatch
        if notify:
            payload = {
                "reservation_id": res.id,
                "reference_id": res.reference_id,
                "guest_name": res.guest_name,
                "guest_email": res.guest_email,
                "guest_phone": res.guest_phone,
                "outlet_name": res.outlet_name,
                "date_str": res.reservation_date,
                "time_str": res.reservation_time,
                "guest_count": res.guest_count,
                "status": res.status,
                "environment": res.environment,
                "notes": notes,
                "outlet_id": res.outlet_id,
            }
            try:
                notification_service.notify_reservation_lifecycle(**payload)
            except Exception as ex:
                logger.warning(f"Notification error on lifecycle transition: {ex}")

        return res

reservation_lifecycle_service = ReservationLifecycleService()
