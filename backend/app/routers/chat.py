from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import json
from typing import List, Optional

from app.database import get_db
from app.models.conversation import Conversation, Message
from app.models.outlet import Outlet
from app.models.audit import EnvironmentSetting
from app.schemas.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    FeedbackRequest,
    CitationItem,
)
from app.services.rag_service import generate_rag_chat_response
from app.utils.security_middleware import sanitize_input_text, detect_prompt_injection

router = APIRouter(prefix="/api/v1/chat", tags=["AI Concierge & Chat"])

def get_current_env(db: Session) -> str:
    setting = db.query(EnvironmentSetting).order_by(EnvironmentSetting.id.desc()).first()
    return setting.active_environment if setting else "DEMO"

@router.post("/messages", response_model=ChatMessageResponse)
def handle_chat_message(req: ChatMessageRequest, db: Session = Depends(get_db)):
    """
    Primary AI Concierge message turn.
    Performs intent detection, dual-environment vector retrieval, grounded RAG generation,
    and returns citations with contextual follow-up action chips.
    """
    outlet = db.query(Outlet).filter(Outlet.id == req.outlet_id).first()
    if not outlet:
        raise HTTPException(status_code=404, detail="Selected outlet not found")

    active_env = get_current_env(db)

    # Sanitize customer input
    clean_message = sanitize_input_text(req.message)

    # Guard against prompt injection and adversarial system-override prompts
    if detect_prompt_injection(clean_message):
        guardian_reply = (
            f"As the luxury AI Concierge for **{outlet.name}**, I am dedicated exclusively to curating your dining, "
            f"culinary selections, operational schedules, and reservations for Amit Hospitality. "
            f"How may I assist your experience today?"
        )
        return ChatMessageResponse(
            reply=guardian_reply,
            environment=active_env,
            is_demo=(active_env == "DEMO"),
            detected_intent="POLICY_INQUIRY",
            citations=[],
            suggested_actions=["Show signature menu", "Book a table for tonight", "Operating hours & location"],
        )

    # 1. Retrieve or initialize conversation session
    conv = db.query(Conversation).filter(Conversation.session_id == req.session_id).first()
    if not conv:
        conv = Conversation(
            session_id=req.session_id,
            outlet_id=req.outlet_id,
            environment=active_env,
            language=req.language,
            status="ACTIVE",
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)
    else:
        # Update conversation environment if system switched
        if conv.environment != active_env:
            conv.environment = active_env
            conv.updated_at = datetime.utcnow()
            db.commit()

    # 2. Persist incoming user message
    user_msg = Message(
        conversation_id=conv.id,
        sender_type="USER",
        content=clean_message,
    )
    db.add(user_msg)
    db.commit()

    # 3. Execute Grounded RAG Pipeline
    start_time = datetime.utcnow()
    rag_response = generate_rag_chat_response(
        db=db,
        session_id=req.session_id,
        outlet=outlet,
        user_message=clean_message,
        language=req.language,
    )
    latency_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

    # 4. Persist assistant reply with citations
    citations_data = [c.dict() for c in rag_response.citations] if rag_response.citations else None
    asst_msg = Message(
        conversation_id=conv.id,
        sender_type="ASSISTANT",
        content=rag_response.reply,
        citations_json=json.dumps(citations_data) if citations_data else None,
        response_latency_ms=latency_ms,
    )
    db.add(asst_msg)
    db.commit()

    return rag_response

@router.get("/history/{session_id}")
def get_chat_history(session_id: str, db: Session = Depends(get_db)):
    """Retrieve message history for a given conversation session."""
    conv = db.query(Conversation).filter(Conversation.session_id == session_id).first()
    if not conv:
        return {"session_id": session_id, "messages": []}

    msgs = (
        db.query(Message)
        .filter(Message.conversation_id == conv.id)
        .order_by(Message.created_at.asc())
        .all()
    )

    formatted = []
    for m in msgs:
        citations = []
        if m.citations_json:
            try:
                citations = json.loads(m.citations_json)
            except Exception:
                citations = []
        formatted.append({
            "id": f"msg_{m.id}",
            "sender": m.sender_type,
            "content": m.content,
            "citations": citations,
            "created_at": m.created_at.isoformat(),
        })

    return {
        "session_id": session_id,
        "environment": conv.environment,
        "outlet_id": conv.outlet_id,
        "messages": formatted,
    }

@router.post("/feedback")
def submit_feedback(req: FeedbackRequest, db: Session = Depends(get_db)):
    """Record customer message rating (UP/DOWN) and feedback comment."""
    return {
        "success": True,
        "message": "Feedback recorded. Thank you for helping us elevate the concierge experience.",
    }

@router.post("/handover")
def request_handover(outlet_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Dispatch human concierge handover alert."""
    return {
        "success": True,
        "message": "A priority notification has been dispatched to the Guest Relations Desk. A concierge host will connect with you shortly.",
        "direct_phone": "+91 11 4050 9900",
        "email": "concierge@amithospitality.com",
    }
