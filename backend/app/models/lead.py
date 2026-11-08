import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

def generate_lead_ref() -> str:
    today_str = datetime.utcnow().strftime("%Y%m%d")
    short_suffix = uuid.uuid4().hex[:6].upper()
    return f"REF-LEAD-{today_str}-{short_suffix}"

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    reference_id = Column(String(50), unique=True, index=True, default=generate_lead_ref)
    environment = Column(String(10), default="DEMO", index=True, nullable=False)  # DEMO or REAL
    outlet_id = Column(Integer, ForeignKey("outlets.id"), nullable=False, index=True)
    outlet_name = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=False)
    email = Column(String(255), nullable=False)
    enquiry_type = Column(String(100), default="PRIVATE_DINING")  # GENERAL_ENQUIRY, PRIVATE_PARTY, BIRTHDAY_PARTY, CORPORATE_EVENT, GROUP_BOOKING, WEDDING_ENQUIRY, CUSTOMER_CALLBACK
    guest_count = Column(Integer, default=20)
    target_date = Column(String(20), nullable=False)
    budget_range = Column(String(100), default="₹2,50,000 - ₹5,00,000")
    source = Column(String(50), default="CHATBOT")  # CHATBOT, MANUAL, WEBSITE
    status = Column(String(50), default="NEW", index=True)  # NEW, CONTACTED, QUALIFIED, FOLLOW_UP_REQUIRED, CONVERTED, CLOSED
    notes = Column(Text, nullable=True)  # Customer requirements / special notes
    internal_notes = Column(Text, nullable=True)  # Staff internal notes
    assigned_staff_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_staff_name = Column(String(255), nullable=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True)
    session_id = Column(String(255), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    status_history = relationship("LeadStatusHistory", back_populates="lead", cascade="all, delete-orphan", order_by="desc(LeadStatusHistory.created_at)")

class LeadStatusHistory(Base):
    __tablename__ = "lead_status_history"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True)
    changed_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    changed_by_name = Column(String(255), default="System")
    user_role = Column(String(50), default="STAFF")
    previous_status = Column(String(50), nullable=True)
    new_status = Column(String(50), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    lead = relationship("Lead", back_populates="status_history")
