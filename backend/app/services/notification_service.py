import time
import json
import base64
import logging
import smtplib
import html
import re
import urllib.request
import urllib.error
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any, Set

from app.config import settings

logger = logging.getLogger("notification_service")

class NotificationService:
    """
    Production Email and SMS Transactional Communication Service.
    Supports SendGrid & standard SMTP for email, and Twilio for SMS.
    Provides branded HTML templates, deduplication, and connectivity verification.
    """

    @staticmethod
    def sanitize_html(text: Optional[str]) -> str:
        """
        Strip script tags, event handlers, and escape HTML entities
        to prevent stored and reflective XSS in email templates.
        """
        if not text:
            return ""
        # Strip script and dangerous executable tags
        cleaned = re.sub(r"<\s*(script|iframe|object|embed|style|meta)[^>]*>.*?<\s*/\s*\1\s*>", "", str(text), flags=re.IGNORECASE | re.DOTALL)
        cleaned = re.sub(r"<\s*(script|iframe|object|embed|style|meta|input|form|img|svg|audio|video|link)[^>]*>", "", cleaned, flags=re.IGNORECASE)
        # Strip inline event handlers like onerror=, onclick=, onload=, etc.
        cleaned = re.sub(r"\bon\w+\s*=\s*(?:'[^']*'|\"[^\"]*\"|[^\s>]+)", "", cleaned, flags=re.IGNORECASE)
        # Escape all remaining special HTML characters
        return html.escape(cleaned.strip())

    def __init__(self):
        # In-memory deduplication set: {idempotency_key: timestamp}
        self._sent_idempotency_keys: Dict[str, float] = {}

    @property
    def is_email_configured(self) -> bool:
        if settings.SENDGRID_API_KEY and len(settings.SENDGRID_API_KEY.strip()) > 15 and not settings.SENDGRID_API_KEY.startswith("your_"):
            return True
        if settings.SMTP_HOST and settings.SMTP_USER and settings.SMTP_PASSWORD and not settings.SMTP_HOST.startswith("your_"):
            return True
        return False

    @property
    def is_sms_configured(self) -> bool:
        return bool(
            settings.TWILIO_ACCOUNT_SID
            and settings.TWILIO_AUTH_TOKEN
            and settings.TWILIO_PHONE_NUMBER
            and len(settings.TWILIO_ACCOUNT_SID.strip()) > 10
            and not settings.TWILIO_ACCOUNT_SID.startswith("your_")
        )

    def _clean_old_idempotency_keys(self):
        now = time.time()
        expired = [k for k, t in self._sent_idempotency_keys.items() if now - t > 3600]
        for k in expired:
            del self._sent_idempotency_keys[k]

    def is_duplicate(self, idempotency_key: Optional[str]) -> bool:
        if not idempotency_key:
            return False
        self._clean_old_idempotency_keys()
        return idempotency_key in self._sent_idempotency_keys

    def record_sent_key(self, idempotency_key: Optional[str]):
        if idempotency_key:
            self._clean_old_idempotency_keys()
            self._sent_idempotency_keys[idempotency_key] = time.time()

    # ==========================================
    # EMAIL DISPATCH (SENDGRID / SMTP)
    # ==========================================

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send transactional email via SendGrid API or SMTP fallback.
        """
        if self.is_duplicate(idempotency_key):
            logger.info(f"Duplicate email suppressed for key: {idempotency_key}")
            return {"sent": True, "deduplicated": True, "message": "Email already sent previously (idempotent)"}

        if not self.is_email_configured:
            logger.warning("Email dispatch skipped: Email credentials not configured.")
            return {
                "sent": False,
                "status": "NOT CONFIGURED",
                "error": "SENDGRID_API_KEY or SMTP credentials missing in environment",
            }

        if settings.SENDGRID_API_KEY and len(settings.SENDGRID_API_KEY.strip()) > 15 and not settings.SENDGRID_API_KEY.startswith("your_"):
            return self._send_sendgrid(to_email, subject, html_content, text_content, idempotency_key)
        else:
            return self._send_smtp(to_email, subject, html_content, text_content, idempotency_key)

    def _send_sendgrid(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str],
        idempotency_key: Optional[str],
    ) -> Dict[str, Any]:
        start_t = time.time()
        url = "https://api.sendgrid.com/v3/mail/send"
        headers = {
            "Authorization": f"Bearer {settings.SENDGRID_API_KEY.strip()}",
            "Content-Type": "application/json",
        }
        body = {
            "personalizations": [{"to": [{"email": to_email}]}],
            "from": {"email": settings.SMTP_FROM_EMAIL or "concierge@amithospitality.com", "name": "Amit Hospitality Concierge"},
            "subject": subject,
            "content": [
                {"type": "text/html", "value": html_content}
            ],
        }
        if text_content:
            body["content"].insert(0, {"type": "text/plain", "value": text_content})

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(body).encode("utf-8"),
                headers=headers,
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                duration_ms = round((time.time() - start_t) * 1000, 1)
                if response.status in (200, 202):
                    self.record_sent_key(idempotency_key)
                    logger.info(f"Email sent via SendGrid to {to_email} in {duration_ms}ms")
                    return {"sent": True, "provider": "SendGrid", "latency_ms": duration_ms}
                else:
                    return {"sent": False, "status": "ERROR", "error": f"HTTP {response.status}"}
        except urllib.error.HTTPError as he:
            err = he.read().decode("utf-8", errors="ignore")
            logger.error(f"SendGrid API HTTP error: {he.code} {err}")
            return {"sent": False, "status": "ERROR", "error": f"HTTP {he.code}: {err[:200]}"}
        except Exception as e:
            logger.error(f"SendGrid API error: {str(e)}")
            return {"sent": False, "status": "ERROR", "error": str(e)}

    def _send_smtp(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str],
        idempotency_key: Optional[str],
    ) -> Dict[str, Any]:
        start_t = time.time()
        from_addr = settings.SMTP_FROM_EMAIL or "concierge@amithospitality.com"
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"Amit Hospitality Concierge <{from_addr}>"
        msg["To"] = to_email

        if text_content:
            msg.attach(MIMEText(text_content, "plain"))
        msg.attach(MIMEText(html_content, "html"))

        try:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
                server.ehlo()
                if server.has_extn("STARTTLS"):
                    server.starttls()
                    server.ehlo()
                if settings.SMTP_USER and settings.SMTP_PASSWORD:
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(from_addr, [to_email], msg.as_string())

            duration_ms = round((time.time() - start_t) * 1000, 1)
            self.record_sent_key(idempotency_key)
            logger.info(f"Email sent via SMTP to {to_email} in {duration_ms}ms")
            return {"sent": True, "provider": "SMTP", "latency_ms": duration_ms}
        except Exception as e:
            logger.error(f"SMTP send error: {str(e)}")
            return {"sent": False, "status": "ERROR", "error": str(e)}

    # ==========================================
    # SMS DISPATCH (TWILIO)
    # ==========================================

    def send_sms(
        self,
        to_phone: str,
        message_text: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send transactional SMS via Twilio Messages API.
        """
        if self.is_duplicate(idempotency_key):
            logger.info(f"Duplicate SMS suppressed for key: {idempotency_key}")
            return {"sent": True, "deduplicated": True, "message": "SMS already sent previously (idempotent)"}

        if not self.is_sms_configured:
            logger.warning("SMS dispatch skipped: Twilio credentials not configured.")
            return {
                "sent": False,
                "status": "NOT CONFIGURED",
                "error": "TWILIO_ACCOUNT_SID, AUTH_TOKEN, or PHONE_NUMBER missing in environment",
            }

        start_t = time.time()
        url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}/Messages.json"
        auth_str = f"{settings.TWILIO_ACCOUNT_SID}:{settings.TWILIO_AUTH_TOKEN}"
        encoded_auth = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")

        post_fields = {
            "To": to_phone,
            "From": settings.TWILIO_PHONE_NUMBER,
            "Body": message_text,
        }
        encoded_data = urllib.parse.urlencode(post_fields).encode("utf-8")

        try:
            req = urllib.request.Request(
                url,
                data=encoded_data,
                headers={"Authorization": f"Basic {encoded_auth}", "Content-Type": "application/x-www-form-urlencoded"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                duration_ms = round((time.time() - start_t) * 1000, 1)
                res_body = json.loads(response.read().decode("utf-8"))
                sid = res_body.get("sid", "unknown")
                self.record_sent_key(idempotency_key)
                logger.info(f"SMS sent via Twilio to {to_phone} (Sid: {sid}) in {duration_ms}ms")
                return {"sent": True, "provider": "Twilio SMS", "sid": sid, "latency_ms": duration_ms}
        except urllib.error.HTTPError as he:
            err = he.read().decode("utf-8", errors="ignore")
            logger.error(f"Twilio SMS HTTP error: {he.code} {err}")
            return {"sent": False, "status": "ERROR", "error": f"HTTP {he.code}: {err[:200]}"}
        except Exception as e:
            logger.error(f"Twilio SMS error: {str(e)}")
            return {"sent": False, "status": "ERROR", "error": str(e)}

    # ==========================================
    # HTML EMAIL TEMPLATES
    # ==========================================

    def build_reservation_request_email(
        self,
        ref_id: str,
        guest_name: str,
        outlet_name: str,
        date_str: str,
        time_str: str,
        guests_count: int,
        is_demo: bool = True,
    ) -> str:
        s_ref_id = self.sanitize_html(ref_id)
        s_guest_name = self.sanitize_html(guest_name)
        s_outlet_name = self.sanitize_html(outlet_name)
        s_date_str = self.sanitize_html(date_str)
        s_time_str = self.sanitize_html(time_str)

        demo_banner = """
        <div style="background-color: #fef3c7; border: 1px solid #f59e0b; color: #92400e; padding: 12px; border-radius: 8px; margin-bottom: 20px; font-weight: bold; text-align: center;">
            ⚠️ DEMO SIMULATION NOTICE — This is an automated demonstration booking request. No actual restaurant reservation has been secured.
        </div>
        """ if is_demo else ""

        return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 24px;">
    <div style="max-width: 600px; margin: 0 auto; background-color: #1e293b; border-radius: 12px; border: 1px solid #334155; padding: 32px;">
        {demo_banner}
        <div style="text-align: center; border-bottom: 1px solid #334155; padding-bottom: 20px; margin-bottom: 24px;">
            <h1 style="color: #f59e0b; margin: 0; font-size: 24px; letter-spacing: 1px;">AMIT HOSPITALITY</h1>
            <p style="color: #94a3b8; margin: 4px 0 0; font-size: 14px;">Luxury Dining & Bespoke Experiences</p>
        </div>

        <h2 style="color: #f8fafc; font-size: 20px; margin-top: 0;">Reservation Request Received</h2>
        <p style="color: #cbd5e1; font-size: 15px; line-height: 1.6;">
            Dear <strong>{s_guest_name}</strong>,<br>
            Thank you for choosing Amit Hospitality. We have received your reservation inquiry and our Concierge team is currently reviewing availability.
        </p>

        <div style="background-color: #0f172a; border-radius: 8px; padding: 20px; margin: 24px 0; border: 1px solid #334155;">
            <table style="width: 100%; border-collapse: collapse; font-size: 14px; color: #cbd5e1;">
                <tr><td style="padding: 6px 0; color: #94a3b8;">Reference ID:</td><td style="font-family: monospace; font-weight: bold; color: #f59e0b;">{s_ref_id}</td></tr>
                <tr><td style="padding: 6px 0; color: #94a3b8;">Outlet:</td><td style="font-weight: bold; color: #ffffff;">{s_outlet_name}</td></tr>
                <tr><td style="padding: 6px 0; color: #94a3b8;">Date:</td><td>{s_date_str}</td></tr>
                <tr><td style="padding: 6px 0; color: #94a3b8;">Preferred Time:</td><td>{s_time_str}</td></tr>
                <tr><td style="padding: 6px 0; color: #94a3b8;">Party Size:</td><td>{guests_count} Guests</td></tr>
                <tr><td style="padding: 6px 0; color: #94a3b8;">Status:</td><td><span style="background: #eab308; color: #000; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 12px;">PENDING REVIEW</span></td></tr>
            </table>
        </div>

        <p style="color: #94a3b8; font-size: 13px; line-height: 1.5;">
            *Please note that this acknowledgment is a request confirmation, not an immediate table allocation. Our restaurant coordinator will contact you via WhatsApp/Email once availability is confirmed.
        </p>

        <div style="border-top: 1px solid #334155; margin-top: 32px; padding-top: 20px; text-align: center; color: #64748b; font-size: 12px;">
            Amit Hospitality Concierge • New Delhi, India<br>
            Direct: {settings.HOTLINE_PHONE_NUMBER} • Web: <a href="https://amithospitality.com" style="color: #f59e0b; text-decoration: none;">amithospitality.com</a>
        </div>
    </div>
</body>
</html>"""

    def build_reservation_status_email(
        self,
        ref_id: str,
        guest_name: str,
        outlet_name: str,
        status: str,
        notes: Optional[str] = None,
        is_demo: bool = True,
    ) -> str:
        s_ref_id = self.sanitize_html(ref_id)
        s_guest_name = self.sanitize_html(guest_name)
        s_outlet_name = self.sanitize_html(outlet_name)
        s_status = self.sanitize_html(status)
        s_notes = self.sanitize_html(notes) if notes else ""

        status_color = "#10b981" if status.lower() == "accepted" else "#ef4444"
        return f"""<!DOCTYPE html>
<html>
<body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 24px;">
    <div style="max-width: 600px; margin: 0 auto; background-color: #1e293b; border-radius: 12px; border: 1px solid #334155; padding: 32px;">
        <div style="text-align: center; border-bottom: 1px solid #334155; padding-bottom: 20px; margin-bottom: 24px;">
            <h1 style="color: #f59e0b; margin: 0; font-size: 24px; letter-spacing: 1px;">AMIT HOSPITALITY</h1>
            <p style="color: #94a3b8; margin: 4px 0 0; font-size: 14px;">Luxury Dining & Bespoke Experiences</p>
        </div>
        <h2 style="color: #f8fafc; font-size: 20px;">Reservation Update: <span style="color: {status_color};">{s_status.upper()}</span></h2>
        <p style="color: #cbd5e1; font-size: 15px;">
            Dear {s_guest_name},<br>
            Your dining request <strong>{s_ref_id}</strong> at <strong>{s_outlet_name}</strong> has been updated to: <strong>{s_status.upper()}</strong>.
        </p>
        {f'<div style="background:#0f172a; padding:12px; border-radius:6px; margin:16px 0; color:#e2e8f0; font-size:14px;"><strong>Staff Note:</strong> {s_notes}</div>' if s_notes else ''}
        <p style="color: #94a3b8; font-size: 13px;">For inquiries or changes, please call our Concierge at {settings.HOTLINE_PHONE_NUMBER}.</p>
    </div>
</body>
</html>"""

    def build_lead_acknowledgement_email(
        self,
        lead_id: str,
        guest_name: str,
        event_type: str,
        outlet_name: str,
        is_demo: bool = True,
    ) -> str:
        s_lead_id = self.sanitize_html(lead_id)
        s_guest_name = self.sanitize_html(guest_name)
        s_event_type = self.sanitize_html(event_type)
        s_outlet_name = self.sanitize_html(outlet_name)

        return f"""<!DOCTYPE html>
<html>
<body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 24px;">
    <div style="max-width: 600px; margin: 0 auto; background-color: #1e293b; border-radius: 12px; border: 1px solid #334155; padding: 32px;">
        <h2 style="color: #f59e0b; font-size: 20px;">Event & Banquet Inquiry Received</h2>
        <p style="color: #cbd5e1; font-size: 15px;">
            Dear {s_guest_name},<br>
            Thank you for considering Amit Hospitality for your upcoming {s_event_type} at {s_outlet_name}.
            Our Private Events & Catering Manager has been assigned to your request (Ref: #{s_lead_id}) and will prepare a tailored proposal within 24 business hours.
        </p>
    </div>
</body>
</html>"""

    # ==========================================
    # CONNECTIVITY AUDIT
    # ==========================================

    def test_email_connection(self) -> Dict[str, Any]:
        """
        Test live email connectivity against SendGrid or SMTP without sending mail.
        """
        if not self.is_email_configured:
            return {
                "name": "Transactional Email (SendGrid/SMTP)",
                "status": "NOT CONFIGURED",
                "connected": False,
                "error": "SENDGRID_API_KEY or SMTP credentials missing in environment",
                "action_required": "Provide SENDGRID_API_KEY or configure SMTP_HOST/USER/PASSWORD.",
            }

        start_t = time.time()
        # Test SendGrid
        if settings.SENDGRID_API_KEY and len(settings.SENDGRID_API_KEY.strip()) > 15 and not settings.SENDGRID_API_KEY.startswith("your_"):
            try:
                # Query SendGrid user profile or scopes endpoint to verify token
                url = "https://api.sendgrid.com/v3/scopes"
                req = urllib.request.Request(
                    url,
                    headers={"Authorization": f"Bearer {settings.SENDGRID_API_KEY.strip()}"},
                    method="GET",
                )
                with urllib.request.urlopen(req, timeout=8) as response:
                    latency = round((time.time() - start_t) * 1000, 1)
                    if response.status == 200:
                        return {
                            "name": "Transactional Email (SendGrid)",
                            "status": "CONNECTED",
                            "connected": True,
                            "provider": "SendGrid",
                            "sender_email": settings.SMTP_FROM_EMAIL,
                            "latency_ms": latency,
                            "verified_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        }
                    else:
                        return {"name": "Transactional Email (SendGrid)", "status": "DISCONNECTED", "connected": False, "error": f"HTTP {response.status}"}
            except urllib.error.HTTPError as he:
                err = he.read().decode("utf-8", errors="ignore")
                return {"name": "Transactional Email (SendGrid)", "status": "DISCONNECTED", "connected": False, "error": f"HTTP {he.code}: {err[:200]}"}
            except Exception as e:
                return {"name": "Transactional Email (SendGrid)", "status": "DISCONNECTED", "connected": False, "error": str(e)}

        # Test SMTP
        try:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=8) as server:
                server.ehlo()
                if server.has_extn("STARTTLS"):
                    server.starttls()
                    server.ehlo()
                if settings.SMTP_USER and settings.SMTP_PASSWORD:
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            latency = round((time.time() - start_t) * 1000, 1)
            return {
                "name": "Transactional Email (SMTP)",
                "status": "CONNECTED",
                "connected": True,
                "provider": f"SMTP ({settings.SMTP_HOST}:{settings.SMTP_PORT})",
                "sender_email": settings.SMTP_FROM_EMAIL,
                "latency_ms": latency,
                "verified_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
        except Exception as e:
            return {
                "name": "Transactional Email (SMTP)",
                "status": "DISCONNECTED",
                "connected": False,
                "error": str(e),
            }

    def test_sms_connection(self) -> Dict[str, Any]:
        """
        Test live SMS connectivity against Twilio Messaging API.
        """
        if not self.is_sms_configured:
            return {
                "name": "Twilio SMS Service",
                "status": "NOT CONFIGURED",
                "connected": False,
                "error": "TWILIO_ACCOUNT_SID, AUTH_TOKEN, or PHONE_NUMBER missing.",
                "action_required": "Provide Twilio Account SID, Auth Token, and Sender Phone Number.",
            }

        start_t = time.time()
        url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}/Messages.json?PageSize=1"
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
                    return {
                        "name": "Twilio SMS Service",
                        "status": "CONNECTED",
                        "connected": True,
                        "phone_number": settings.TWILIO_PHONE_NUMBER,
                        "latency_ms": latency,
                        "verified_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    }
                else:
                    return {"name": "Twilio SMS Service", "status": "DISCONNECTED", "connected": False, "error": f"HTTP {response.status}"}
        except urllib.error.HTTPError as he:
            err = he.read().decode("utf-8", errors="ignore")
            return {"name": "Twilio SMS Service", "status": "DISCONNECTED", "connected": False, "error": f"HTTP {he.code}: {err[:200]}"}
        except Exception as e:
            return {"name": "Twilio SMS Service", "status": "DISCONNECTED", "connected": False, "error": str(e)}

notification_service = NotificationService()
