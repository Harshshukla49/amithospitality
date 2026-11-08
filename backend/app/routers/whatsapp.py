import json
import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, Request, Response, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.conversation import Customer, Conversation, Message
from app.models.reservation import ReservationRequest
from app.models.lead import Lead
from app.models.audit import EnvironmentSetting, AuditLog
from app.models.outlet import Outlet
from app.models.user import User
from app.services.whatsapp_service import whatsapp_service
from app.services.intent_service import detect_intent
from app.services.rag_service import generate_rag_chat_response
from app.routers.reservations import generate_reservation_ref
from app.routers.leads import generate_lead_ref
from app.utils.security import require_roles

router = APIRouter(prefix="/api/v1/whatsapp", tags=["WhatsApp Business Integration"])
logger = logging.getLogger("whatsapp_router")

def get_current_env(db: Session) -> str:
    setting = db.query(EnvironmentSetting).order_by(EnvironmentSetting.id.desc()).first()
    return setting.active_environment if setting else "DEMO"

@router.get("/webhook")
def verify_whatsapp_webhook(
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge"),
):
    """
    Meta WhatsApp Cloud API Webhook Verification Endpoint.
    Validates challenge token provided in Meta App Dashboard during webhook registration.
    """
    expected_token = settings.WHATSAPP_VERIFY_TOKEN or "amit_concierge_whatsapp_verify_token_2026"

    if hub_mode == "subscribe" and hub_verify_token == expected_token:
        logger.info("[OK] Meta WhatsApp webhook successfully verified.")
        return Response(content=hub_challenge or "", media_type="text/plain")

    logger.warning(f"WhatsApp webhook verification failed: token mismatch (mode={hub_mode})")
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Verification token mismatch")

