from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from app.database import Base

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    environment = Column(String(10), default="DEMO", index=True, nullable=False)  # DEMO or REAL
    outlet_id = Column(Integer, ForeignKey("outlets.id"), nullable=False, index=True)
    outlet_name = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=False)
    email = Column(String(255), nullable=False)
    enquiry_type = Column(String(100), default="PRIVATE_DINING")  # PRIVATE_DINING, CORPORATE_EVENT, WEDDING, BIRTHDAY, CATERING
    guest_count = Column(Integer, default=20)
    target_date = Column(String(20), nullable=False)
    budget_range = Column(String(100), default="₹2,50,000 - ₹5,00,000")
    source = Column(String(50), default="CHATBOT")
    status = Column(String(50), default="NEW", index=True)  # NEW, CONTACTED, QUALIFIED, PROPOSAL_SENT, WON, LOST
    notes = Column(Text, nullable=True)
    assigned_staff_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
