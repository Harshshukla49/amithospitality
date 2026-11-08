from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.database import Base

class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id = Column(Integer, primary_key=True, index=True)
    environment = Column(String(10), default="DEMO", index=True, nullable=False)  # DEMO or REAL
    outlet_id = Column(Integer, ForeignKey("outlets.id"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)  # PDF, DOCX, XLSX, CSV, TXT, MANUAL
    file_path = Column(String(500), nullable=True)
    file_size_bytes = Column(Integer, default=0)
    mime_type = Column(String(100), nullable=True)
    category = Column(String(50), default="GENERAL")  # MENU, POLICY, TIMING, EVENT, GENERAL
    verification_status = Column(String(50), default="UNVERIFIED")  # VERIFIED, UNVERIFIED, PENDING
    verified_by = Column(String(255), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    chunk_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    chunks = relationship("KnowledgeChunk", back_populates="document", cascade="all, delete-orphan")

class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("knowledge_documents.id"), nullable=True, index=True)
    environment = Column(String(10), default="DEMO", index=True, nullable=False)  # DEMO or REAL
    outlet_id = Column(Integer, ForeignKey("outlets.id"), nullable=True, index=True)
    chunk_index = Column(Integer, default=0)
    content = Column(Text, nullable=False)
    metadata_json = Column(Text, nullable=True)  # JSON-encoded metadata
    embedding_json = Column(Text, nullable=True)  # Vector stored as JSON float array (dual SQLite/PostgreSQL)
    embedding = Column(Vector(256), nullable=True)  # Native pgvector embedding column (PostgreSQL pgvector)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("KnowledgeDocument", back_populates="chunks")

class Policy(Base):
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, index=True)
    outlet_id = Column(Integer, ForeignKey("outlets.id"), nullable=True, index=True)
    environment = Column(String(10), default="DEMO", index=True, nullable=False)
    policy_type = Column(String(100), default="GENERAL")  # CANCELLATION, DRESS_CODE, CHILDREN, VALET
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class FAQ(Base):
    __tablename__ = "faqs"

    id = Column(Integer, primary_key=True, index=True)
    outlet_id = Column(Integer, ForeignKey("outlets.id"), nullable=True, index=True)
    environment = Column(String(10), default="DEMO", index=True, nullable=False)
    category = Column(String(100), default="GENERAL")
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
