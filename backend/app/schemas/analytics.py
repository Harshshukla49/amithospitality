from pydantic import BaseModel
from typing import List, Dict

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
    frequent_queries: List[FrequentQueryItem]
    unanswered_questions: List[UnansweredItem]
