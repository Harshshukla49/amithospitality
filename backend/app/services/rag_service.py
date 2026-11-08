import os
import json
import logging
from typing import List, Dict, Any, Optional
import urllib.request
import urllib.error
from sqlalchemy.orm import Session

from app.config import settings
from app.models.outlet import Outlet, MenuItem
from app.models.knowledge import KnowledgeChunk, KnowledgeDocument
from app.schemas.chat import ChatMessageResponse, CitationItem
from app.services.intent_service import detect_intent
from app.services.embedding_service import search_relevant_chunks
from app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the sophisticated AI Hospitality Concierge representing Amit Hospitality (https://amithospitality.com/).
Amit Hospitality curates premier dining, rooftop lounge, and fine-dining experiences.

CRITICAL OPERATIONAL RULES:
1. STRICT ENVIRONMENT ISOLATION:
   - In DEMO MODE: You may share illustrative sample menus, pricing, and event packages, clearly marking fictional data as [DEMO DATA].
   - In REAL MODE: You MUST ONLY provide verified factual information from the retrieved verified company knowledge chunks.
   - If verified information is not available in REAL MODE, you MUST state that verified company records are not yet indexed for that question and offer to connect the guest with Amit Hospitality Guest Relations (guestrelations@amithospitality.com / +91 11 4050 9900). Never invent or hallucinate pricing, hours, or policies.
2. LUXURY TONE & HOSPITALITY DEMEANOR:
   - Warm, welcoming, respectful, polished, and attentive.
   - Address guests with refined hospitality terminology (e.g., "It is our utmost pleasure", "Allow me to assist with your dining arrangements").
3. MULTILINGUAL COURTESY:
   - If asked in Hindi or Hinglish or if language is set to 'HI', reply in gracious, refined Hindi/Hinglish (e.g., "Namaste, Amber Terrace me aapka swagat hai...").
4. ACCURACY FIRST:
   - Never quote prices unless grounded in the provided menu items or retrieved documents.
   - Never contradict restaurant operational hours or dress codes.
"""

def call_gemini_api(prompt: str, system_instruction: str, api_key: str) -> Optional[str]:
    """Invoke Google Gemini REST API using urllib."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": system_instruction}]},
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 600,
            "topP": 0.8,
        },
    }
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
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
    language: str = "EN",
) -> Dict[str, Any]:
    """
    High-fidelity deterministic concierge generation engine.
    Ensures 100% reliable, grounded hospitality responses in both English and Hindi/Hinglish.
    """
    lower = query.lower()
    is_hindi = (language == "HI") or any(w in lower for w in ["namaste", "aapka", "kripya", "karna", "hai", "shukriya", "kitna"])
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
        if is_hindi:
            reply = (
                f"[REAL MODE — VERIFIED INFORMATION REQUIRED]\n\n"
                f"**{outlet.name}** ke liye is vishay par abhi company dwara verified documents uplabdh nahi hain.\n\n"
                f"Amit Hospitality ke official standards ke anusaar hum unverified jaankari pradan nahi karte. "
                f"Kripya hamari Guest Relations team se seedhe sampark karein: **{settings.HOTLINE_EMAIL}** ya **{settings.HOTLINE_PHONE_NUMBER}**."
            )
            return {
                "reply": reply,
                "citations": [],
                "suggested_actions": ["Guest Relations se baat karein", "Event enquiry bhejein", "DEMO mode me sample dekhein"],
            }
        else:
            reply = (
                f"[REAL MODE — VERIFIED INFORMATION REQUIRED]\n\n"
                f"I do not currently have verified corporate documentation indexed regarding this specific inquiry for **{outlet.name}**.\n\n"
                f"To maintain strict operational authenticity, our AI Concierge does not present unverified information. "
                f"Please allow our Guest Relations team to assist you directly at **{settings.HOTLINE_EMAIL}** or **{settings.HOTLINE_PHONE_NUMBER}**."
            )
            return {
                "reply": reply,
                "citations": [],
                "suggested_actions": ["Connect with Guest Relations", "Submit event enquiry", "Switch to DEMO mode for sample data"],
            }

    # --- 1. HUMAN HANDOVER INTENT ---
    if intent == "HUMAN_HANDOVER":
        if is_hindi:
            reply = (
                f"Mujhe aapko **{outlet.name}** ke Guest Relations Desk se connect karne me khushi hogi.\n\n"
                f"Hamare duty manager ko priority notification bhej diya gaya hai. "
                f"Turant sahayata ke liye aap hamari concierge hotline par call kar sakte hain: **{settings.HOTLINE_PHONE_NUMBER}** ya email karein **{settings.HOTLINE_EMAIL}**."
            )
            suggested_actions = ["Concierge Desk par call karein", "Aaj ki table availability check karein"]
        else:
            reply = (
                f"I am pleased to connect you directly with our Guest Relations Desk at **{outlet.name}**.\n\n"
                f"A priority notification has been routed to our duty manager. "
                f"For immediate concierge assistance, you may also call our concierge hotline directly at **{settings.HOTLINE_PHONE_NUMBER}** or email **{settings.HOTLINE_EMAIL}**."
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
            if is_hindi:
                reply = (
                    f"**{outlet.name}** ke culinary selections me se:\n\n"
                    f"• **{item.name}** — **₹{item.price:,.2f}**{dietary_str}\n"
                    f"  *{item.description}*\n\n"
                )
                if len(matched_items) > 1:
                    reply += "Aap inhein bhi pasand kar sakte hain:\n"
                    for other in matched_items[1:3]:
                        reply += f"• **{other.name}** (₹{other.price:,.2f}) — *{other.description}*\n"
                if environment == "DEMO":
                    reply += "\n*[DEMO DATA — Demonstration ke liye fictional pricing]*"
                suggested_actions = ["Table reserve karein", "Beverage pairings dekhein", "Dietary options poochein"]
            else:
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
            if is_hindi:
                reply = (
                    f"**{outlet.name}** ke menu aur dishes ki jaankari:\n\n"
                    f"{chunk_body}\n"
                )
                if environment == "DEMO":
                    reply += "\n*[DEMO DATA — Demonstration ke liye sample menu]*"
                suggested_actions = ["Price range kya hai?", "Dinner table reserve karein", "Jain options hain?"]
            else:
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
            if is_hindi:
                reply = (
                    f"**{outlet.name}** ({outlet.cuisine_type}) ka curated culinary preview:\n\n"
                    f"{summary}\n"
                )
                if environment == "DEMO":
                    reply += "\n*[DEMO DATA — Fictional sample menu]*"
                suggested_actions = ["Vegetarian options hain?", "Table book karein", "Operating hours"]
            else:
                reply = (
                    f"Here is a curated culinary preview for **{outlet.name}** ({outlet.cuisine_type}):\n\n"
                    f"{summary}\n"
                )
                if environment == "DEMO":
                    reply += "\n*[DEMO DATA — Fictional sample menu]*"
                suggested_actions = ["Do you have vegetarian options?", "Book table for tonight", "Operating hours"]
        else:
            if is_hindi:
                reply = f"**{outlet.name}** ki team **{outlet.cuisine_type}** cuisines me mahir hai. Kripya apni pasand ya dietary zarooratein batayein."
                suggested_actions = ["Signature dishes dekhein", "Operating hours"]
            else:
                reply = f"Our culinary team at **{outlet.name}** specializes in **{outlet.cuisine_type}**. Please inform me of your taste preferences or dietary needs."
                suggested_actions = ["Show signature dishes", "Operating hours"]

        return {"reply": reply, "citations": citations, "suggested_actions": suggested_actions}

    # --- 3. TIMING & LOCATION INQUIRY ---
    if intent == "TIMING_LOCATION":
        if chunks:
            primary_chunk = chunks[0]["content"]
            if is_hindi:
                reply = f"**{outlet.name} ke Operating Timings & Location**:\n\n{primary_chunk}\n\n"
            else:
                reply = f"**Operating Schedule & Location Details for {outlet.name}**:\n\n{primary_chunk}\n\n"
        else:
            if is_hindi:
                reply = (
                    f"**{outlet.name}** ke timings aur location details:\n\n"
                    f"• **Operating Hours:** {outlet.opening_time} se {outlet.closing_time} (Rozana)\n"
                    f"• **Cuisine & Style:** {outlet.cuisine_type} ({outlet.outlet_type})\n"
                    f"• **Location:** {outlet.location}\n"
                    f"• **Dress Code:** {outlet.dress_code}\n"
                    f"• **Valet Parking:** Main portico par complimentary VIP valet parking uplabdh hai.\n\n"
                )
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
            if is_hindi:
                reply = (
                    f"**{outlet.name} ki Guest Policies**:\n\n"
                    f"• **Dress Code:** {outlet.dress_code}. Hum smart evening attire ki request karte hain.\n"
                    f"• **Reservations Policy:** Tables booking time se 15 minute tak hold ki jaati hain.\n"
                    f"• **Valet Service:** Sabre guests ke liye complimentary valet uplabdh hai.\n\n"
                )
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
        if is_hindi:
            reply = (
                f"**{outlet.name}** me table reservation request darj karne ke liye main aapki sahayata karta hoon.\n\n"
                f"Reservation request submit karne ke liye yeh jankari aavashyak hai:\n"
                f"• **Guest Name:** Aapka poora naam\n"
                f"• **Contact:** Phone number (7–15 digits) aur optional email\n"
                f"• **Date & Time:** Aane ki taareekh aur samay\n"
                f"• **Party Size:** Mehmano ki sankhya{guest_count_text}\n"
                f"• **Seating Preference:** Indoor, Al Fresco Terrace, ya Private Dining\n\n"
                f"*Kripya dhyan dein:* Request darj hone par aapko ek unique **Reference ID (REF-RES-...)** pradan ki jayegi. Hamare maître d' table review karne ke baad hi booking confirm karenge; request submit hona automatic table confirmation nahi hai.\n\n"
                f"Aap **'Reserve a Table'** button par click karke form turant submit kar sakte hain."
            )
            if environment == "DEMO":
                reply += "\n\n*[DEMO DATA — DEMO mode me reservation requests simulate ki jaati hain aur 'DEMO DATA' mark hoti hain]*"
            suggested_actions = ["Reserve a Table", "Seating options dekhein", "Check tonight's availability"]
        else:
            reply = (
                f"It will be my pleasure to assist with your table reservation request at **{outlet.name}**{guest_count_text}{time_text}.\n\n"
                f"To submit a reservation request, our maître d' requires:\n"
                f"• **Guest Name:** Full name\n"
                f"• **Contact:** Phone number (7–15 digits) and optional email\n"
                f"• **Date & Time:** Preferred date and reservation time\n"
                f"• **Party Size:** Number of guests\n"
                f"• **Seating Preference:** Indoor, Al Fresco Terrace, or Private Dining\n\n"
                f"*Please note:* Upon submission, you will receive a unique **Reference ID (REF-RES-...)**. All submissions are reservation requests awaiting host verification and allocation; this is not an automated table confirmation.\n\n"
                f"You may click **'Reserve a Table'** to open the reservation request form."
            )
            if environment == "DEMO":
                reply += "\n\n*[DEMO DATA — Reservation requests in DEMO mode are marked as simulated demo records]*"
            suggested_actions = ["Reserve a Table", "View seating options", "Check tonight's availability"]
        return {"reply": reply, "citations": citations, "suggested_actions": suggested_actions}

    # --- 6. EVENT & PRIVATE DINING INQUIRY ---
    if intent == "EVENT_INQUIRY":
        if is_hindi:
            reply = (
                f"**{outlet.name}** private events, birthday parties, corporate dinners aur landmark celebrations ke liye curated venue hai.\n\n"
                f"Hamari banquets team se customized proposal aur date booking ke liye yeh jankari zaroori hai:\n"
                f"• **Enquiry Type:** Private party, Corporate event, Birthday, Wedding, ya Group booking\n"
                f"• **Date & Size:** Target date aur anumanit mehmano ki sankhya (Up to {outlet.seating_capacity})\n"
                f"• **Contact Details:** Aapka naam, phone number aur official email\n"
                f"• **Requirements:** Custom menu, AV audio-visual, decor ya special vision\n\n"
                f"Inquiry submit karte hi aapko ek unique **Reference ID (REF-LEAD-...)** mil jayegi aur hamare Events Director aapse sampark karenge.\n\n"
                f"Aap **'Submit Event Inquiry'** button click karke proposal request bhej sakte hain."
            )
            if environment == "DEMO":
                reply += "\n\n*[DEMO DATA — Event lead submissions in DEMO mode are simulated]*"
            suggested_actions = ["Submit Event Inquiry", "Contact Events Director", "View banquet packages"]
        else:
            reply = (
                f"**{outlet.name}** provides distinguished settings for intimate private parties, executive corporate events, and wedding celebrations.\n\n"
                f"To initiate a bespoke event proposal, our Events Director requires:\n"
                f"• **Enquiry Type:** Private party, Corporate event, Birthday celebration, Wedding, or Group booking\n"
                f"• **Schedule & Scale:** Preferred date and estimated guest count (Up to {outlet.seating_capacity})\n"
                f"• **Contact Details:** Name, direct phone number, and email address\n"
                f"• **Vision:** Course preferences, AV setup, or entertainment requirements\n\n"
                f"Upon submission, you will be assigned a unique **Reference ID (REF-LEAD-...)** for direct follow-up with our banquets team.\n\n"
                f"Click **'Submit Event Inquiry'** to provide your specifications."
            )
            if environment == "DEMO":
                reply += "\n\n*[DEMO DATA — Event lead inquiries in DEMO mode are marked as simulated demo records]*"
            suggested_actions = ["Submit Event Inquiry", "Contact Events Director", "View banquet packages"]
        return {"reply": reply, "citations": citations, "suggested_actions": suggested_actions}

    # --- 7. DIETARY INQUIRY ---
    if intent == "DIETARY_INQUIRY":
        diet_str = ", ".join(entities.get("dietary", ["Special Dietary Accommodations"]))
        if chunks:
            reply = f"**Dietary Accommodations ({diet_str}) at {outlet.name}**:\n\n{chunks[0]['content']}\n\n"
        else:
            if is_hindi:
                reply = (
                    f"**{outlet.name}** me hamare masterchefs dietary requirements ka poora dhyan rakhte hain:\n\n"
                    f"• **Jain Dining:** Bina pyaaz, bina lehsun aur bina root vegetables ke customized fresh dishes taiyar ki jaati hain.\n"
                    f"• **Vegetarian & Vegan:** Rich seasonal produce aur special copper tandoori preparations uplabdh hain.\n"
                    f"• **Gluten-Free & Allergens:** Hamari kitchen me cross-contamination rokne ke liye strict isolation protocols follow kiye jaate hain.\n\n"
                )
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
        if is_hindi:
            reply = (
                f"**{outlet.name}** ke dastavezon ({doc_titles}) ke anusaar:\n\n"
                f"{chunk_snippets}\n\n"
                f"Kripya batayein agar aapko kisi anya suvidha ya booking ke baare me aur jaankari chahiye."
            )
        else:
            reply = (
                f"Based on documentation for **{outlet.name}** ({doc_titles}):\n\n"
                f"{chunk_snippets}\n\n"
                f"Please let me know if you would like further details regarding our services or reservations."
            )
        if environment == "DEMO":
            reply += "\n\n*[DEMO DATA — Illustrative sample information]*"
        suggested_actions = ["Reserve a table", "Explore more details", "Connect with team"]
        return {"reply": reply, "citations": citations, "suggested_actions": suggested_actions}

    if is_hindi:
        reply = (
            f"Namaste! Amit Hospitality ke **{outlet.name}** me aapka hardik swagat hai.\n\n"
            f"Main aapka personal AI Concierge hoon. Main in vishayon par aapki sahayata kar sakta hoon:\n"
            f"• Hamare **{outlet.cuisine_type}** culinary aur cocktail menu ki jankari\n"
            f"• Operating hours ({outlet.opening_time} – {outlet.closing_time}) aur dress code\n"
            f"• Dining tables aur rooftop terrace booking\n"
            f"• Private banquets aur celebrations arrangements\n\n"
            f"Aapko kis tarah ki sahayata chahiye?"
        )
    else:
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

    # 4. Attempt Gemini LLM Generation if API key is provided and conditions met
    reply_text = None
    citations: List[CitationItem] = []
    suggested_actions: List[str] = []

    # In REAL mode, only call Gemini if verified chunks or verified menu items exist; otherwise enforce zero-hallucination guard
    can_call_gemini = gemini_service.is_configured and (active_env == "DEMO" or bool(retrieved_chunks or menu_items))

    if can_call_gemini:
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

        lang_instruction = "Respond in polite Hindi/Hinglish." if language == "HI" else "Respond in English."
        prompt = f"""Outlet: {outlet.name} ({outlet.outlet_type})
Cuisine: {outlet.cuisine_type}
Operating Hours: {outlet.opening_time} to {outlet.closing_time}
Dress Code: {outlet.dress_code}
Environment: {active_env}
Language: {lang_instruction}

{context_str}

Customer Inquiry: "{user_message}"
Detected Intent: {intent}

Respond as the luxury Amit Hospitality AI Concierge following the system instructions."""

        llm_result = gemini_service.generate_grounded_response(
            prompt=prompt,
            system_instruction=SYSTEM_PROMPT,
            environment=active_env,
        )
        if llm_result and llm_result.get("reply"):
            reply_text = llm_result["reply"]
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
            language=language,
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
