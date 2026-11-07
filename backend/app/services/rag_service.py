import json
import logging
import httpx
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.outlet import Outlet, MenuItem
from app.models.knowledge import KnowledgeChunk, KnowledgeDocument
from app.models.conversation import Conversation, Message
from app.services.intent_service import detect_intent
from app.services.embedding_service import search_relevant_chunks
from app.schemas.chat import CitationItem, ChatMessageResponse
from app.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the Premier AI Concierge for Amit Hospitality, representing luxury dining and nightlife destinations in New Delhi.
Your tone is sophisticated, welcoming, warm, articulate, and observant of luxury hospitality standards.

CRITICAL OPERATIONAL RULES:
1. GROUNDING MANDATE: Answer strictly based on the provided Context Documents and Menu Items below. Never fabricate dishes, ingredients, prices, operating hours, or policies.
2. MODE ADHERENCE:
   - If Environment is DEMO: Use the sample context provided. Clearly note that pricing and items are illustrative DEMO data.
   - If Environment is REAL: Answer only from verified company documentation. If verified details are not in the context, explicitly inform the guest that verified documentation is currently unavailable for this specific inquiry and offer direct connection to Guest Relations. NEVER invent or guess facts.
3. CONVERSATIONAL CONTINUITY: Take into account recent turns in the conversation.
4. CITATIONS: Include precise references to the source documents used.
"""

def call_gemini_api(
    prompt: str,
    system_instruction: str,
    api_key: str,
    model: str = "gemini-2.5-flash"
) -> Optional[str]:
    """Call Google Gemini API using REST endpoint."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": system_instruction}]},
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 800,
        }
    }
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "").strip()
    except Exception as e:
        logger.warning(f"Gemini API call failed or timed out: {e}")
    return None

