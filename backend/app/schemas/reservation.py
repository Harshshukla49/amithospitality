from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime
import re

class ReservationCreate(BaseModel):
    outlet_id: int = Field(..., gt=0, description="Target outlet ID")
    guest_name: str = Field(..., min_length=2, max_length=100, description="Primary guest full name")
    guest_phone: str = Field(..., min_length=7, max_length=25, description="Primary contact phone number")
    guest_email: Optional[EmailStr] = None
    guest_count: int = Field(default=2, ge=1, le=100, description="Party size (1 to 100 covers)")
    reservation_date: str = Field(..., description="Date of reservation in YYYY-MM-DD")
    reservation_time: str = Field(..., description="Time of reservation in HH:MM")
    seating_preference: str = Field(default="ROOFTOP", description="INDOOR, OUTDOOR, ROOFTOP, PRIVATE")
    special_requests: Optional[str] = Field(default=None, max_length=500)
    assigned_staff_name: Optional[str] = None
    session_id: Optional[str] = None
    conversation_id: Optional[int] = None

    @field_validator("guest_name")
    def clean_name(cls, v: str) -> str:
        cleaned = re.sub(r"[<>]", "", v.strip())
        if len(cleaned) < 2:
            raise ValueError("Guest name must contain at least 2 characters")
        return cleaned

    @field_validator("guest_phone")
    def validate_phone(cls, v: str) -> str:
        cleaned = re.sub(r"[^\d+ -]", "", v.strip())
        digits = re.sub(r"\D", "", cleaned)
        if len(digits) < 7 or len(digits) > 15:
            raise ValueError("Phone number must contain between 7 and 15 digits")
        return cleaned

    @field_validator("reservation_date")
    def validate_date_format(cls, v: str) -> str:
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Reservation date must be in YYYY-MM-DD format")
        return v

class ReservationStatusUpdate(BaseModel):
    status: str = Field(..., description="NEW, PENDING, UNDER_REVIEW, ACCEPTED, REJECTED, CANCELLED, COMPLETED")
    internal_notes: Optional[str] = Field(default=None, max_length=1000)
    assigned_staff_id: Optional[int] = None
    assigned_staff_name: Optional[str] = None

class ReservationHistoryItem(BaseModel):
    id: int
    changed_by_name: str
    user_role: str
    previous_status: Optional[str] = None
    new_status: str
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ReservationResponse(BaseModel):
    id: int
    reference_id: Optional[str] = None
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
    assigned_staff_id: Optional[int] = None
    assigned_staff_name: Optional[str] = None
    session_id: Optional[str] = None
    conversation_id: Optional[int] = None
    capacity_warning: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