@router.post("/webhook")
async def process_whatsapp_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Process incoming WhatsApp events from Meta Cloud API.
    Handles message deduplication, conversation persistence, AI concierge RAG replies,
    reservation requests, event leads, and delivery status tracking.
    """
    body_bytes = await request.body()
    sig_header = request.headers.get("X-Hub-Signature-256")

    # Validate HMAC signature if app secret is configured
    if not whatsapp_service.verify_webhook_signature(body_bytes, sig_header):
        logger.warning("Rejected WhatsApp webhook with invalid HMAC signature.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook signature")

    try:
        payload = json.loads(body_bytes.decode("utf-8"))
    except Exception:
        return {"status": "invalid_json"}

    # Walk entries in Meta webhook structure
    entries = payload.get("entry", [])
    for entry in entries:
        for change in entry.get("changes", []):
            val = change.get("value", {})

            # 1. Handle Message Delivery Statuses
            statuses = val.get("statuses", [])
            for st in statuses:
                wamid = st.get("id")
                status_type = st.get("status")  # sent, delivered, read, failed
                logger.debug(f"WhatsApp message {wamid} status: {status_type}")

            # 2. Handle Inbound Customer Messages
            messages = val.get("messages", [])
            contacts = val.get("contacts", [])
            contact_name = contacts[0].get("profile", {}).get("name", "WhatsApp Guest") if contacts else "WhatsApp Guest"

            for msg in messages:
                wamid = msg.get("id")
                from_phone = msg.get("from")  # E.164 phone without '+'
                msg_type = msg.get("type")

                # Deduplication check
                if whatsapp_service.is_duplicate_message(wamid):
                    logger.info(f"Ignored duplicate WhatsApp message: {wamid}")
                    continue

                # Extract text body
                user_text = ""
                if msg_type == "text":
                    user_text = msg.get("text", {}).get("body", "").strip()
                elif msg_type == "interactive":
                    user_text = msg.get("interactive", {}).get("button_reply", {}).get("title", "")
                elif msg_type == "button":
                    user_text = msg.get("button", {}).get("text", "")

                if not user_text or not from_phone:
                    continue

                formatted_phone = f"+{from_phone}"
                active_env = get_current_env(db)

                # Customer Identity Mapping
                customer = db.query(Customer).filter(Customer.phone == formatted_phone).first()
                if not customer:
                    customer = Customer(
                        phone=formatted_phone,
                        name=contact_name,
                        preferred_language="EN",
                        first_channel="WHATSAPP",
                        last_channel="WHATSAPP",
                    )
                    db.add(customer)
                    db.commit()
                    db.refresh(customer)

                # Resolve Preferred / Default Outlet
                outlet = db.query(Outlet).filter(Outlet.is_active == True).first()
                if not outlet:
                    outlet = Outlet(name="Amit Hospitality Flagship", slug="flagship", outlet_type="Dining Lounge", location="New Delhi", is_active=True)
                    db.add(outlet)
                    db.commit()

                # Conversation Persistence
                conversation = (
                    db.query(Conversation)
                    .filter(
                        Conversation.customer_id == customer.id,
                        Conversation.environment == active_env,
                        Conversation.channel == "WHATSAPP",
                    )
                    .order_by(Conversation.id.desc())
                    .first()
                )

                if not conversation:
                    conversation = Conversation(
                        customer_id=customer.id,
                        session_id=f"wa_{from_phone}_{int(time.time())}",
                        channel="WHATSAPP",
                        environment=active_env,
                        outlet_id=outlet.id,
                        status="ACTIVE",
                    )
                    db.add(conversation)
                    db.commit()
                    db.refresh(conversation)

                # Save user message
                user_msg_record = Message(
                    conversation_id=conversation.id,
                    sender_type="USER",
                    content=user_text,
                    detected_intent="UNKNOWN",
                )
                db.add(user_msg_record)
                db.commit()

                # Detect Intent
                intent_res = detect_intent(user_text)
                detected_intent = intent_res["intent"]
                user_msg_record.detected_intent = detected_intent
                entities = intent_res.get("entities", {})

                outbound_reply_text = ""

                # Flow A: Table Reservation Request Intent
                if detected_intent in ("RESERVATION_REQUEST", "BOOKING_REQUEST") or "book a table" in user_text.lower():
                    ref_id = generate_reservation_ref()
                    guest_count = entities.get("guest_count") or 2
                    res_date = entities.get("date") or "2026-11-20"
                    res_time = entities.get("time") or "20:00"

                    new_res = ReservationRequest(
                        reference_id=ref_id,
                        environment=active_env,
                        outlet_id=outlet.id,
                        outlet_name=outlet.name,
                        customer_id=customer.id,
                        guest_name=customer.name,
                        guest_phone=customer.phone,
                        guest_count=guest_count,
                        reservation_date=res_date,
                        reservation_time=res_time,
                        status="NEW",
                        source="WHATSAPP",
                        conversation_id=conversation.id,
                    )
                    db.add(new_res)
                    db.commit()

                    whatsapp_service.send_reservation_confirmation(
                        to_phone=formatted_phone,
                        guest_name=customer.name,
                        reference_id=ref_id,
                        outlet_name=outlet.name,
                        reservation_date=res_date,
                        reservation_time=res_time,
                        guest_count=guest_count,
                        is_demo=(active_env == "DEMO"),
                    )
                    outbound_reply_text = f"Reservation request registered ({ref_id}). Confirmation sent via WhatsApp."

                # Flow B: Corporate / Banquet Event Lead Intent
                elif detected_intent in ("EVENT_INQUIRY", "PARTY_INQUIRY", "CORPORATE_EVENT") or "party" in user_text.lower():
                    lead_ref = generate_lead_ref()
                    new_lead = Lead(
                        reference_id=lead_ref,
                        environment=active_env,
                        outlet_id=outlet.id,
                        outlet_name=outlet.name,
                        name=customer.name,
                        phone=customer.phone,
                        email="whatsapp_lead@amithospitality.local",
                        enquiry_type="PRIVATE_PARTY" if "party" in user_text.lower() else "CORPORATE_EVENT",
                        guest_count=entities.get("guest_count") or 30,
                        target_date=entities.get("date") or "2026-12-01",
                        source="WHATSAPP",
                        status="NEW",
                        conversation_id=conversation.id,
                    )
                    db.add(new_lead)
                    db.commit()

                    lead_msg = (
                        f"Thank you, {customer.name}! We have registered your private event enquiry for *{outlet.name}* (Ref: *{lead_ref}*).\n\n"
                        f"Our dedicated Events & Banquets Director will contact you within 2 hours to curate your bespoke menu and arrangements."
                    )
                    whatsapp_service.send_text_message(to_phone=formatted_phone, text_body=lead_msg)
                    outbound_reply_text = lead_msg

                # Flow C: Human Concierge Escalation Intent
                elif detected_intent == "HUMAN_HANDOVER" or "manager" in user_text.lower() or "human" in user_text.lower():
                    audit = AuditLog(
                        user_name=customer.name,
                        user_role="CUSTOMER",
                        action="HUMAN_HANDOVER_REQUESTED",
                        entity_type="WHATSAPP_CONVERSATION",
                        environment=active_env,
                        details=f"Priority callback requested via WhatsApp from {customer.phone}",
                    )
                    db.add(audit)
                    db.commit()

                    handover_msg = (
                        f"Namaste {customer.name}. We have alerted our Senior Guest Relations Concierge at *{outlet.name}*.\n\n"
                        f"A dining host will call you directly at {customer.phone} shortly. You may also connect immediately at +91 11 4050 9900."
                    )
                    whatsapp_service.send_text_message(to_phone=formatted_phone, text_body=handover_msg)
                    outbound_reply_text = handover_msg

                # Flow D: Standard Hospitality Concierge RAG Answer
                else:
                    rag_res = generate_rag_chat_response(
                        db=db,
                        session_id=conversation.session_id,
                        outlet=outlet,
                        user_message=user_text,
                        language=customer.preferred_language or "EN",
                    )
                    outbound_reply_text = rag_res.reply
                    whatsapp_service.send_text_message(to_phone=formatted_phone, text_body=outbound_reply_text)

                # Save assistant message
                assistant_msg = Message(
                    conversation_id=conversation.id,
                    sender_type="ASSISTANT",
                    content=outbound_reply_text,
                    detected_intent=detected_intent,
                )
                db.add(assistant_msg)
                db.commit()

    return {"status": "success"}

@router.post("/test-connection")
def test_whatsapp_connection(
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN")),
):
    """
    Perform an authorized live verification check against Meta WhatsApp Cloud API.
    """
    return whatsapp_service.test_connection()

@router.post("/send-message")
def send_custom_whatsapp(
    to_phone: str,
    message: str,
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN", "MANAGER", "STAFF")),
):
    """
    Dispatch manual concierge WhatsApp message to guest.
    """
    return whatsapp_service.send_text_message(to_phone=to_phone, text_body=message)
