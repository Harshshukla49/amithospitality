from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from app.database import Base

class ReservationRequest(Base):
    __tablename__ = "reservation_requests"

    id = Column(Integer, primary_key=True, index=True)
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
    status = Column(String(50), default="NEW", index=True)  # NEW, PENDING, UNDER_REVIEW, ACCEPTED, REJECTED, CANCELLED
    internal_notes = Column(Text, nullable=True)
    assigned_staff_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
