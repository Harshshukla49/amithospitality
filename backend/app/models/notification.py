from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from app.database import Base

class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50), nullable=False)  # RESERVATION, LEAD
    entity_id = Column(Integer, nullable=False, index=True)
    reference_id = Column(String(100), nullable=True, index=True)
    channel = Column(String(20), nullable=False)  # EMAIL, SMS, WHATSAPP
    recipient = Column(String(255), nullable=False)
    event_type = Column(String(50), nullable=False)  # CREATED, ACCEPTED, CANCELLED, REJECTED, LEAD_ACK
    idempotency_key = Column(String(255), unique=True, index=True, nullable=False)
    status = Column(String(20), default="SENT")  # SENT, SIMULATED, FAILED, DUPLICATE
    error_message = Column(Text, nullable=True)
    environment = Column(String(10), default="DEMO")
    created_at = Column(DateTime, default=datetime.utcnow)
