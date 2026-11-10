import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

def generate_reservation_ref() -> str:
    today_str = datetime.utcnow().strftime("%Y%m%d")
    short_suffix = uuid.uuid4().hex[:6].upper()
    return f"REF-RES-{today_str}-{short_suffix}"

class ReservationRequest(Base):
    __tablename__ = "reservation_requests"

    id = Column(Integer, primary_key=True, index=True)
    reference_id = Column(String(50), unique=True, index=True, default=generate_reservation_ref)
    environment = Column(String(10), default="DEMO", index=True, nullable=False)  # DEMO or REAL
    outlet_id = Column(Integer, ForeignKey("outlets.id"), nullable=False, index=True)
    outlet_name = Column(String(255), nullable=False)
    guest_name = Column(String(255), nullable=False)
    guest_phone = Column(String(50), nullable=False)
    guest_email = Column(String(255), nullable=True)
    guest_count = Column(Integer, default=2)
    reservation_date = Column(String(20), nullable=False)
    reservation_time = Column(String(20), nullable=False)
    seating_preference = Column(String(50), default="ROOFTOP")  # INDOOR, OUTDOOR, ROOFTOP, PRIVATE
    special_requests = Column(Text, nullable=True)
    status = Column(String(50), default="NEW", index=True)  # NEW, PENDING, UNDER_REVIEW, ACCEPTED, REJECTED, CANCELLED, COMPLETED
    internal_notes = Column(Text, nullable=True)
    assigned_staff_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_staff_name = Column(String(255), nullable=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True)
    session_id = Column(String(255), nullable=True, index=True)
    guest_profile_id = Column(Integer, ForeignKey("guest_profiles.id"), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    status_history = relationship("ReservationStatusHistory", back_populates="reservation", cascade="all, delete-orphan", order_by="desc(ReservationStatusHistory.created_at)")
    guest_profile = relationship("GuestProfile", back_populates="reservations")

class ReservationStatusHistory(Base):
    __tablename__ = "reservation_status_history"

    id = Column(Integer, primary_key=True, index=True)
    reservation_id = Column(Integer, ForeignKey("reservation_requests.id", ondelete="CASCADE"), nullable=False, index=True)
    changed_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    changed_by_name = Column(String(255), default="System")
    user_role = Column(String(50), default="STAFF")
    previous_status = Column(String(50), nullable=True)
    new_status = Column(String(50), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    reservation = relationship("ReservationRequest", back_populates="status_history")
