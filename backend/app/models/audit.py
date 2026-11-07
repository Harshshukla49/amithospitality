from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from app.database import Base

class EnvironmentSetting(Base):
    __tablename__ = "environment_settings"

    id = Column(Integer, primary_key=True, index=True)
    active_environment = Column(String(10), default="DEMO", nullable=False)  # DEMO or REAL
    updated_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by_name = Column(String(255), default="System")
    switch_reason = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user_name = Column(String(255), nullable=False)
    user_role = Column(String(50), default="STAFF")
    action = Column(String(100), nullable=False)  # ENVIRONMENT_SWITCH, KNOWLEDGE_INGEST, etc.
    entity_type = Column(String(100), nullable=True)
    entity_id = Column(Integer, nullable=True)
    environment = Column(String(10), default="DEMO")
    details = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
