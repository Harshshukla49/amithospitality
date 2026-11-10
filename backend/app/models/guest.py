import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.database import Base

def generate_guest_uuid() -> str:
    return f"GST-{uuid.uuid4().hex[:10].upper()}"

class GuestProfile(Base):
    """
    Unified Guest CRM Profile for Amit Hospitality.
    Tracks guest identity, contact information, dining preferences, food allergies,
    accessibility requirements, internal staff notes, and aggregated reservation metrics.
    Strictly isolated between DEMO and REAL environments.
    """
    __tablename__ = "guest_profiles"

    id = Column(Integer, primary_key=True, index=True)
    guest_uuid = Column(String(50), unique=True, index=True, default=generate_guest_uuid, nullable=False)
    environment = Column(String(10), default="DEMO", index=True, nullable=False)  # DEMO or REAL

    full_name = Column(String(255), nullable=False, index=True)
    phone = Column(String(50), nullable=False, index=True)
    phone_normalized = Column(String(50), nullable=False, index=True)
    email = Column(String(255), nullable=True, index=True)
    email_normalized = Column(String(255), nullable=True, index=True)

    preferred_channel = Column(String(20), default="SMS")  # EMAIL, SMS, WHATSAPP, PHONE
    dietary_preferences = Column(String(100), default="NONE")  # VEG, NON_VEG, VEGAN, JAIN, HALAL, GLUTEN_FREE
    allergies = Column(Text, nullable=True)  # e.g. "Peanuts, Shellfish, Lactose"
    cuisine_preferences = Column(String(255), nullable=True)  # e.g. "Pan-Asian, Royal Awadhi"
    special_occasions = Column(String(255), nullable=True)  # e.g. "Anniversary: Oct 14"
    accessibility_requirements = Column(Text, nullable=True)  # e.g. "Wheelchair access required"

    staff_notes = Column(Text, nullable=True)
    vip_status = Column(Boolean, default=False, index=True)
    total_visits = Column(Integer, default=1)
    total_spend = Column(Float, default=0.0)
    preferred_outlet_id = Column(Integer, ForeignKey("outlets.id"), nullable=True, index=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    reservations = relationship("ReservationRequest", back_populates="guest_profile", order_by="desc(ReservationRequest.created_at)")
    preferred_outlet = relationship("Outlet")

    __table_args__ = (
        Index("ix_guest_phone_env", "phone_normalized", "environment"),
        Index("ix_guest_email_env", "email_normalized", "environment"),
    )

class GuestVerification(Base):
    """
    Expiring Single-Use OTP / Verification Token for Guest Self-Service Access.
    Stored as SHA-256 hash with attempt counters and 10-minute expiry window.
    """
    __tablename__ = "guest_verifications"

    id = Column(Integer, primary_key=True, index=True)
    reservation_id = Column(Integer, ForeignKey("reservation_requests.id", ondelete="CASCADE"), nullable=False, index=True)
    reference_id = Column(String(50), nullable=False, index=True)

    target_type = Column(String(20), nullable=False)  # "PHONE" or "EMAIL"
    target_masked = Column(String(255), nullable=False)  # Masked e.g. "+91 ******0001" or "k***@example.com"
    token_hash = Column(String(64), nullable=False)  # SHA-256 hash of the 6-digit OTP

    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=5)
    is_used = Column(Boolean, default=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class GuestAccessAudit(Base):
    """
    Immutable Audit Log for Guest Self-Service Interactions & Security Events.
    Tracks lookup attempts, OTP verification status, rate limiting blocks, and modifications.
    """
    __tablename__ = "guest_access_audits"

    id = Column(Integer, primary_key=True, index=True)
    reference_id = Column(String(50), nullable=True, index=True)
    reservation_id = Column(Integer, nullable=True, index=True)
    action = Column(String(50), nullable=False, index=True)  # LOOKUP_ATTEMPT, OTP_REQUESTED, OTP_VERIFIED, OTP_FAILED, RESERVATION_VIEWED, MODIFICATION_SUBMITTED, CANCELLATION_SUBMITTED, RATE_LIMITED
    status = Column(String(20), nullable=False)  # SUCCESS, FAILED, BLOCKED
    ip_address = Column(String(100), nullable=True)
    user_agent = Column(String(255), nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ReservationModificationRequest(Base):
    """
    Record of Self-Service Modification Requests.
    Allows automated application or staging for Manager approval if party size changes significantly.
    """
    __tablename__ = "reservation_modification_requests"

    id = Column(Integer, primary_key=True, index=True)
    reservation_id = Column(Integer, ForeignKey("reservation_requests.id", ondelete="CASCADE"), nullable=False, index=True)
    reference_id = Column(String(50), nullable=False, index=True)
    requested_by = Column(String(50), default="GUEST")  # GUEST or STAFF

    old_date = Column(String(20), nullable=False)
    new_date = Column(String(20), nullable=False)
    old_time = Column(String(20), nullable=False)
    new_time = Column(String(20), nullable=False)
    old_guest_count = Column(Integer, nullable=False)
    new_guest_count = Column(Integer, nullable=False)
    old_special_requests = Column(Text, nullable=True)
    new_special_requests = Column(Text, nullable=True)

    status = Column(String(30), default="APPLIED", index=True)  # APPLIED, PENDING_APPROVAL, REJECTED
    review_notes = Column(Text, nullable=True)
    reviewed_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_by_name = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
