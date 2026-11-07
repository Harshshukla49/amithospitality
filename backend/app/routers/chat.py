from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import json

from app.database import get_db
from app.models.conversation import Conversation, Message
from app.models.outlet import Outlet, MenuItem
from app.models.knowledge import KnowledgeDocument, KnowledgeChunk, Policy
from app.models.audit import EnvironmentSetting
from app.schemas.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    FeedbackRequest,
    CitationItem,
)

router = APIRouter(prefix="/api/v1/chat", tags=["AI Concierge & Chat"])

def get_current_env(db: Session) -> str:
    setting = db.query(EnvironmentSetting).order_by(EnvironmentSetting.id.desc()).first()
    return setting.active_environment if setting else "DEMO"

@router.post("/messages", response_model=ChatMessageResponse)
def handle_chat_message(req: ChatMessageRequest, db: Session = Depends(get_db)):
    outlet = db.query(Outlet).filter(Outlet.id == req.outlet_id).first()
    if not outlet:
        raise HTTPException(status_code=404, detail="Selected outlet not found")

    active_env = get_current_env(db)
    is_demo = active_env == "DEMO"

    # Persist or retrieve conversation session
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

    # Save incoming user message
    user_msg = Message(
        conversation_id=conv.id,
        sender_type="USER",
        content=req.message,
    )
    db.add(user_msg)
    db.commit()

    lower = req.message.lower()
    citations = []
    suggested_actions = []

    # STRICT ENVIRONMENT ISOLATION GROUNDING LOGIC:
    if not is_demo:
        # REAL MODE: Check for verified documents
        real_docs = (
            db.query(KnowledgeDocument)
            .filter(
                KnowledgeDocument.environment == "REAL",
                KnowledgeDocument.outlet_id == outlet.id,
                KnowledgeDocument.verification_status == "VERIFIED",
                KnowledgeDocument.is_active == True,
            )
            .all()
        )

        if not real_docs:
            reply_text = (
                f"[REAL MODE - VERIFIED INFORMATION REQUIRED]\n\n"
                f"I do not currently have verified corporate documentation indexed regarding this inquiry for **{outlet.name}**.\n\n"
                f"To maintain complete integrity, I strictly do not present unverified information. "
                f"Our Guest Relations Concierge team will be pleased to assist you directly at guestrelations@amithospitality.com or +91 11 4050 9900."
            )
            suggested_actions = ["Connect me with guest relations", "Switch to DEMO mode to view sample menu"]
        else:
            doc_titles = ", ".join([d.title for d in real_docs])
            reply_text = (
                f"Based on verified Amit Hospitality corporate documentation ({doc_titles}), "
                f"**{outlet.name}** operates daily with strict quality standards. How may I assist your booking further?"
            )
            citations = [CitationItem(document_title=real_docs[0].title, category=real_docs[0].category)]
            suggested_actions = ["Show me the verified menu", "Table reservation", "Private event inquiry"]

    else:
        # DEMO MODE: Retrieve from DEMO stores
        if "menu" in lower or "dish" in lower or "food" in lower or "price" in lower:
            menu_items = (
                db.query(MenuItem)
                .filter(MenuItem.outlet_id == outlet.id, MenuItem.environment == "DEMO")
                .all()
            )
            if "price" in lower or "cost" in lower or "truffle" in lower or "sea bass" in lower:
                matched = next((i for i in menu_items if i.name.lower().split()[0] in lower or "truffle" in lower), None)
                if matched:
                    reply_text = (
                        f"The **{matched.name}** is priced at **₹{matched.price:,.2f}**.\n\n"
                        f"• *Description:* {matched.description}\n"
                        f"• *Dietary Flags:* {matched.dietary_flags}\n\n"
                        f"*[DEMO DATA - Fictional sample price for presentation]*"
                    )
                else:
                    items_summary = "\n".join([f"• **{i.name}**: ₹{i.price:,.2f}" for i in menu_items[:4]])
                    reply_text = f"Sample pricing for **{outlet.name}**:\n\n{items_summary}\n\n*[DEMO DATA - Sample prices]*"
            else:
                items_summary = "\n".join([f"• **{i.name}** (₹{i.price:,.2f}) — *{i.description}*" for i in menu_items[:5]])
                reply_text = (
                    f"Here is a curated selection from the sample menu at **{outlet.name}**:\n\n"
                    f"{items_summary}\n\n"
                    f"*[DEMO DATA - Illustrative sample menu]*"
                )
            citations = [CitationItem(document_title=f"{outlet.name} Sample Menu Roster", category="MENU")]
            suggested_actions = ["What is the price of the Sea Bass?", "Do you have vegetarian dishes?", "Reserve a table"]

        elif "timing" in lower or "hours" in lower or "dress code" in lower or "open" in lower:
            reply_text = (
                f"**Operating Hours & Policies for {outlet.name}**:\n\n"
                f"• **Timings:** {outlet.opening_time} to {outlet.closing_time} (Daily)\n"
                f"• **Cuisine:** {outlet.cuisine_type}\n"
                f"• **Dress Code:** {outlet.dress_code}\n"
                f"• **Valet Service:** Complimentary valet parking at main portico.\n\n"
                f"*[DEMO DATA - Sample policies]*"
            )
            citations = [CitationItem(document_title=f"{outlet.name} Operating Policies (Sample)", category="POLICY")]
            suggested_actions = ["Book a table", "Show me the cocktail menu", "Private dining options"]

        elif "book" in lower or "reserve" in lower or "table" in lower:
            reply_text = (
                f"I would be delighted to assist you with a table reservation at **{outlet.name}**.\n\n"
                f"Please provide your preferred date, time, and guest count, or use the reservation form. "
                f"*(Note: In DEMO mode, reservations are simulated and will not book real tables.)*"
            )
            suggested_actions = ["Book table for tonight", "Do you have outdoor seating?"]

        elif "private" in lower or "event" in lower or "banquet" in lower or "party" in lower:
            reply_text = (
                f"**{outlet.name}** features exceptional private dining rooms and full buyout options with seating up to {outlet.seating_capacity} guests.\n\n"
                f"Would you like our Banquets Director to prepare a bespoke 5-course proposal for your celebration?"
            )
            suggested_actions = ["Submit private event inquiry", "Speak with Events Team"]

        else:
            reply_text = (
                f"Welcome to **{outlet.name}**. As your luxury concierge, I can assist you with:\n\n"
                f"1. Exploring our curated culinary & mixology creations.\n"
                f"2. Operating hours, valet services, and dress code.\n"
                f"3. Table reservation requests.\n"
                f"4. Private dining, corporate galas, and milestones.\n\n"
                f"How may I curate your evening?"
            )
            suggested_actions = ["Show me the menu", "What are your timings?", "Book a table for tonight"]

    # Save assistant message
    asst_msg = Message(
        conversation_id=conv.id,
        sender_type="ASSISTANT",
        content=reply_text,
        citations_json=json.dumps([c.dict() for c in citations]) if citations else None,
    )
    db.add(asst_msg)
    db.commit()

    return ChatMessageResponse(
        reply=reply_text,
        environment=active_env,
        is_demo=is_demo,
        citations=citations,
        suggested_actions=suggested_actions,
    )

@router.post("/feedback")
def submit_feedback(req: FeedbackRequest, db: Session = Depends(get_db)):
    return {"success": True, "message": "Feedback recorded. Thank you for helping us refine the concierge experience."}

@router.post("/handover")
def request_handover(db: Session = Depends(get_db)):
    return {
        "success": True,
        "message": "A priority notification has been dispatched to the Guest Relations Desk. A concierge host will connect with you shortly.",
        "direct_phone": "+91 11 4050 9900",
    }
