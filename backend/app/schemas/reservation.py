from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class ReservationCreate(BaseModel):
    outlet_id: int
    guest_name: str
    guest_phone: str
    guest_email: Optional[EmailStr] = None
    guest_count: int = 2
    reservation_date: str
    reservation_time: str
    seating_preference: str = "ROOFTOP"
    special_requests: Optional[str] = None

class ReservationStatusUpdate(BaseModel):
    status: str  # NEW, PENDING, UNDER_REVIEW, ACCEPTED, REJECTED, CANCELLED
    internal_notes: Optional[str] = None

class ReservationResponse(BaseModel):
    id: int
    environment: str
    outlet_id: int
    outlet_name: str
    guest_name: str
    guest_phone: str
    guest_email: Optional[str] = None
    guest_count: int
    reservation_date: str
    reservation_time: str
    seating_preference: str
    special_requests: Optional[str] = None
    status: str
    internal_notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
