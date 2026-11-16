import re
import logging
import threading
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func

from app.models.guest import GuestProfile
from app.models.reservation import ReservationRequest
from app.models.notification import NotificationLog
from app.models.audit import AuditLog
from app.models.user import User
from app.models.outlet import Outlet
from app.schemas.guest import GuestProfileUpdate
from fastapi import HTTPException

logger = logging.getLogger("guest_crm_service")

def normalize_phone(phone: Optional[str]) -> str:
    if not phone:
        return ""
    clean = phone.strip()
    # Retain leading + if present, keep only digits
    has_plus = clean.startswith("+")
    digits = re.sub(r"[^\d]", "", clean)
    return f"+{digits}" if has_plus else digits

def normalize_email(email: Optional[str]) -> Optional[str]:
    if not email:
        return None
    clean = email.strip().lower()
    return clean if "@" in clean else None

def mask_contact(contact: str, contact_type: str = "PHONE") -> str:
    """Mask sensitive contact for secure display."""
    if not contact:
        return ""
    if contact_type == "EMAIL" or "@" in contact:
        parts = contact.split("@")
        local = parts[0]
        domain = parts[1] if len(parts) > 1 else ""
        if len(local) <= 2:
            masked_local = f"{local[0]}***"
        else:
            masked_local = f"{local[0]}***{local[-1]}"
        return f"{masked_local}@{domain}"
    else:
        # Phone masking
        digits = re.sub(r"[^\d+]", "", contact)
        if len(digits) > 6:
            prefix = digits[:3]
            suffix = digits[-4:]
            return f"{prefix} ****** {suffix}"
        return f"***{digits[-3:]}" if len(digits) >= 3 else "***"

