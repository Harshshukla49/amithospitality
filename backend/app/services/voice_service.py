import time
import json
import base64
import hmac
import hashlib
import logging
import urllib.request
import urllib.error
from typing import Optional, Dict, Any

from app.config import settings

logger = logging.getLogger("voice_service")

class TwilioVoiceService:
    """
    Production Twilio Telephony & Voice AI Service.
    Handles TwiML generation, speech-to-text dialogue flow,
    signature verification, call transfer, and connection verification.
    """

    @property
    def is_configured(self) -> bool:
        return bool(
            settings.TWILIO_ACCOUNT_SID
            and settings.TWILIO_AUTH_TOKEN
            and settings.TWILIO_PHONE_NUMBER
            and len(settings.TWILIO_ACCOUNT_SID.strip()) > 10
            and not settings.TWILIO_ACCOUNT_SID.startswith("your_")
        )

    def verify_twilio_signature(
        self,
        full_url: str,
        post_params: Dict[str, str],
        signature: Optional[str],
        auth_token: Optional[str] = None,
    ) -> bool:
        """
        Validate Twilio X-Twilio-Signature using HMAC-SHA1.
        """
        active_token = auth_token or settings.TWILIO_AUTH_TOKEN
        if not active_token:
            return True

        if not signature:
            return False

        # Sort parameters alphabetically and concatenate key+value
        data_string = full_url
        for k in sorted(post_params.keys()):
            data_string += f"{k}{post_params[k]}"

        computed_sig = base64.b64encode(
            hmac.new(
                active_token.encode("utf-8"),
                data_string.encode("utf-8"),
                hashlib.sha1,
            ).digest()
        ).decode("utf-8").strip()

        return hmac.compare_digest(signature.strip(), computed_sig)

    def build_welcome_twiml(self, language: str = "en-IN") -> str:
        """
        Generate initial TwiML welcoming incoming phone caller.
        """
        esc_number = settings.ESCALATION_PHONE_NUMBER or "+911140509900"
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech" action="/api/v1/voice/interact" language="en-IN" speechTimeout="auto" timeout="4">
        <Say voice="Polly.Aditi" language="en-IN">Namaste, and welcome to Amit Hospitality Concierge. How may I assist with your table reservation or dining plans today?</Say>
    </Gather>
    <Say voice="Polly.Aditi" language="en-IN">We did not catch your question. Please stay on the line to connect with our front desk, or visit Amit Hospitality dot com.</Say>
    <Dial>{esc_number}</Dial>
</Response>"""

    def build_interaction_twiml(self, speech_text: str, is_hindi: bool = False) -> str:
        """
        Process speech transcript and generate conversational TwiML response.
        """
        esc_number = settings.ESCALATION_PHONE_NUMBER or "+911140509900"
        lower = speech_text.lower()

        # 1. Human Escalation Intent
        if any(w in lower for w in ["human", "manager", "operator", "speak to someone", "front desk", "agent"]):
            return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Aditi" language="en-IN">Connecting you with our Senior Guest Relations Concierge right away. Please hold.</Say>
    <Dial>{esc_number}</Dial>
</Response>"""

        # 2. Table Reservation Intent
        if any(w in lower for w in ["reserve", "reservation", "book", "table", "dinner", "lunch"]):
            return """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Aditi" language="en-IN">I would be delighted to assist with your dining reservation at Amit Hospitality. We curate Amber Terrace Rooftop and Saffron and Silk Fine Dining. I have dispatched our reservation portal link to your phone number.</Say>
    <Gather input="speech" action="/api/v1/voice/interact" language="en-IN" speechTimeout="auto" timeout="3">
        <Say voice="Polly.Aditi" language="en-IN">Would you like me to check table availability for this evening?</Say>
    </Gather>
    <Say voice="Polly.Aditi" language="en-IN">Thank you for calling Amit Hospitality. We look forward to hosting you soon.</Say>
</Response>"""

        # 3. Timings & Policies
        if any(w in lower for w in ["time", "hours", "open", "close", "dress code", "valet"]):
            return """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Aditi" language="en-IN">Our rooftop lounge, Amber Terrace, welcomes guests from 5 PM until 1 AM with smart evening attire. Complimentary valet parking is available at the main porch.</Say>
    <Gather input="speech" action="/api/v1/voice/interact" language="en-IN" speechTimeout="auto" timeout="3">
        <Say voice="Polly.Aditi" language="en-IN">May I assist you with anything else today?</Say>
    </Gather>
    <Say voice="Polly.Aditi" language="en-IN">Have a wonderful day, and thank you for calling Amit Hospitality.</Say>
</Response>"""

        # 4. Default Concierge Dialogue
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Aditi" language="en-IN">At Amit Hospitality, we take pride in curating exceptional dining experiences. Regarding your inquiry, our masterchefs offer authentic seasonal menus and private dining.</Say>
    <Gather input="speech" action="/api/v1/voice/interact" language="en-IN" speechTimeout="auto" timeout="3">
        <Say voice="Polly.Aditi" language="en-IN">Would you like to reserve a table or speak with our concierge desk?</Say>
    </Gather>
    <Say voice="Polly.Aditi" language="en-IN">Thank you for contacting Amit Hospitality. Goodbye.</Say>
</Response>"""

    def test_connection(self) -> Dict[str, Any]:
        """
        Verify live connection against Twilio REST API.
        Never fabricates connection state.
        """
        if not self.is_configured:
            return {
                "name": "Twilio Telephony & Voice AI",
                "status": "NOT CONFIGURED",
                "connected": False,
                "error": "TWILIO_ACCOUNT_SID, AUTH_TOKEN, or PHONE_NUMBER missing.",
                "action_required": "Provide Twilio Cloud credentials.",
            }

        start_t = time.time()
        url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}.json"

        # Basic Auth
        auth_str = f"{settings.TWILIO_ACCOUNT_SID}:{settings.TWILIO_AUTH_TOKEN}"
        encoded_auth = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")

        try:
            req = urllib.request.Request(
                url,
                headers={"Authorization": f"Basic {encoded_auth}"},
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=8) as response:
                latency = round((time.time() - start_t) * 1000, 1)
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    account_name = data.get("friendly_name", "Amit Hospitality Twilio")
                    account_status = data.get("status", "active")
                    return {
                        "name": "Twilio Telephony & Voice AI",
                        "status": "CONNECTED",
                        "connected": True,
                        "account_name": account_name,
                        "account_status": account_status,
                        "phone_number": settings.TWILIO_PHONE_NUMBER,
                        "latency_ms": latency,
                        "verified_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    }
                else:
                    return {
                        "name": "Twilio Telephony & Voice AI",
                        "status": "DISCONNECTED",
                        "connected": False,
                        "error": f"HTTP status {response.status}",
                    }
        except urllib.error.HTTPError as he:
            err = he.read().decode("utf-8", errors="ignore")
            return {
                "name": "Twilio Telephony & Voice AI",
                "status": "DISCONNECTED",
                "connected": False,
                "error": f"HTTP {he.code}: {err[:200]}",
            }
        except Exception as e:
            return {
                "name": "Twilio Telephony & Voice AI",
                "status": "DISCONNECTED",
                "connected": False,
                "error": str(e),
            }

voice_service = TwilioVoiceService()
