from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class EnvironmentSwitchRequest(BaseModel):
    target_environment: str  # DEMO or REAL
    reason: str
    confirm_acknowledgment: bool

class ChunkDetailResponse(BaseModel):
    id: int
    chunk_index: int
    content: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

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
    verified_at: Optional[datetime] = None
    chunk_count: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class KnowledgeDocDetailResponse(KnowledgeDocResponse):
    chunks: List[ChunkDetailResponse] = []

class ManualKnowledgeCreate(BaseModel):
    title: str
    content: str
    category: str = "POLICY"  # MENU, POLICY, TIMING, EVENT, GENERAL
    outlet_id: Optional[int] = None
    environment: str = "DEMO"

class DocumentUpdateRequest(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    outlet_id: Optional[int] = None

class DocumentStatusUpdateRequest(BaseModel):
    is_active: bool

class SearchHitResponse(BaseModel):
    chunk_id: int
    document_id: int
    document_title: str
    category: str
    environment: str
    outlet_id: Optional[int] = None
    chunk_index: int
    content: str
    score: float
    cosine_similarity: float
    lexical_overlap: float

class KnowledgeSearchResponse(BaseModel):
    query: str
    environment: str
    total_hits: int
    results: List[SearchHitResponse]

class CategoryCount(BaseModel):
    category: str
    count: int

class KnowledgeStatsResponse(BaseModel):
    active_environment: str
    demo_doc_count: int
    real_doc_count: int
    demo_chunk_count: int
    real_chunk_count: int
    total_active_docs: int
    total_inactive_docs: int
    verified_docs_count: int
    unverified_docs_count: int
    categories: List[CategoryCount]
