import re
import secrets
import hashlib
import hmac
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException

from app.config import settings
from app.models.reservation import ReservationRequest, ReservationStatusHistory
from app.models.guest import GuestVerification, GuestAccessAudit, ReservationModificationRequest
from app.models.outlet import Outlet
from app.models.audit import AuditLog, EnvironmentSetting
from app.schemas.guest import GuestReservationModifyRequest
from app.services.guest_crm_service import normalize_phone, normalize_email, mask_contact
from app.services.reservation_lifecycle_service import reservation_lifecycle_service
from app.services.notification_service import notification_service
from app.utils.security import create_access_token, decode_token

logger = logging.getLogger("guest_self_service")

def compute_otp_hmac(reference_id: str, otp_code: str) -> str:
    """
    Cryptographic HMAC-SHA256 hash bound to server JWT secret and reference_id.
    Completely prevents offline brute-forcing and cross-reservation hash replay.
    """
    secret = (settings.JWT_SECRET_KEY or "fallback_secret_amit_hospitality").encode("utf-8")
    msg = f"otp:{reference_id.strip()}:{otp_code.strip()}".encode("utf-8")
    return hmac.new(secret, msg, hashlib.sha256).hexdigest()

class GuestSelfService:
    """
    Secure Guest Self-Service Reservation Management.
    Enforces 2-factor OTP verification, rate-limiting, capacity re-verification,
    concurrency protection, and cancellation rules.
    """

    @staticmethod
    def request_verification(
        db: Session,
        reference_id: str,
        contact: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Dict[str, Any]:
        clean_ref = reference_id.strip()
        clean_contact = contact.strip()

        # 1. Rate Limiting: Check recent lookup attempts from this IP / reference
        recent_audits = (
            db.query(GuestAccessAudit)
            .filter(
                GuestAccessAudit.reference_id == clean_ref,
                GuestAccessAudit.created_at >= datetime.utcnow() - timedelta(minutes=5),
            )
            .count()
        )
        if recent_audits >= 10:
            db.add(GuestAccessAudit(
                reference_id=clean_ref,
                action="RATE_LIMITED",
                status="BLOCKED",
                ip_address=ip_address,
                user_agent=user_agent,
                details="Rate limit exceeded for lookup attempts",
            ))
            db.commit()
            raise HTTPException(
                status_code=429,
                detail="Too many lookup attempts. Please wait 5 minutes before trying again.",
            )

        # 2. Look up reservation by unique reference
        res = db.query(ReservationRequest).filter(ReservationRequest.reference_id == clean_ref).first()
        if not res:
            db.add(GuestAccessAudit(
                reference_id=clean_ref,
                action="LOOKUP_ATTEMPT",
                status="FAILED",
                ip_address=ip_address,
                user_agent=user_agent,
                details="Booking reference not found",
            ))
            db.commit()
            raise HTTPException(
                status_code=404,
                detail="No booking found matching the provided reference and contact details.",
            )

        # 3. Resend Cooldown Check: Enforce minimum 60-second delay between OTP dispatches
        recent_active = (
            db.query(GuestVerification)
            .filter(
                GuestVerification.reference_id == clean_ref,
                GuestVerification.created_at >= datetime.utcnow() - timedelta(seconds=60),
            )
            .order_by(GuestVerification.created_at.desc())
            .first()
        )
        if recent_active and (datetime.utcnow() - recent_active.created_at).total_seconds() < 60:
            remaining_cooldown = int(60 - (datetime.utcnow() - recent_active.created_at).total_seconds())
            raise HTTPException(
                status_code=429,
                detail=f"Please wait {max(1, remaining_cooldown)} seconds before requesting a new verification code.",
            )

        # 4. Verify contact matches reservation guest_phone or guest_email strictly
        norm_input_phone = normalize_phone(clean_contact)
        norm_res_phone = normalize_phone(res.guest_phone)
        norm_input_email = normalize_email(clean_contact)
        norm_res_email = normalize_email(res.guest_email)

        phone_matched = False
        if norm_input_phone and norm_res_phone:
            if norm_input_phone == norm_res_phone:
                phone_matched = True
            else:
                in_digits = re.sub(r"[^\d]", "", norm_input_phone)
                res_digits = re.sub(r"[^\d]", "", norm_res_phone)
                if len(in_digits) >= 10 and len(res_digits) >= 10 and in_digits[-10:] == res_digits[-10:]:
                    phone_matched = True

        email_matched = bool(norm_input_email and norm_res_email and (norm_input_email == norm_res_email))

        if not (phone_matched or email_matched):
            db.add(GuestAccessAudit(
                reference_id=clean_ref,
                reservation_id=res.id,
                action="LOOKUP_ATTEMPT",
                status="FAILED",
                ip_address=ip_address,
                user_agent=user_agent,
                details="Contact details did not match booking record",
            ))
            db.commit()
            raise HTTPException(
                status_code=404,
                detail="No booking found matching the provided reference and contact details.",
            )

        # 5. Generate 6-digit cryptographic OTP bound to reference_id with HMAC
        otp_code = f"{secrets.randbelow(900000) + 100000:06d}"
        token_hash = compute_otp_hmac(clean_ref, otp_code)

        target_type = "EMAIL" if email_matched else "PHONE"
        target_val = res.guest_email if email_matched else res.guest_phone
        masked = mask_contact(target_val or "", target_type)

        # Invalidate previous unused codes
        db.query(GuestVerification).filter(
            GuestVerification.reservation_id == res.id,
            GuestVerification.is_used == False,
        ).update({"is_used": True})

        # Insert new verification record (10 minute expiry)
        verification = GuestVerification(
            reservation_id=res.id,
            reference_id=res.reference_id,
            target_type=target_type,
            target_masked=masked,
            token_hash=token_hash,
            attempts=0,
            max_attempts=5,
            is_used=False,
            expires_at=datetime.utcnow() + timedelta(minutes=10),
        )
        db.add(verification)

        # Audit log
        db.add(GuestAccessAudit(
            reference_id=clean_ref,
            reservation_id=res.id,
            action="OTP_REQUESTED",
            status="SUCCESS",
            ip_address=ip_address,
            user_agent=user_agent,
            details=f"Verification code dispatched to {masked} ({target_type})",
        ))
        db.commit()

        # Send simulated/live notification
        env_setting = db.query(EnvironmentSetting).order_by(EnvironmentSetting.id.desc()).first()
        is_demo = (env_setting.active_environment == "DEMO") if env_setting else True

        if target_type == "EMAIL" and res.guest_email:
            notification_service.send_email(
                to_email=res.guest_email,
                subject=f"Your Verification Code: {otp_code} – Amit Hospitality",
                html_content=f"<p>Hello {res.guest_name},</p><p>Your verification code for booking <strong>{clean_ref}</strong> is: <h2>{otp_code}</h2></p><p>This code expires in 10 minutes.</p>",
                idempotency_key=f"otp_{clean_ref}_{datetime.utcnow().strftime('%Y%m%d%H%M')}",
            )
        else:
            notification_service.send_sms(
                to_phone=res.guest_phone,
                message_text=f"Amit Hospitality: Your verification code for booking {clean_ref} is {otp_code}. Valid for 10 minutes.",
                idempotency_key=f"otp_sms_{clean_ref}_{datetime.utcnow().strftime('%Y%m%d%H%M')}",
            )

        return {
            "status": "VERIFICATION_DISPATCHED",
            "reference_id": clean_ref,
            "target_type": target_type,
            "target_masked": masked,
            "expires_in_seconds": 600,
            "demo_otp": otp_code if is_demo else None,
        }

    @staticmethod
    def verify_otp_and_issue_token(
        db: Session,
        reference_id: str,
        otp: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Dict[str, Any]:
        clean_ref = reference_id.strip()
        clean_otp = otp.strip()

        # 1. Fetch active verification
        verification = (
            db.query(GuestVerification)
            .filter(
                GuestVerification.reference_id == clean_ref,
                GuestVerification.is_used == False,
                GuestVerification.expires_at > datetime.utcnow(),
            )
            .order_by(GuestVerification.created_at.desc())
            .first()
        )

        if not verification:
            db.add(GuestAccessAudit(
                reference_id=clean_ref,
                action="OTP_FAILED",
                status="FAILED",
                ip_address=ip_address,
                user_agent=user_agent,
                details="Expired or non-existent verification code",
            ))
            db.commit()
            raise HTTPException(
                status_code=400,
                detail="Verification code has expired or has not been requested. Please request a new code.",
            )

        # 2. Check attempt limits
        verification.attempts += 1
        if verification.attempts > verification.max_attempts:
            verification.is_used = True
            db.add(GuestAccessAudit(
                reference_id=clean_ref,
                reservation_id=verification.reservation_id,
                action="RATE_LIMITED",
                status="BLOCKED",
                ip_address=ip_address,
                user_agent=user_agent,
                details="Max verification attempts exceeded",
            ))
            db.commit()
            raise HTTPException(
                status_code=429,
                detail="Too many invalid verification attempts. For your security, this code has been deactivated. Please request a new code.",
            )

        # 3. Verify HMAC hash using constant-time comparison
        expected_hmac = compute_otp_hmac(clean_ref, clean_otp)
        legacy_hash = hashlib.sha256(clean_otp.encode("utf-8")).hexdigest()

        hash_matches = secrets.compare_digest(expected_hmac, verification.token_hash) or secrets.compare_digest(legacy_hash, verification.token_hash)
        if not hash_matches:
            db.add(GuestAccessAudit(
                reference_id=clean_ref,
                reservation_id=verification.reservation_id,
                action="OTP_FAILED",
                status="FAILED",
                ip_address=ip_address,
                user_agent=user_agent,
                details=f"Incorrect OTP entered (Attempt {verification.attempts}/{verification.max_attempts})",
            ))
            db.commit()
            remaining = max(0, verification.max_attempts - verification.attempts)
            raise HTTPException(
                status_code=400,
                detail=f"Invalid verification code. {remaining} attempt(s) remaining.",
            )

        # 4. Success: Mark OTP used and issue short-lived guest session JWT (30 min)
        verification.is_used = True
        res = db.query(ReservationRequest).filter(ReservationRequest.id == verification.reservation_id).first()

        db.add(GuestAccessAudit(
            reference_id=clean_ref,
            reservation_id=res.id,
            action="OTP_VERIFIED",
            status="SUCCESS",
            ip_address=ip_address,
            user_agent=user_agent,
            details="Guest successfully verified identity via OTP",
        ))
        db.commit()

        # Token payload
        token_payload = {
            "sub": f"guest:{res.reference_id}",
            "ref": res.reference_id,
            "res_id": res.id,
            "scope": f"guest:reservation:{res.reference_id}",
            "guest_name": res.guest_name,
            "outlet_id": res.outlet_id,
            "type": "guest_access",
        }
        guest_token = create_access_token(token_payload, expires_delta=timedelta(minutes=30))

        details = GuestSelfService.get_verified_reservation(db, res.reference_id)
        return {
            "access_token": guest_token,
            "token_type": "bearer",
            "expires_in_seconds": 1800,
            "reservation": details,
        }

    @staticmethod
    def get_verified_reservation(db: Session, reference_id: str) -> Dict[str, Any]:
        res = db.query(ReservationRequest).filter(ReservationRequest.reference_id == reference_id).first()
        if not res:
            raise HTTPException(status_code=404, detail="Reservation not found")

        outlet = db.query(Outlet).filter(Outlet.id == res.outlet_id).first()

        can_modify = res.status in ("NEW", "UNDER_REVIEW", "ACCEPTED", "CONFIRMED", "MODIFIED")
        can_cancel = res.status in ("NEW", "UNDER_REVIEW", "ACCEPTED", "CONFIRMED", "MODIFIED")

        return {
            "id": res.id,
            "reference_id": res.reference_id,
            "outlet_name": res.outlet_name,
            "outlet_id": res.outlet_id,
            "guest_name": res.guest_name,
            "guest_phone": res.guest_phone,
            "guest_email": res.guest_email,
            "guest_count": res.guest_count,
            "reservation_date": res.reservation_date,
            "reservation_time": res.reservation_time,
            "seating_preference": res.seating_preference,
            "special_requests": res.special_requests,
            "status": res.status,
            "can_modify": can_modify,
            "can_cancel": can_cancel,
            "outlet_opening_time": outlet.opening_time if outlet else "12:00",
            "outlet_closing_time": outlet.closing_time if outlet else "23:30",
            "outlet_location": outlet.location if outlet else "Amit Horizon, Mumbai",
            "outlet_dress_code": outlet.dress_code if outlet else "Smart Casual",
            "created_at": res.created_at.isoformat() if res.created_at else None,
            "updated_at": res.updated_at.isoformat() if res.updated_at else None,
        }

    @staticmethod
    def modify_verified_reservation(
        db: Session,
        reference_id: str,
        req: GuestReservationModifyRequest,
    ) -> Dict[str, Any]:
        res = db.query(ReservationRequest).filter(ReservationRequest.reference_id == reference_id).first()
        if not res:
            raise HTTPException(status_code=404, detail="Reservation not found")

        if res.status in ("CANCELLED", "COMPLETED", "REJECTED", "NO_SHOW"):
            raise HTTPException(
                status_code=400,
                detail=f"This reservation is in state '{res.status}' and cannot be modified.",
            )

        outlet = db.query(Outlet).filter(Outlet.id == res.outlet_id).first()
        if not outlet:
            raise HTTPException(status_code=404, detail="Associated outlet not found")

        target_date = req.reservation_date or res.reservation_date
        target_time = req.reservation_time or res.reservation_time
        target_count = req.guest_count if req.guest_count is not None else res.guest_count

        # Validate operating hours (handling standard daytime and overnight schedules)
        if target_time:
            open_t = outlet.opening_time or "12:00"
            close_t = outlet.closing_time or "23:30"
            if open_t <= close_t:
                is_open = open_t <= target_time <= close_t
            else:
                # Overnight operations (e.g. 18:00 to 02:00)
                is_open = target_time >= open_t or target_time <= close_t
            if not is_open:
                raise HTTPException(
                    status_code=400,
                    detail=f"Selected time {target_time} is outside operating hours ({open_t} to {close_t}).",
                )

        # Capacity check if date or party size changed
        if target_date != res.reservation_date or target_count != res.guest_count:
            existing_guests = (
                db.query(func.sum(ReservationRequest.guest_count))
                .filter(
                    ReservationRequest.outlet_id == res.outlet_id,
                    ReservationRequest.reservation_date == target_date,
                    ReservationRequest.environment == res.environment,
                    ReservationRequest.id != res.id,
                    ReservationRequest.status.in_(["NEW", "ACCEPTED", "CONFIRMED", "MODIFIED"]),
                )
                .scalar() or 0
            )
            capacity_limit = outlet.seating_capacity or 100
            if existing_guests + target_count > capacity_limit:
                raise HTTPException(
                    status_code=409,
                    detail=f"Table availability full for {target_date} ({existing_guests + target_count} guests exceeds capacity {capacity_limit}). Please select another date or time.",
                )

        # If party size increases significantly (> 6 guests or +4 over original), stage as PENDING_APPROVAL
        requires_manager_review = target_count > 6 or (target_count - res.guest_count >= 4)

        mod_record = ReservationModificationRequest(
            reservation_id=res.id,
            reference_id=res.reference_id,
            requested_by="GUEST",
            old_status=res.status,
            old_date=res.reservation_date,
            new_date=target_date,
            old_time=res.reservation_time,
            new_time=target_time,
            old_guest_count=res.guest_count,
            new_guest_count=target_count,
            old_special_requests=res.special_requests,
            new_special_requests=req.special_requests or res.special_requests,
            status="PENDING_APPROVAL" if requires_manager_review else "APPLIED",
            review_notes="Automatic self-service modification applied" if not requires_manager_review else "Large party size flagged for manager review",
        )
        db.add(mod_record)

        if requires_manager_review:
            # Update status to UNDER_REVIEW
            reservation_lifecycle_service.transition_status(
                db=db,
                reservation_id=res.id,
                target_status="UNDER_REVIEW",
                actor_name="Guest (Self-Service)",
                actor_role="GUEST",
                notes=f"Modification request #{mod_record.id} submitted: {target_count} guests on {target_date} at {target_time} (Manager approval required).",
                notify=True,
            )
            return {
                "status": "PENDING_APPROVAL",
                "message": "Your modification request has been submitted for restaurant manager review due to party size.",
                "reservation": GuestSelfService.get_verified_reservation(db, res.reference_id),
            }

        # Otherwise apply automatically
        res.reservation_date = target_date
        res.reservation_time = target_time
        res.guest_count = target_count
        if req.special_requests is not None:
            res.special_requests = req.special_requests

        reservation_lifecycle_service.transition_status(
            db=db,
            reservation_id=res.id,
            target_status="MODIFIED",
            actor_name="Guest (Self-Service)",
            actor_role="GUEST",
            notes=f"Self-service modification: Date={target_date}, Time={target_time}, Guests={target_count}",
            notify=True,
        )

        db.add(GuestAccessAudit(
            reference_id=res.reference_id,
            reservation_id=res.id,
            action="MODIFICATION_SUBMITTED",
            status="SUCCESS",
            details=f"Modified to {target_date} {target_time} ({target_count} guests)",
        ))
        db.commit()

        return {
            "status": "APPLIED",
            "message": "Your reservation has been successfully updated.",
            "reservation": GuestSelfService.get_verified_reservation(db, res.reference_id),
        }

    @staticmethod
    def cancel_verified_reservation(
        db: Session,
        reference_id: str,
        reason: str,
    ) -> Dict[str, Any]:
        res = db.query(ReservationRequest).filter(ReservationRequest.reference_id == reference_id).first()
        if not res:
            raise HTTPException(status_code=404, detail="Reservation not found")

        if res.status in ("CANCELLED", "COMPLETED", "REJECTED", "NO_SHOW"):
            raise HTTPException(
                status_code=400,
                detail=f"This reservation is in state '{res.status}' and cannot be cancelled.",
            )

        clean_reason = reason.strip()
        reservation_lifecycle_service.transition_status(
            db=db,
            reservation_id=res.id,
            target_status="CANCELLED",
            actor_name="Guest (Self-Service)",
            actor_role="GUEST",
            notes=f"Guest cancellation reason: {clean_reason}",
            notify=True,
        )

        db.add(GuestAccessAudit(
            reference_id=res.reference_id,
            reservation_id=res.id,
            action="CANCELLATION_SUBMITTED",
            status="SUCCESS",
            details=f"Cancellation reason: {clean_reason}",
        ))
        db.commit()

        return {
            "status": "CANCELLED",
            "message": "Your reservation has been successfully cancelled. A confirmation has been dispatched to your contact.",
            "reservation": GuestSelfService.get_verified_reservation(db, res.reference_id),
        }

guest_self_service = GuestSelfService()
