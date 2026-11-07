from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class MenuItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    currency: str = "INR"
    dietary_flags: str = "VEG"
    is_available: bool = True
    is_signature: bool = False
    display_order: int = 0

class MenuItemCreate(MenuItemBase):
    outlet_id: int
    category_id: Optional[int] = None
    environment: str = "DEMO"

class MenuItemUpdate(BaseModel):
    price: Optional[float] = None
    is_available: Optional[bool] = None
    description: Optional[str] = None
    name: Optional[str] = None

class MenuItemResponse(MenuItemBase):
    id: int
    outlet_id: int
    category_id: Optional[int] = None
    environment: str
    created_at: datetime

    class Config:
        from_attributes = True

class OutletResponse(BaseModel):
    id: int
    name: str
    slug: str
    outlet_type: str
    cuisine_type: str
    opening_time: str
    closing_time: str
    dress_code: str
    seating_capacity: int
    location: Optional[str] = None
    description: Optional[str] = None
    is_popular: bool
    is_active: bool

    class Config:
        from_attributes = True