class GuestCrmService:
    """
    Unified Guest Relationship Management Service.
    Handles normalized identity resolution, cross-outlet privacy boundaries,
    guest preferences, and VIP tracking.
    """
    _resolution_lock = threading.Lock()

    @staticmethod
    def resolve_or_create_guest_profile(
        db: Session,
        full_name: str,
        phone: str,
        email: Optional[str] = None,
        outlet_id: Optional[int] = None,
        environment: str = "DEMO",
    ) -> GuestProfile:
        """
        Normalized identity matching with concurrency synchronization.
        Matches by verified phone or verified email within the active environment.
        Never merges solely on identical or similar names.
        """
        with GuestCrmService._resolution_lock:
            norm_phone = normalize_phone(phone)
            norm_email = normalize_email(email)
            clean_name = full_name.strip()

            # 1. Search for exact identity match (phone or email AND identical name)
            existing_guest = None
            if norm_phone and len(norm_phone) >= 7:
                existing_guest = (
                    db.query(GuestProfile)
                    .filter(
                        GuestProfile.environment == environment,
                        GuestProfile.phone_normalized == norm_phone,
                        func.lower(GuestProfile.full_name) == clean_name.lower(),
                    )
                    .first()
                )

            if not existing_guest and norm_email:
                existing_guest = (
                    db.query(GuestProfile)
                    .filter(
                        GuestProfile.environment == environment,
                        GuestProfile.email_normalized == norm_email,
                        func.lower(GuestProfile.full_name) == clean_name.lower(),
                    )
                    .first()
                )

            # 2. Check for shared household contact without conflating distinct individuals
            is_shared = False
            if not existing_guest:
                contact_match = None
                if norm_phone and len(norm_phone) >= 7:
                    contact_match = (
                        db.query(GuestProfile)
                        .filter(
                            GuestProfile.environment == environment,
                            GuestProfile.phone_normalized == norm_phone,
                        )
                        .first()
                    )
                if not contact_match and norm_email:
                    contact_match = (
                        db.query(GuestProfile)
                        .filter(
                            GuestProfile.environment == environment,
                            GuestProfile.email_normalized == norm_email,
                        )
                        .first()
                    )

                if contact_match:
                    # Shared family or assistant contact: mark shared flag and create isolated profile
                    is_shared = True
                    contact_match.is_shared_contact = True
                    db.flush()

            if existing_guest:
                # Increment cumulative CRM visits counter on repeat reservation
                existing_guest.total_visits = (existing_guest.total_visits or 0) + 1
                if norm_email and not existing_guest.email:
                    existing_guest.email = email.strip()
                    existing_guest.email_normalized = norm_email
                if outlet_id and not existing_guest.preferred_outlet_id:
                    existing_guest.preferred_outlet_id = outlet_id
                existing_guest.updated_at = datetime.utcnow()
                db.commit()
                db.refresh(existing_guest)
                return existing_guest

            # 3. Create new normalized guest profile
            new_guest = GuestProfile(
                environment=environment,
                full_name=clean_name,
                phone=phone.strip(),
                phone_normalized=norm_phone,
                email=email.strip() if email else None,
                email_normalized=norm_email,
                preferred_outlet_id=outlet_id,
                total_visits=1,
                total_spend=0.0,
                currency="INR",
                is_shared_contact=is_shared,
                vip_status=False,
                dietary_preferences="NONE",
            )
            db.add(new_guest)
            db.commit()
            db.refresh(new_guest)
            return new_guest

    @staticmethod
    def recompute_guest_metrics(db: Session, guest_profile_id: int) -> Dict[str, Any]:
        """
        Data and financial integrity: accurately calculate completed dining visits
        and verified paid spend. Distinguishes completed visits from unverified booking requests.
        """
        guest = db.query(GuestProfile).filter(GuestProfile.id == guest_profile_id).first()
        if not guest:
            return {"total_visits": 0, "completed_visits": 0, "total_spend": 0.0, "currency": "INR"}

        completed_count = (
            db.query(ReservationRequest)
            .filter(
                ReservationRequest.guest_profile_id == guest.id,
                ReservationRequest.status == "COMPLETED",
            )
            .count()
        )
        return {
            "total_visits": guest.total_visits or 0,
            "completed_visits": completed_count,
            "total_spend": round(guest.total_spend or 0.0, 2),
            "currency": guest.currency or "INR",
        }

    @staticmethod
    def list_guests(
        db: Session,
        current_user: User,
        environment: str = "DEMO",
        outlet_id: Optional[int] = None,
        search: Optional[str] = None,
        vip_only: Optional[bool] = None,
        dietary: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        List guest profiles with role-based outlet scoping.
        Managers and Staff only view guests associated with their assigned outlet.
        """
        user_role = getattr(current_user, "role", "STAFF")
        user_outlet = getattr(current_user, "outlet_id", None)

        query = db.query(GuestProfile).filter(GuestProfile.environment == environment)

        # Multi-outlet tenant isolation
        if user_role in ("MANAGER", "STAFF") and user_outlet:
            # Match guests preferred for this outlet or with reservations at this outlet
            guest_ids_subquery = (
                db.query(ReservationRequest.guest_profile_id)
                .filter(ReservationRequest.outlet_id == user_outlet)
                .distinct()
            )
            query = query.filter(
                or_(
                    GuestProfile.preferred_outlet_id == user_outlet,
                    GuestProfile.id.in_(guest_ids_subquery),
                )
            )
        elif outlet_id:
            guest_ids_subquery = (
                db.query(ReservationRequest.guest_profile_id)
                .filter(ReservationRequest.outlet_id == outlet_id)
                .distinct()
            )
            query = query.filter(
                or_(
                    GuestProfile.preferred_outlet_id == outlet_id,
                    GuestProfile.id.in_(guest_ids_subquery),
                )
            )

        if vip_only:
            query = query.filter(GuestProfile.vip_status == True)

        if dietary and dietary != "ALL":
            query = query.filter(GuestProfile.dietary_preferences == dietary)

        if search and search.strip():
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    GuestProfile.full_name.ilike(term),
                    GuestProfile.phone.ilike(term),
                    GuestProfile.email.ilike(term),
                    GuestProfile.guest_uuid.ilike(term),
                )
            )

        total_count = query.count()
        guests = query.order_by(GuestProfile.updated_at.desc()).offset(skip).limit(limit).all()

        results = []
        for g in guests:
            outlet_name = g.preferred_outlet.name if g.preferred_outlet else None
            # Staff role cannot view detailed spend
            spend = g.total_spend if user_role in ("SUPER_ADMIN", "ADMIN", "MANAGER") else None
            results.append({
                "id": g.id,
                "guest_uuid": g.guest_uuid,
                "environment": g.environment,
                "full_name": g.full_name,
                "phone": g.phone,
                "email": g.email,
                "preferred_channel": g.preferred_channel or "SMS",
                "dietary_preferences": g.dietary_preferences or "NONE",
                "allergies": g.allergies,
                "cuisine_preferences": g.cuisine_preferences,
                "special_occasions": g.special_occasions,
                "accessibility_requirements": g.accessibility_requirements,
                "staff_notes": g.staff_notes,
                "vip_status": g.vip_status,
                "total_visits": g.total_visits or 0,
                "total_spend": round(spend, 2) if spend is not None else None,
                "currency": g.currency or "INR",
                "is_shared_contact": bool(g.is_shared_contact),
                "preferred_outlet_id": g.preferred_outlet_id,
                "preferred_outlet_name": outlet_name,
                "created_at": g.created_at,
                "updated_at": g.updated_at,
            })
        return results, total_count

    @staticmethod
    def get_guest_detail(db: Session, guest_id: int, current_user: User) -> Dict[str, Any]:
        """
        Retrieve complete guest profile, linked reservations, and outbound notifications.
        Enforces outlet isolation for Manager and Staff roles.
        """
        user_role = getattr(current_user, "role", "STAFF")
        user_outlet = getattr(current_user, "outlet_id", None)

        guest = db.query(GuestProfile).filter(GuestProfile.id == guest_id).first()
        if not guest:
            raise HTTPException(status_code=404, detail="Guest profile not found")

        # Tenant isolation check
        if user_role in ("MANAGER", "STAFF") and user_outlet:
            has_outlet_booking = (
                db.query(ReservationRequest)
                .filter(
                    ReservationRequest.guest_profile_id == guest.id,
                    ReservationRequest.outlet_id == user_outlet,
                )
                .first()
            )
            if guest.preferred_outlet_id != user_outlet and not has_outlet_booking:
                raise HTTPException(
                    status_code=403,
                    detail=f"Cross-outlet access forbidden: Guest is not associated with outlet {user_outlet}.",
                )

        # Linked reservations
        res_query = (
            db.query(ReservationRequest)
            .filter(ReservationRequest.guest_profile_id == guest.id)
            .order_by(ReservationRequest.created_at.desc())
        )
        if user_role in ("MANAGER", "STAFF") and user_outlet:
            res_query = res_query.filter(ReservationRequest.outlet_id == user_outlet)

        reservations_data = [
            {
                "id": r.id,
                "reference_id": r.reference_id,
                "outlet_name": r.outlet_name,
                "outlet_id": r.outlet_id,
                "reservation_date": r.reservation_date,
                "reservation_time": r.reservation_time,
                "guest_count": r.guest_count,
                "status": r.status,
                "seating_preference": r.seating_preference,
                "special_requests": r.special_requests,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in res_query.all()
        ]

        # Communication / Notification history
        comm_query = db.query(NotificationLog).filter(
            or_(
                NotificationLog.recipient == guest.email,
                NotificationLog.recipient == guest.phone,
            )
        ).order_by(NotificationLog.created_at.desc())

        if user_role in ("MANAGER", "STAFF") and user_outlet:
            comm_query = comm_query.filter(NotificationLog.outlet_id == user_outlet)

        comm_logs = [
            {
                "id": c.id,
                "channel": c.channel,
                "event_type": c.event_type,
                "status": c.status,
                "recipient": c.recipient,
                "reference_id": c.reference_id,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in comm_query.limit(50).all()
        ]

        outlet_name = guest.preferred_outlet.name if guest.preferred_outlet else None
        spend = guest.total_spend if user_role in ("SUPER_ADMIN", "ADMIN", "MANAGER") else None

        return {
            "id": guest.id,
            "guest_uuid": guest.guest_uuid,
            "environment": guest.environment,
            "full_name": guest.full_name,
            "phone": guest.phone,
            "email": guest.email,
            "preferred_channel": guest.preferred_channel or "SMS",
            "dietary_preferences": guest.dietary_preferences or "NONE",
            "allergies": guest.allergies,
            "cuisine_preferences": guest.cuisine_preferences,
            "special_occasions": guest.special_occasions,
            "accessibility_requirements": guest.accessibility_requirements,
            "staff_notes": guest.staff_notes,
            "vip_status": guest.vip_status,
            "total_visits": guest.total_visits or 0,
            "total_spend": round(spend, 2) if spend is not None else None,
            "currency": guest.currency or "INR",
            "is_shared_contact": bool(guest.is_shared_contact),
            "preferred_outlet_id": guest.preferred_outlet_id,
            "preferred_outlet_name": outlet_name,
            "created_at": guest.created_at,
            "updated_at": guest.updated_at,
            "reservations": reservations_data,
            "communication_logs": comm_logs,
        }

    @staticmethod
    def update_guest_profile(
        db: Session,
        guest_id: int,
        req: GuestProfileUpdate,
        current_user: User,
    ) -> Dict[str, Any]:
        """Update guest profile preferences, dietary flags, and staff notes."""
        user_role = getattr(current_user, "role", "STAFF")
        user_outlet = getattr(current_user, "outlet_id", None)

        guest = db.query(GuestProfile).filter(GuestProfile.id == guest_id).first()
        if not guest:
            raise HTTPException(status_code=404, detail="Guest profile not found")

        # Isolation check
        if user_role in ("MANAGER", "STAFF") and user_outlet:
            has_outlet_booking = (
                db.query(ReservationRequest)
                .filter(
                    ReservationRequest.guest_profile_id == guest.id,
                    ReservationRequest.outlet_id == user_outlet,
                )
                .first()
            )
            if guest.preferred_outlet_id != user_outlet and not has_outlet_booking:
                raise HTTPException(status_code=403, detail="Cross-outlet guest modification forbidden")

        # RBAC: Staff cannot update VIP status
        if req.vip_status is not None and user_role == "STAFF":
            raise HTTPException(status_code=403, detail="Staff role is not authorized to modify VIP designation.")

        # Apply updates
        if req.full_name:
            guest.full_name = req.full_name.strip()
        if req.dietary_preferences is not None:
            guest.dietary_preferences = req.dietary_preferences
        if req.allergies is not None:
            guest.allergies = req.allergies
        if req.cuisine_preferences is not None:
            guest.cuisine_preferences = req.cuisine_preferences
        if req.special_occasions is not None:
            guest.special_occasions = req.special_occasions
        if req.accessibility_requirements is not None:
            guest.accessibility_requirements = req.accessibility_requirements
        if req.preferred_channel is not None:
            guest.preferred_channel = req.preferred_channel
        if req.staff_notes is not None:
            guest.staff_notes = req.staff_notes
        if req.vip_status is not None:
            guest.vip_status = req.vip_status
        if req.preferred_outlet_id is not None:
            guest.preferred_outlet_id = req.preferred_outlet_id

        guest.updated_at = datetime.utcnow()

        # Audit log
        user_name = getattr(current_user, "full_name", "Staff User")
        audit = AuditLog(
            user_id=getattr(current_user, "id", None),
            user_name=user_name,
            user_role=user_role,
            action="GUEST_PROFILE_UPDATED",
            entity_type="GUEST",
            entity_id=guest.id,
            environment=guest.environment,
            details=f"Guest profile #{guest.id} ({guest.full_name}) preferences updated by {user_name} ({user_role}).",
        )
        db.add(audit)
        db.commit()
        db.refresh(guest)

        return GuestCrmService.get_guest_detail(db, guest.id, current_user)

guest_crm_service = GuestCrmService()
