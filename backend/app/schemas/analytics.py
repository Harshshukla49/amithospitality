from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class FrequentQueryItem(BaseModel):
    query: str
    count: int
    category: str

class UnansweredItem(BaseModel):
    question: str
    frequency: int
    outlet: str
    suggestion: str

class DashboardKPIs(BaseModel):
    total_conversations: int
    pending_reservations: int
    total_leads: int
    active_documents: int
    active_environment: str
    total_covers: int = 0
    accepted_reservations: int = 0
    reservation_status_breakdown: Dict[str, int] = Field(default_factory=dict)
    lead_status_breakdown: Dict[str, int] = Field(default_factory=dict)
    lead_type_breakdown: Dict[str, int] = Field(default_factory=dict)
    date_range: str = "7D"
    outlet_id: Optional[int] = None
    outlet_name: Optional[str] = None
    frequent_queries: List[FrequentQueryItem] = Field(default_factory=list)
    unanswered_questions: List[UnansweredItem] = Field(default_factory=list)
