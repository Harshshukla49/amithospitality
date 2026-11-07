from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ChatMessageRequest(BaseModel):
    session_id: str
    outlet_id: int
    message: str
    language: str = "EN"

class CitationItem(BaseModel):
    document_title: str
    category: str

class ChatMessageResponse(BaseModel):
    reply: str
    environment: str
    is_demo: bool
    citations: Optional[List[CitationItem]] = None
    suggested_actions: Optional[List[str]] = None

class FeedbackRequest(BaseModel):
    message_id: str
    rating: str  # UP or DOWN
    comment: Optional[str] = None
