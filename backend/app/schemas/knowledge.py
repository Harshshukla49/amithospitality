from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class EnvironmentSwitchRequest(BaseModel):
    target_environment: str  # DEMO or REAL
    reason: str
    confirm_acknowledgment: bool

class KnowledgeDocResponse(BaseModel):
    id: int
    environment: str
    outlet_id: Optional[int] = None
    title: str
    file_name: str
    file_type: str
    file_size_bytes: int
    category: str
    verification_status: str
    verified_by: Optional[str] = None
    chunk_count: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ManualKnowledgeCreate(BaseModel):
    title: str
    content: str
    category: str = "POLICY"  # MENU, POLICY, TIMING, EVENT, GENERAL
    outlet_id: Optional[int] = None
    environment: str = "DEMO"
