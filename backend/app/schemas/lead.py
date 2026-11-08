from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime
import re

class LeadCreate(BaseModel):
    outlet_id: int = Field(..., gt=0, description="Target outlet ID")
    name: str = Field(..., min_length=2, max_length=100, description="Contact person full name")
    phone: str = Field(..., min_length=7, max_length=25, description="Contact phone number")
    email: EmailStr = Field(..., description="Contact email address")
    enquiry_type: str = Field(default="PRIVATE_DINING", description="GENERAL_ENQUIRY, PRIVATE_PARTY, BIRTHDAY_PARTY, CORPORATE_EVENT, GROUP_BOOKING, WEDDING_ENQUIRY, CUSTOMER_CALLBACK")
    guest_count: int = Field(default=20, ge=1, le=1000, description="Estimated attendees")
    target_date: str = Field(..., description="Event date or timeline in YYYY-MM-DD")
    budget_range: str = Field(default="₹2,50,000 - ₹5,00,000")
    notes: Optional[str] = Field(default=None, max_length=1000, description="Client specifications and requirements")
    assigned_staff_name: Optional[str] = None
    source: Optional[str] = Field(default="CHATBOT", description="CHATBOT, MANUAL, WEBSITE")
    session_id: Optional[str] = None
    conversation_id: Optional[int] = None

    @field_validator("name")
    def clean_name(cls, v: str) -> str:
        cleaned = re.sub(r"[<>]", "", v.strip())
        if len(cleaned) < 2:
            raise ValueError("Name must contain at least 2 characters")
        return cleaned

    @field_validator("phone")
    def validate_phone(cls, v: str) -> str:
        cleaned = re.sub(r"[^\d+ -]", "", v.strip())
        digits = re.sub(r"\D", "", cleaned)
        if len(digits) < 7 or len(digits) > 15:
            raise ValueError("Phone number must contain between 7 and 15 digits")
        return cleaned

class LeadStatusUpdate(BaseModel):
    status: str = Field(..., description="NEW, CONTACTED, QUALIFIED, FOLLOW_UP_REQUIRED, CONVERTED, CLOSED")
    notes: Optional[str] = Field(default=None, max_length=1000)
    internal_notes: Optional[str] = Field(default=None, max_length=1000)
    assigned_staff_id: Optional[int] = None
    assigned_staff_name: Optional[str] = None

class LeadHistoryItem(BaseModel):
    id: int
    changed_by_name: str
    user_role: str
    previous_status: Optional[str] = None
    new_status: str
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class LeadResponse(BaseModel):
    id: int
    reference_id: Optional[str] = None
    environment: str
    outlet_id: int
    outlet_name: str
    name: str
    phone: str
    email: str
    enquiry_type: str
    guest_count: int
    target_date: str
    budget_range: str
    source: str
    status: str
    notes: Optional[str] = None
    internal_notes: Optional[str] = None
    assigned_staff_id: Optional[int] = None
    assigned_staff_name: Optional[str] = None
    session_id: Optional[str] = None
    conversation_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