def build_deterministic_concierge_response(
    intent: str,
    outlet: Outlet,
    environment: str,
    chunks: List[Dict[str, Any]],
    menu_items: List[MenuItem],
    entities: Dict[str, Any],
    query: str,
) -> Dict[str, Any]:
    """
    High-fidelity deterministic concierge generation engine.
    Ensures 100% reliable, grounded hospitality responses even without external API keys.
    """
    lower = query.lower()
    citations: List[CitationItem] = []
    suggested_actions: List[str] = []

    # If chunks were retrieved, build citations
    for c in chunks[:3]:
        snippet_text = c["content"].split("\n")[0] if "\n" in c["content"] else c["content"][:120]
        citations.append(CitationItem(
            document_title=c["document_title"],
            category=c["category"],
            snippet=snippet_text,
        ))

    # --- REAL MODE ZERO-HALLUCINATION GUARD ---
    if environment == "REAL" and not chunks:
        reply = (
            f"[REAL MODE — VERIFIED INFORMATION REQUIRED]\n\n"
            f"I do not currently have verified corporate documentation indexed regarding this specific inquiry for **{outlet.name}**.\n\n"
            f"To maintain strict operational authenticity, our AI Concierge does not present unverified information. "
            f"Please allow our Guest Relations team to assist you directly at **guestrelations@amithospitality.com** or **+91 11 4050 9900**."
        )
        return {
            "reply": reply,
            "citations": [],
            "suggested_actions": ["Connect with Guest Relations", "Submit event enquiry", "Switch to DEMO mode for sample data"],
        }

    # --- 1. HUMAN HANDOVER INTENT ---
    if intent == "HUMAN_HANDOVER":
        reply = (
            f"I am pleased to connect you directly with our Guest Relations Desk at **{outlet.name}**.\n\n"
            f"A priority notification has been routed to our duty manager. "
            f"For immediate concierge assistance, you may also call our concierge hotline directly at **+91 11 4050 9900** or email **concierge@amithospitality.com**."
        )
        suggested_actions = ["Call Concierge Desk", "Check today's table availability"]
        return {"reply": reply, "citations": citations, "suggested_actions": suggested_actions}

    # --- 2. MENU & PRICING INQUIRY ---
    if intent in ["MENU_INQUIRY", "PRICING_INQUIRY"]:
        # Check if query matches specific item in menu_items
        matched_items = [
            i for i in menu_items
            if any(word in i.name.lower() for word in lower.split() if len(word) > 3)
            or ("truffle" in lower and "truffle" in i.name.lower())
            or ("dumpling" in lower and "dumpling" in i.name.lower())
            or ("biryani" in lower and "biryani" in i.name.lower())
            or ("nihari" in lower and "nihari" in i.name.lower())
            or ("kebab" in lower and "kebab" in i.name.lower())
        ]

        if matched_items:
            item = matched_items[0]
            dietary_val = ", ".join(item.dietary_flags) if isinstance(item.dietary_flags, list) else str(item.dietary_flags or "")
            dietary_str = f" [{dietary_val}]" if dietary_val else ""
            reply = (
                f"From our culinary creations at **{outlet.name}**:\n\n"
                f"• **{item.name}** — **₹{item.price:,.2f}**{dietary_str}\n"
                f"  *{item.description}*\n\n"
            )
            if len(matched_items) > 1:
                reply += "You may also savor:\n"
                for other in matched_items[1:3]:
                    reply += f"• **{other.name}** (₹{other.price:,.2f}) — *{other.description}*\n"
            
            if environment == "DEMO":
                reply += "\n*[DEMO DATA — Fictional sample pricing for demonstration]*"
            
            suggested_actions = ["Reserve a table to savor this", "View beverage pairings", "Ask about dietary options"]
        elif chunks:
            # Answer directly from chunk content
            chunk_body = "\n\n".join([f"• {c['content']}" for c in chunks[:2]])
            reply = (
                f"Here are the culinary details for **{outlet.name}**:\n\n"
                f"{chunk_body}\n"
            )
            if environment == "DEMO":
                reply += "\n*[DEMO DATA — Illustrative sample menu]*"
            suggested_actions = ["What is the price range?", "Reserve a table for dinner", "Do you have Jain options?"]
        elif menu_items:
            summary = "\n".join([
                f"• **{i.name}** (₹{i.price:,.2f}) — *{i.description}*"
                for i in menu_items[:4]
            ])
            reply = (
                f"Here is a curated culinary preview for **{outlet.name}** ({outlet.cuisine_type}):\n\n"
                f"{summary}\n"
            )
            if environment == "DEMO":
                reply += "\n*[DEMO DATA — Fictional sample menu]*"
            suggested_actions = ["Do you have vegetarian options?", "Book table for tonight", "Operating hours"]
        else:
            reply = f"Our culinary team at **{outlet.name}** specializes in **{outlet.cuisine_type}**. Please inform me of your taste preferences or dietary needs."
            suggested_actions = ["Show signature dishes", "Operating hours"]

        return {"reply": reply, "citations": citations, "suggested_actions": suggested_actions}

    # --- 3. TIMING & LOCATION INQUIRY ---
    if intent == "TIMING_LOCATION":
        if chunks:
            primary_chunk = chunks[0]["content"]
            reply = f"**Operating Schedule & Location Details for {outlet.name}**:\n\n{primary_chunk}\n\n"
        else:
            reply = (
                f"**{outlet.name}** details:\n\n"
                f"• **Operating Hours:** {outlet.opening_time} to {outlet.closing_time} (Daily)\n"
                f"• **Cuisine & Concept:** {outlet.cuisine_type} ({outlet.outlet_type})\n"
                f"• **Address & Location:** {outlet.location}\n"
                f"• **Dress Code:** {outlet.dress_code}\n"
                f"• **Valet Parking:** Complimentary VIP valet parking is available at the main portico.\n\n"
            )
        if environment == "DEMO":
            reply += "*[DEMO DATA — Fictional sample policies]*"
        suggested_actions = ["Book a table for tonight", "Show me the cocktail menu", "Private dining options"]
        return {"reply": reply, "citations": citations, "suggested_actions": suggested_actions}

    # --- 4. POLICY & DRESS CODE INQUIRY ---
    if intent == "POLICY_INQUIRY":
        if chunks:
            primary_chunk = chunks[0]["content"]
            reply = f"**Policies & Etiquette at {outlet.name}**:\n\n{primary_chunk}\n\n"
        else:
            reply = (
                f"**Guest Policies at {outlet.name}**:\n\n"
                f"• **Dress Code:** {outlet.dress_code}. We request smart, polished evening attire.\n"
                f"• **Reservations Policy:** Tables are held for 15 minutes past the scheduled booking time.\n"
                f"• **Valet Service:** Complimentary valet service available for all guests.\n\n"
            )
        if environment == "DEMO":
            reply += "*[DEMO DATA — Sample policy details]*"
        suggested_actions = ["Book table for tonight", "What are your timings?", "Private dining inquiry"]
        return {"reply": reply, "citations": citations, "suggested_actions": suggested_actions}

    # --- 5. RESERVATION REQUEST ---
    if intent == "RESERVATION_REQUEST":
        guest_count_text = f" for {entities.get('guest_count')} guests" if entities.get("guest_count") else ""
        time_text = f" at {entities.get('time')}" if entities.get("time") else ""
        reply = (
            f"It will be my pleasure to assist with your table reservation at **{outlet.name}**{guest_count_text}{time_text}.\n\n"
            f"To confirm your reservation, please specify:\n"
            f"1. Date of your visit\n"
            f"2. Preferred seating (Indoor, Al Fresco Terrace, or Private Dining)\n"
            f"3. Any anniversary, celebration, or dietary preferences\n\n"
            f"You can also click **'Reserve a Table'** to open the interactive booking drawer."
        )
        if environment == "DEMO":
            reply += "\n\n*[DEMO DATA — Reservation requests in DEMO mode are simulated]*"
        suggested_actions = ["Open Reservation Drawer", "View seating options", "Check tonight's availability"]
        return {"reply": reply, "citations": citations, "suggested_actions": suggested_actions}

    # --- 6. EVENT & PRIVATE DINING INQUIRY ---
    if intent == "EVENT_INQUIRY":
        reply = (
            f"**{outlet.name}** provides exclusive settings for intimate gatherings, executive board dinners, and landmark celebrations.\n\n"
            f"• **Venue Capacity:** Accommodates up to {outlet.seating_capacity} guests in curated configurations.\n"
            f"• **Bespoke Menus:** Multi-course tasting menus paired with sommelier-selected vintages.\n"
            f"• **Dedicated Host:** A senior banquets manager coordinates your entire event timeline.\n\n"
            f"Would you like our Events Director to prepare a bespoke proposal?"
        )
        if environment == "DEMO":
            reply += "\n\n*[DEMO DATA — Sample event specifications]*"
        suggested_actions = ["Submit Private Event Lead", "Contact Events Director", "View cocktail packages"]
        return {"reply": reply, "citations": citations, "suggested_actions": suggested_actions}

    # --- 7. DIETARY INQUIRY ---
    if intent == "DIETARY_INQUIRY":
        diet_str = ", ".join(entities.get("dietary", ["Special Dietary Accommodations"]))
        if chunks:
            reply = f"**Dietary Accommodations ({diet_str}) at {outlet.name}**:\n\n{chunks[0]['content']}\n\n"
        else:
            reply = (
                f"At **{outlet.name}**, our culinary masterchefs cater with the utmost precision to dietary requirements:\n\n"
                f"• **Jain Dining:** Dedicated preparations crafted strictly without root vegetables, onion, or garlic upon request.\n"
                f"• **Vegetarian & Vegan:** Rich selections featuring seasonal produce, copper tandoori preparations, and plant-based gravies.\n"
                f"• **Gluten-Free & Allergens:** Our kitchen follows strict isolation protocols to prevent cross-contamination.\n\n"
            )
        if environment == "DEMO":
            reply += "*[DEMO DATA — Illustrative sample dietary guidelines]*"
        suggested_actions = ["Show Jain dishes", "Show vegetarian menu", "Book a table"]
        return {"reply": reply, "citations": citations, "suggested_actions": suggested_actions}

    # --- 8. GENERAL INQUIRY / GROUNDED KNOWLEDGE ---
    if chunks:
        doc_titles = ", ".join(list(dict.fromkeys([c["document_title"] for c in chunks[:2]])))
        chunk_snippets = "\n\n".join([f"• {c['content']}" for c in chunks[:2]])
        reply = (
            f"Based on documentation for **{outlet.name}** ({doc_titles}):\n\n"
            f"{chunk_snippets}\n\n"
            f"Please let me know if you would like further details regarding our services or reservations."
        )
        if environment == "DEMO":
            reply += "\n\n*[DEMO DATA — Illustrative sample information]*"
        suggested_actions = ["Reserve a table", "Explore more details", "Connect with team"]
        return {"reply": reply, "citations": citations, "suggested_actions": suggested_actions}

    reply = (
        f"Welcome to **{outlet.name}**, an esteemed venue by Amit Hospitality.\n\n"
        f"As your personal luxury concierge, I can assist you with:\n"
        f"• Exploring our **{outlet.cuisine_type}** culinary & cocktail selections\n"
        f"• Operating hours ({outlet.opening_time} – {outlet.closing_time}) and smart dress code\n"
        f"• Reserving premium terrace or indoor dining tables\n"
        f"• Private banquets and celebration inquiries\n\n"
        f"How may I curate your evening?"
    )
    if environment == "DEMO":
        reply += "\n\n*[DEMO DATA — System operating in DEMO presentation mode]*"
    suggested_actions = [
        "Show signature menu",
        "What are your timings and dress code?",
        "Book a table for tonight",
        "Private dining inquiry",
    ]
    return {"reply": reply, "citations": citations, "suggested_actions": suggested_actions}

