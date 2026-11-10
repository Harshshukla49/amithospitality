from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import re

class GuestProfileBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: str = Field(..., min_length=7, max_length=50)
    email: Optional[EmailStr] = None
    preferred_channel: Optional[str] = "SMS"
    dietary_preferences: Optional[str] = "NONE"
    allergies: Optional[str] = None
    cuisine_preferences: Optional[str] = None
    special_occasions: Optional[str] = None
    accessibility_requirements: Optional[str] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        clean = v.strip()
        digits = re.sub(r"[^\d+]", "", clean)
        if len(digits) < 7:
            raise ValueError("Invalid phone number format: must contain at least 7 digits.")
        return clean

class GuestProfileCreate(GuestProfileBase):
    environment: Optional[str] = "DEMO"
    staff_notes: Optional[str] = None
    preferred_outlet_id: Optional[int] = None

class GuestProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    preferred_channel: Optional[str] = None
    dietary_preferences: Optional[str] = None
    allergies: Optional[str] = None
    cuisine_preferences: Optional[str] = None
    special_occasions: Optional[str] = None
    accessibility_requirements: Optional[str] = None
    staff_notes: Optional[str] = None
    vip_status: Optional[bool] = None
    preferred_outlet_id: Optional[int] = None

class GuestProfileResponse(BaseModel):
    id: int
    guest_uuid: str
    environment: str
    full_name: str
    phone: str
    email: Optional[str] = None
    preferred_channel: str
    dietary_preferences: str
    allergies: Optional[str] = None
    cuisine_preferences: Optional[str] = None
    special_occasions: Optional[str] = None
    accessibility_requirements: Optional[str] = None
    staff_notes: Optional[str] = None
    vip_status: bool
    total_visits: int
    total_spend: Optional[float] = 0.0
    currency: Optional[str] = "INR"
    is_shared_contact: Optional[bool] = False
    preferred_outlet_id: Optional[int] = None
    preferred_outlet_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class GuestProfileDetailResponse(GuestProfileResponse):
    reservations: List[Dict[str, Any]] = []
    communication_logs: List[Dict[str, Any]] = []

class GuestLookupRequest(BaseModel):
    reference_id: str = Field(..., min_length=5, max_length=50)
    contact: str = Field(..., min_length=4, max_length=255)

class GuestLookupResponse(BaseModel):
    status: str
    reference_id: str
    target_type: str
    target_masked: str
    expires_in_seconds: int = 600
    demo_otp: Optional[str] = None

class GuestVerifyOtpRequest(BaseModel):
    reference_id: str = Field(..., min_length=5, max_length=50)
    otp: str = Field(..., min_length=4, max_length=10)

class GuestVerifyOtpResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int = 1800
    reservation: Dict[str, Any]

class GuestReservationModifyRequest(BaseModel):
    reservation_date: Optional[str] = None
    reservation_time: Optional[str] = None
    guest_count: Optional[int] = None
    special_requests: Optional[str] = None

class GuestReservationCancelRequest(BaseModel):
    cancellation_reason: str = Field(..., min_length=3, max_length=500)

class ReservationModificationReviewRequest(BaseModel):
    action: str = Field(..., pattern="^(APPROVE|REJECT)$")
    review_notes: Optional[str] = None
