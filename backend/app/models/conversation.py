from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True, index=True)
    email = Column(String(255), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_seen_at = Column(DateTime, default=datetime.utcnow)

    conversations = relationship("Conversation", back_populates="customer")

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    outlet_id = Column(Integer, ForeignKey("outlets.id"), nullable=True)
    environment = Column(String(10), default="DEMO", index=True, nullable=False)
    status = Column(String(50), default="ACTIVE")  # ACTIVE, RESOLVED, HANDOVER_REQUESTED
    language = Column(String(10), default="EN")
    channel = Column(String(50), default="WEB")  # WEB, WIDGET, MOBILE
    rating = Column(Integer, nullable=True)  # 1-5 rating or thumbs up/down
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = relationship("Customer", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)
    sender_type = Column(String(50), nullable=False)  # USER, ASSISTANT, SYSTEM
    content = Column(Text, nullable=False)
    citations_json = Column(Text, nullable=True)
    tokens_used = Column(Integer, default=0)
    response_latency_ms = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")