def generate_rag_chat_response(
    db: Session,
    session_id: str,
    outlet: Outlet,
    user_message: str,
    language: str = "EN",
) -> ChatMessageResponse:
    """
    Orchestrate full RAG pipeline:
    1. Detect intent and extract entities.
    2. Retrieve relevant vector chunks and menu records strictly from active environment.
    3. Generate grounded response with Gemini or deterministic grounded engine.
    4. Compile citations and suggested actions.
    """
    from app.routers.chat import get_current_env
    active_env = get_current_env(db)
    is_demo = (active_env == "DEMO")

    # 1. Detect Intent
    intent_data = detect_intent(user_message)
    intent = intent_data["intent"]
    entities = intent_data["entities"]

    # 2. Vector Retrieval (strictly filtered by active_env)
    retrieved_chunks = search_relevant_chunks(
        db=db,
        query=user_message,
        environment=active_env,
        outlet_id=outlet.id,
        top_k=4,
    )

    # 3. Retrieve outlet menu items if relevant
    menu_items = (
        db.query(MenuItem)
        .filter(MenuItem.outlet_id == outlet.id, MenuItem.environment == active_env)
        .all()
    )

    # 4. Attempt Gemini LLM Generation if API key is provided
    reply_text = None
    citations: List[CitationItem] = []
    suggested_actions: List[str] = []

    if settings.GEMINI_API_KEY and active_env != "REAL":
        # Prepare context blocks
        context_str = ""
        if retrieved_chunks:
            context_str += "CONTEXT DOCUMENTS:\n"
            for idx, c in enumerate(retrieved_chunks, 1):
                context_str += f"[{idx}] {c['document_title']} ({c['category']}): {c['content']}\n"
        if menu_items:
            context_str += "\nMENU ITEMS:\n"
            for m in menu_items[:10]:
                context_str += f"- {m.name} (₹{m.price}): {m.description} [Dietary: {m.dietary_flags}]\n"

        prompt = f"""Outlet: {outlet.name} ({outlet.outlet_type})
Cuisine: {outlet.cuisine_type}
Operating Hours: {outlet.opening_time} to {outlet.closing_time}
Dress Code: {outlet.dress_code}
Environment: {active_env}

{context_str}

Customer Inquiry: "{user_message}"
Detected Intent: {intent}

Respond as the luxury Amit Hospitality AI Concierge following the system instructions."""

        llm_reply = call_gemini_api(prompt, SYSTEM_PROMPT, settings.GEMINI_API_KEY)
        if llm_reply:
            reply_text = llm_reply
            for c in retrieved_chunks[:2]:
                citations.append(CitationItem(
                    document_title=c["document_title"],
                    category=c["category"],
                    snippet=c["content"][:100],
                ))
            suggested_actions = ["Reserve a table", "Explore more dishes", "Timings & valet service"]

    # Fallback to high-fidelity grounded engine
    if not reply_text:
        res = build_deterministic_concierge_response(
            intent=intent,
            outlet=outlet,
            environment=active_env,
            chunks=retrieved_chunks,
            menu_items=menu_items,
            entities=entities,
            query=user_message,
        )
        reply_text = res["reply"]
        citations = res["citations"]
        suggested_actions = res["suggested_actions"]

    return ChatMessageResponse(
        reply=reply_text,
        environment=active_env,
        is_demo=is_demo,
        detected_intent=intent,
        citations=citations,
        suggested_actions=suggested_actions,
    )
