import re
from typing import Dict, Any, List

INTENT_PRIORITY_WEIGHTS = {
    "HUMAN_HANDOVER": 3.0,
    "RESERVATION_REQUEST": 2.5,
    "EVENT_INQUIRY": 2.0,
    "DIETARY_INQUIRY": 2.2,
    "PRICING_INQUIRY": 2.0,
    "POLICY_INQUIRY": 1.8,
    "TIMING_LOCATION": 1.8,
    "MENU_INQUIRY": 1.2,
    "GENERAL_INQUIRY": 1.0,
}

INTENT_PATTERNS = {
    "HUMAN_HANDOVER": [
        r"\b(connect|speak|talk|call)\b.*\b(human|agent|manager|desk|person|staff|team|representative)\b",
        r"\b(human support|customer care|receptionist|operator)\b",
        r"\b(complaint|escalate|escalation)\b",
    ],
    "RESERVATION_REQUEST": [
        r"\b(book|reserve|reservation|table)\b.*\b(tonight|tomorrow|table|seats|dinner|lunch|evening)\b",
        r"\b(i want to book|need a table|reserve a table|make a reservation)\b",
        r"\b(seating capacity|table for \d+|party of \d+)\b",
    ],
    "EVENT_INQUIRY": [
        r"\b(private dining|private party|banquet|wedding|corporate event|buyout|anniversary|birthday celebration|conference)\b",
        r"\b(hall|lawn|private room|celebrate|gala dinner|cocktail reception)\b",
    ],
    "DIETARY_INQUIRY": [
        r"\b(jain|vegetarian|vegan|halal|gluten[- ]?free|nut[- ]?free|dairy[- ]?free|allergy|allergies|pure veg|dietary)\b",
        r"\b(without|no)\s+(onion|garlic|meat|egg|dairy)\b",
        r"\bjain food|jain menu|jain preparations\b",
    ],
    "PRICING_INQUIRY": [
        r"\b(price|pricing|cost|how much|rate|charge|bill|expensive|cheap|inexpensive)\b",
        r"\bhow much is\b",
        r"\bwhat is the price of\b",
    ],
    "MENU_INQUIRY": [
        r"\b(menu|dishes|speciality|specialties|food|beverage|cocktail|wine|signature dish|culinary|starters|desserts|mains)\b",
        r"\bwhat do you serve\b",
        r"\bshow me the menu\b",
        r"\brecommend\b.*\b(dish|food|drink|starter)\b",
    ],
    "TIMING_LOCATION": [
        r"\b(timing|timings|hours|opening|closing|open today|close today|when do you open|when do you close)\b",
        r"\b(where are you located|address|directions|how to reach|location|map)\b",
        r"\b(valet|parking|car parking)\b",
    ],
    "POLICY_INQUIRY": [
        r"\b(dress code|dresscode|attire|formal|casual|shoes|slippers|shorts|tank tops)\b",
        r"\b(cancellation policy|kids allowed|children allowed|age limit|smoking policy|corkage)\b",
        r"\b(policy|policies|guidelines|regulations|standards|charter|rules|sustainability|esg)\b",
    ],
}

def detect_intent(text: str) -> Dict[str, Any]:
    """
    Detect user intent and extract contextual entities from query text.
    Uses pattern matching weighted by intent specificity.
    """
    cleaned = text.strip().lower()
    
    detected_intent = "GENERAL_INQUIRY"
    highest_score = 0.0

    for intent, patterns in INTENT_PATTERNS.items():
        matches = 0
        for pattern in patterns:
            if re.search(pattern, cleaned, re.IGNORECASE):
                matches += 1
        
        weighted_score = matches * INTENT_PRIORITY_WEIGHTS.get(intent, 1.0)
        if weighted_score > highest_score:
            highest_score = weighted_score
            detected_intent = intent

    # Extract Entities
    entities: Dict[str, Any] = {}

    # Guest count extraction
    guest_match = re.search(r'\b(?:table for|party of|for)\s+(\d{1,2})\b|\b(\d{1,2})\s+(?:guests|people|persons|pax)\b', cleaned)
    if guest_match:
        entities["guest_count"] = int(guest_match.group(1) or guest_match.group(2))

    # Dietary extraction
    dietary_flags: List[str] = []
    if "jain" in cleaned or "no onion" in cleaned or "without onion" in cleaned:
        dietary_flags.append("JAIN")
    if "vegan" in cleaned:
        dietary_flags.append("VEGAN")
    elif "vegetarian" in cleaned or "veg" in cleaned:
        dietary_flags.append("VEG")
    if "gluten" in cleaned:
        dietary_flags.append("GLUTEN_FREE")
    if dietary_flags:
        entities["dietary"] = dietary_flags

    # Time extraction
    time_match = re.search(r'\b(?:at\s+)?(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)\b', cleaned)
    if time_match:
        entities["time"] = time_match.group(1)

    return {
        "intent": detected_intent,
        "confidence": 0.95 if highest_score > 0 else 0.60,
        "entities": entities,
    }
