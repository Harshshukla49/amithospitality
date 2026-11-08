import time
import json
import hmac
import hashlib
import logging
import urllib.request
import urllib.error
from typing import Optional, Dict, Any, Set

from app.config import settings

logger = logging.getLogger("whatsapp_service")

class WhatsAppService:
    """
    Production Meta WhatsApp Business Cloud API Integration Service.
    Handles webhook signature verification, message dispatch, template messaging,
    deduplication, and connectivity diagnostics.
    """

    def __init__(self):
        self.processed_message_ids: Set[str] = set()

    @property
    def is_configured(self) -> bool:
        return bool(
            settings.WHATSAPP_TOKEN
            and settings.WHATSAPP_PHONE_NUMBER_ID
            and len(settings.WHATSAPP_TOKEN.strip()) > 10
            and not settings.WHATSAPP_TOKEN.startswith("your_")
        )

    def verify_webhook_signature(self, payload_bytes: bytes, signature_header: Optional[str], secret: Optional[str] = None) -> bool:
        """
        Verify Meta X-Hub-Signature-256 HMAC signature.
        """
        active_secret = secret or settings.WHATSAPP_APP_SECRET
        if not active_secret:
            # If app secret not configured, allow payload with warning
            return True

        if not signature_header or not signature_header.startswith("sha256="):
            return False

        expected_sig = signature_header.split("sha256=")[-1].strip()
        computed_sig = hmac.new(
            active_secret.encode("utf-8"),
            payload_bytes,
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(expected_sig, computed_sig)

    def verify_signature(self, payload_bytes: bytes, signature_header: Optional[str], secret: Optional[str] = None) -> bool:
        """Alias for verify_webhook_signature."""
        return self.verify_webhook_signature(payload_bytes, signature_header, secret=secret)

    def is_message_duplicate(self, message_id: str) -> bool:
        """Check if message has already been processed."""
        if not message_id:
            return False
        return message_id in self.processed_message_ids

    def record_processed_message(self, message_id: str):
        """Record processed message ID."""
        if message_id:
            self.processed_message_ids.add(message_id)
            if len(self.processed_message_ids) > 10000:
                self.processed_message_ids.clear()

    def is_duplicate_message(self, message_id: str) -> bool:
        """Prevent double processing of Meta webhook delivery retries."""
        if not message_id:
            return False
        if message_id in self.processed_message_ids:
            return True
        self.record_processed_message(message_id)
        return False

    def send_text_message(self, to_phone: str, text_body: str) -> Dict[str, Any]:
        """
        Dispatch outbound WhatsApp text message via Meta Graph API v20.0.
        """
        if not self.is_configured:
            logger.warning(f"WhatsApp API not configured. Outbound message to {to_phone} bypassed.")
            return {
                "success": False,
                "status": "NOT_CONFIGURED",
                "message": "Meta WhatsApp Cloud API credentials missing.",
            }

        clean_phone = to_phone.replace("+", "").replace(" ", "").replace("-", "")
        url = f"https://graph.facebook.com/v20.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_phone,
            "type": "text",
            "text": {"preview_url": False, "body": text_body},
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status in (200, 201):
                    res_json = json.loads(response.read().decode("utf-8"))
                    msg_id = res_json.get("messages", [{}])[0].get("id")
                    logger.info(f"WhatsApp message dispatched to {clean_phone} (wamid: {msg_id})")
                    return {"success": True, "status": "DELIVERED", "message_id": msg_id}
        except urllib.error.HTTPError as he:
            err = he.read().decode("utf-8", errors="ignore")
            logger.error(f"WhatsApp Cloud API Error HTTP {he.code}: {err}")
            return {"success": False, "status": "FAILED", "error": f"HTTP {he.code}: {err[:200]}"}
        except Exception as e:
            logger.error(f"WhatsApp Cloud API network failure: {e}")
            return {"success": False, "status": "FAILED", "error": str(e)}

        return {"success": False, "status": "FAILED"}

    def send_reservation_confirmation(
        self,
        to_phone: str,
        guest_name: str,
        reference_id: str,
        outlet_name: str,
        reservation_date: str,
        reservation_time: str,
        guest_count: int,
        is_demo: bool = False,
    ) -> Dict[str, Any]:
        """
        Format and send an official WhatsApp reservation request notice.
        """
        demo_header = "[DEMO MODE — NOT A REAL BOOKING]\n" if is_demo else ""
        msg = (
            f"{demo_header}*Amit Hospitality — Table Reservation Request Received*\n\n"
            f"Dear {guest_name},\n\n"
            f"We have registered your dining reservation request for *{outlet_name}*:\n"
            f"• *Reference ID:* {reference_id}\n"
            f"• *Date & Time:* {reservation_date} at {reservation_time}\n"
            f"• *Party Size:* {guest_count} guests\n"
            f"• *Status:* Under Review\n\n"
            f"Our Guest Relations team will review availability and contact you shortly.\n\n"
            f"Need to adjust your plans? Reply directly to this WhatsApp message or call {settings.HOTLINE_PHONE_NUMBER}."
        )
        return self.send_text_message(to_phone=to_phone, text_body=msg)

    def test_connection(self) -> Dict[str, Any]:
        """
        Verify live connection against Meta WhatsApp Business Cloud API.
        Never fabricates connection state.
        """
        if not self.is_configured:
            return {
                "name": "Meta WhatsApp Business Cloud API",
                "status": "NOT CONFIGURED",
                "connected": False,
                "error": "WHATSAPP_TOKEN or WHATSAPP_PHONE_NUMBER_ID is missing.",
                "action_required": "Provide Meta Cloud API access token and phone number ID.",
            }

        start_t = time.time()
        url = f"https://graph.facebook.com/v20.0/{settings.WHATSAPP_PHONE_NUMBER_ID}"

        try:
            req = urllib.request.Request(
                url,
                headers={"Authorization": f"Bearer {settings.WHATSAPP_TOKEN}"},
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=8) as response:
                latency = round((time.time() - start_t) * 1000, 1)
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    display_phone = data.get("display_phone_number", "Registered Number")
                    verified_name = data.get("verified_name", "Amit Hospitality")
                    return {
                        "name": "Meta WhatsApp Business Cloud API",
                        "status": "CONNECTED",
                        "connected": True,
                        "display_phone": display_phone,
                        "verified_name": verified_name,
                        "latency_ms": latency,
                        "verified_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    }
                else:
                    return {
                        "name": "Meta WhatsApp Business Cloud API",
                        "status": "DISCONNECTED",
                        "connected": False,
                        "error": f"HTTP status {response.status}",
                    }
        except urllib.error.HTTPError as he:
            err = he.read().decode("utf-8", errors="ignore")
            return {
                "name": "Meta WhatsApp Business Cloud API",
                "status": "DISCONNECTED",
                "connected": False,
                "error": f"HTTP {he.code}: {err[:200]}",
            }
        except Exception as e:
            return {
                "name": "Meta WhatsApp Business Cloud API",
                "status": "DISCONNECTED",
                "connected": False,
                "error": str(e),
            }

whatsapp_service = WhatsAppService()
