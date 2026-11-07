from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from app.database import Base

class AIConfiguration(Base):
    __tablename__ = "ai_configurations"

    id = Column(Integer, primary_key=True, index=True)
    environment = Column(String(10), default="DEMO", nullable=False)  # DEMO or REAL
    model_name = Column(String(100), default="gemini-1.5-flash")
    temperature = Column(Float, default=0.2)
    max_tokens = Column(Integer, default=1000)
    system_prompt = Column(Text, nullable=True)
    top_k_retrievals = Column(Integer, default=4)
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
