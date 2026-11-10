import time
from datetime import datetime
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
        if idempotency_key in self._sent_idempotency_keys:
            return True

        # Persistent database-level deduplication (cross-worker and post-restart safe)
        try:
            from app.database import SessionLocal
            from app.models.notification import NotificationLog
            db = SessionLocal()
            try:
                existing = db.query(NotificationLog).filter(
                    NotificationLog.idempotency_key == idempotency_key,
                    NotificationLog.status.in_(["SENT", "SIMULATED"]),
                ).first()
                if existing:
                    self.record_sent_key(idempotency_key)
                    return True
            finally:
                db.close()
        except Exception as ex:
            logger.debug(f"DB persistent idempotency notice: {ex}")

        return False

    def record_sent_key(self, idempotency_key: Optional[str]):
        if idempotency_key:
            self._clean_old_idempotency_keys()
            self._sent_idempotency_keys[idempotency_key] = time.time()

    def atomic_claim_notification(
        self,
        idempotency_key: str,
        entity_type: str,
        entity_id: Optional[int],
        reference_id: Optional[str],
        channel: str,
        recipient: str,
        event_type: str,
        environment: str = "DEMO",
        outlet_id: Optional[int] = None,
    ) -> bool:
        """
        Database-backed atomic claim to prevent concurrent duplicate delivery across multiple workers.
        Atomically attempts to reserve the idempotency_key with status 'CLAIMED'.
        Returns True if this worker won the reservation claim; False if already claimed or sent.
        """
        from app.database import SessionLocal
        from app.models.notification import NotificationLog
        from sqlalchemy.exc import IntegrityError

        # Fast in-memory check
        if idempotency_key in self._sent_idempotency_keys:
            return False

        db = SessionLocal()
        try:
            existing = db.query(NotificationLog).filter(NotificationLog.idempotency_key == idempotency_key).first()
            if existing:
                if existing.status in ("SENT", "SIMULATED"):
                    self.record_sent_key(idempotency_key)
                    return False
                elif existing.status == "CLAIMED":
                    # If claimed within last 60 seconds by another worker, do not duplicate
                    if existing.created_at and (datetime.utcnow() - existing.created_at).total_seconds() < 60:
                        return False
                    # Stale claim (> 60s), allow reclaim
                    existing.status = "CLAIMED"
                    existing.created_at = datetime.utcnow()
                    db.commit()
                    return True
                elif existing.status == "FAILED":
                    # Allow safe retry for failed notifications
                    existing.status = "CLAIMED"
                    existing.created_at = datetime.utcnow()
                    db.commit()
                    return True

            # If no existing record, insert claim atomically
            claim_log = NotificationLog(
                outlet_id=outlet_id,
                entity_type=entity_type,
                entity_id=entity_id,
                reference_id=reference_id,
                channel=channel,
                recipient=recipient,
                event_type=event_type,
                idempotency_key=idempotency_key,
                status="CLAIMED",
                environment=environment,
            )
            db.add(claim_log)
            db.commit()
            return True
        except IntegrityError:
            db.rollback()
            # Another concurrent worker claimed the exact same key at the same millisecond
            logger.info(f"Concurrent claim race detected for {idempotency_key} - duplicate suppressed.")
            return False
        except Exception as ex:
            db.rollback()
            logger.warning(f"Error during atomic notification claim: {ex}")
            return not self.is_duplicate(idempotency_key)
        finally:
            db.close()

    def update_claimed_notification(
        self,
        idempotency_key: str,
        final_status: str,
        error_message: Optional[str] = None,
        outlet_id: Optional[int] = None,
    ):
        """Update a previously claimed atomic notification record with final delivery status."""
        from app.database import SessionLocal
        from app.models.notification import NotificationLog

        db = SessionLocal()
        try:
            log_record = db.query(NotificationLog).filter(NotificationLog.idempotency_key == idempotency_key).first()
            if log_record:
                log_record.status = final_status
                log_record.error_message = error_message
                if outlet_id is not None:
                    log_record.outlet_id = outlet_id
                log_record.created_at = datetime.utcnow()
                db.commit()
                if final_status in ("SENT", "SIMULATED"):
                    self.record_sent_key(idempotency_key)
        except Exception as ex:
            db.rollback()
            logger.warning(f"Failed to update claimed NotificationLog for {idempotency_key}: {ex}")
        finally:
            db.close()

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

    # ==========================================
    # RESERVATION & LEAD LIFECYCLE DISPATCH
    # ==========================================

    def notify_reservation_lifecycle(
        self,
        reservation_id: int,
        reference_id: str,
        guest_name: str,
        guest_email: Optional[str],
        guest_phone: str,
        outlet_name: str,
        date_str: str,
        time_str: str,
        guest_count: int,
        status: str,
        environment: str = "DEMO",
        notes: Optional[str] = None,
        outlet_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Asynchronously handles reservation lifecycle notifications (Email & SMS).
        Provides idempotency, delivery logging into notification_logs, and graceful
        unconfigured/sandbox simulation without blocking callers.
        """
        from app.database import SessionLocal
        from app.models.notification import NotificationLog

        is_demo = (environment == "DEMO")
        idempotency_key_base = f"res_{reference_id}_{status.upper()}"
        results = {"email": None, "sms": None}

        # 1. Email Notification
        if guest_email:
            email_key = f"{idempotency_key_base}_email"
            if self.atomic_claim_notification(
                idempotency_key=email_key,
                entity_type="RESERVATION",
                entity_id=reservation_id,
                reference_id=reference_id,
                channel="EMAIL",
                recipient=guest_email,
                event_type=f"RESERVATION_{status.upper()}",
                environment=environment,
                outlet_id=outlet_id,
            ):
                if status.upper() == "NEW":
                    subject = f"Reservation Request Received: {reference_id} – Amit Hospitality"
                    html_body = self.build_reservation_request_email(
                        ref_id=reference_id,
                        guest_name=guest_name,
                        outlet_name=outlet_name,
                        date_str=date_str,
                        time_str=time_str,
                        guests_count=guest_count,
                        is_demo=is_demo,
                    )
                else:
                    subject = f"Reservation Update: {reference_id} ({status.upper()}) – {outlet_name}"
                    html_body = self.build_reservation_status_email(
                        ref_id=reference_id,
                        guest_name=guest_name,
                        outlet_name=outlet_name,
                        status=status,
                        notes=notes,
                        is_demo=is_demo,
                    )

                # Security safeguard: In DEMO mode, NEVER dispatch real emails
                should_send_live = self.is_email_configured and not is_demo
                if should_send_live:
                    res = self.send_email(to_email=guest_email, subject=subject, html_content=html_body, idempotency_key=email_key)
                    email_status = "SENT" if res.get("sent") else "FAILED"
                    err_msg = res.get("error")
                else:
                    email_status = "SIMULATED"
                    err_msg = None
                    res = {"sent": True, "simulated": True, "message": "Email simulation logged (DEMO mode or unconfigured credentials)"}

                results["email"] = res
                self.update_claimed_notification(
                    idempotency_key=email_key,
                    final_status=email_status,
                    error_message=err_msg,
                    outlet_id=outlet_id,
                )

        # 2. SMS Notification
        if guest_phone:
            sms_key = f"{idempotency_key_base}_sms"
            if self.atomic_claim_notification(
                idempotency_key=sms_key,
                entity_type="RESERVATION",
                entity_id=reservation_id,
                reference_id=reference_id,
                channel="SMS",
                recipient=guest_phone,
                event_type=f"RESERVATION_{status.upper()}",
                environment=environment,
                outlet_id=outlet_id,
            ):
                if status.upper() == "NEW":
                    sms_text = f"Amit Hospitality: Request {reference_id} for {outlet_name} on {date_str} at {time_str} received. Our Concierge is confirming table availability."
                elif status.upper() == "ACCEPTED":
                    sms_text = f"Amit Hospitality: Great news! Your reservation {reference_id} for {outlet_name} on {date_str} at {time_str} is CONFIRMED. We look forward to welcoming you."
                elif status.upper() == "CANCELLED":
                    sms_text = f"Amit Hospitality: Your reservation {reference_id} for {outlet_name} has been CANCELLED as requested."
                else:
                    sms_text = f"Amit Hospitality: Reservation {reference_id} for {outlet_name} status updated to {status.upper()}."

                if is_demo:
                    sms_text = f"[DEMO] {sms_text}"

                # Security safeguard: In DEMO mode, NEVER dispatch real SMS
                should_send_live_sms = self.is_sms_configured and not is_demo
                if should_send_live_sms:
                    res = self.send_sms(to_phone=guest_phone, message_text=sms_text, idempotency_key=sms_key)
                    sms_status = "SENT" if res.get("sent") else "FAILED"
                    err_msg = res.get("error")
                else:
                    sms_status = "SIMULATED"
                    err_msg = None
                    res = {"sent": True, "simulated": True, "message": "SMS simulation logged (DEMO mode or unconfigured credentials)"}

                results["sms"] = res
                self.update_claimed_notification(
                    idempotency_key=sms_key,
                    final_status=sms_status,
                    error_message=err_msg,
                    outlet_id=outlet_id,
                )

        return results

    def notify_lead_lifecycle(
        self,
        lead_id: int,
        reference_id: str,
        guest_name: str,
        guest_email: str,
        guest_phone: str,
        outlet_name: str,
        enquiry_type: str,
        environment: str = "DEMO",
        outlet_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        from app.database import SessionLocal
        from app.models.notification import NotificationLog

        is_demo = (environment == "DEMO")
        idempotency_key_base = f"lead_{reference_id}_CREATED"
        results = {"email": None, "sms": None}

        if guest_email:
            email_key = f"{idempotency_key_base}_email"
            if self.atomic_claim_notification(
                idempotency_key=email_key,
                entity_type="LEAD",
                entity_id=lead_id,
                reference_id=reference_id,
                channel="EMAIL",
                recipient=guest_email,
                event_type="LEAD_CREATED",
                environment=environment,
                outlet_id=outlet_id,
            ):
                subject = f"Inquiry Received: #{reference_id} – Amit Hospitality Events"
                html_body = self.build_lead_acknowledgement_email(
                    lead_id=reference_id,
                    guest_name=guest_name,
                    event_type=enquiry_type,
                    outlet_name=outlet_name,
                    is_demo=is_demo,
                )
                should_send_live = self.is_email_configured and not is_demo
                if should_send_live:
                    res = self.send_email(to_email=guest_email, subject=subject, html_content=html_body, idempotency_key=email_key)
                    email_status = "SENT" if res.get("sent") else "FAILED"
                    err_msg = res.get("error")
                else:
                    email_status = "SIMULATED"
                    err_msg = None
                    res = {"sent": True, "simulated": True}

                results["email"] = res
                self.update_claimed_notification(
                    idempotency_key=email_key,
                    final_status=email_status,
                    error_message=err_msg,
                    outlet_id=outlet_id,
                )

        return results

notification_service = NotificationService()
