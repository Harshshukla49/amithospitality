from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class LeadCreate(BaseModel):
    outlet_id: int
    name: str
    phone: str
    email: EmailStr
    enquiry_type: str = "PRIVATE_DINING"
    guest_count: int = 20
    target_date: str
    budget_range: str = "₹2,50,000 - ₹5,00,000"
    notes: Optional[str] = None

class LeadStatusUpdate(BaseModel):
    status: str  # NEW, CONTACTED, QUALIFIED, PROPOSAL_SENT, WON, LOST
    notes: Optional[str] = None

class LeadResponse(BaseModel):
    id: int
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
    status: str
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
