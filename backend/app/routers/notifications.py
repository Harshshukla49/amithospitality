import re
import logging
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, EmailStr, field_validator
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.notification_service import notification_service
from app.utils.security import require_roles, get_current_user
from app.models.user import User
from app.models.notification import NotificationLog

logger = logging.getLogger("notifications_router")
router = APIRouter(prefix="/notifications", tags=["Notifications (Email & SMS)"])

def sanitize_email_html(html_str: str) -> str:
    """
    Sanitize transactional email HTML content to eliminate malicious injection.
    Disallows script tags, iframes, embedded objects, and inline javascript handlers.
    """
    if not html_str:
        return ""
    # Strip script, iframe, object, embed, form, input
    cleaned = re.sub(r"<\s*(script|iframe|object|embed|form|input)[^>]*>.*?<\s*/\s*\1\s*>", "", html_str, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r"<\s*(script|iframe|object|embed|form|input)[^>]*>", "", cleaned, flags=re.IGNORECASE)
    # Strip dangerous event handlers (e.g. onload, onerror, onclick)
    cleaned = re.sub(r"(\s+on[a-z]+\s*=\s*['\"][^'\"]*['\"])", "", cleaned, flags=re.IGNORECASE)
    # Strip javascript: URIs
    cleaned = re.sub(r"href\s*=\s*['\"]javascript:[^'\"]*['\"]", "href='#'", cleaned, flags=re.IGNORECASE)
    return cleaned

class EmailSendRequest(BaseModel):
    to_email: EmailStr
    subject: str
    html_content: str
    text_content: Optional[str] = None
    idempotency_key: Optional[str] = None

    @field_validator("subject")
    @classmethod
    def validate_subject(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("Email subject cannot be empty.")
        if "\n" in clean or "\r" in clean:
            raise ValueError("Email header injection detected in subject line.")
        return clean

class SMSSendRequest(BaseModel):
    to_phone: str
    message: str
    idempotency_key: Optional[str] = None

    @field_validator("to_phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        clean = v.strip()
        digits = re.sub(r"[^\d+]", "", clean)
        if len(digits) < 7:
            raise ValueError("Invalid phone number format.")
        return clean

@router.post("/email/send")
async def send_transactional_email(
    req: EmailSendRequest,
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN", "MANAGER")),
):
    """
    Send authorized transactional email to guest or internal staff.
    Restricted to Super Admin, Admin, and Manager roles.
    Sanitizes HTML content to prevent HTML/XSS injection.
    """
    clean_html = sanitize_email_html(req.html_content)
    result = notification_service.send_email(
        to_email=str(req.to_email),
        subject=req.subject,
        html_content=clean_html,
        text_content=req.text_content,
        idempotency_key=req.idempotency_key,
    )
    return result

@router.post("/sms/send")
async def send_transactional_sms(
    req: SMSSendRequest,
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN", "MANAGER")),
):
    """
    Send authorized transactional SMS via Twilio.
    Restricted to Super Admin, Admin, and Manager roles.
    """
    result = notification_service.send_sms(
        to_phone=req.to_phone,
        message_text=req.message,
        idempotency_key=req.idempotency_key,
    )
    return result

@router.post("/test-email")
async def test_email_connectivity(
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN")),
):
    """
    Live connectivity test for SendGrid / SMTP.
    Requires Super Admin or Admin role.
    """
    return notification_service.test_email_connection()

@router.post("/test-sms")
async def test_sms_connectivity(
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN")),
):
    """
    Live connectivity test for Twilio SMS.
    Requires Super Admin or Admin role.
    """
    return notification_service.test_sms_connection()

@router.get("/logs")
def list_notification_logs(
    limit: int = 50,
    entity_type: Optional[str] = None,
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN", "MANAGER", "STAFF")),
    db: Session = Depends(get_db),
):
    """
    Retrieve audit history of dispatched (and simulated) transactional notifications.
    """
    query = db.query(NotificationLog).order_by(NotificationLog.created_at.desc())
    if entity_type:
        query = query.filter(NotificationLog.entity_type == entity_type)
    logs = query.limit(limit).all()
    return [
        {
            "id": l.id,
            "entity_type": l.entity_type,
            "entity_id": l.entity_id,
            "reference_id": l.reference_id,
            "channel": l.channel,
            "recipient": l.recipient,
            "event_type": l.event_type,
            "idempotency_key": l.idempotency_key,
            "status": l.status,
            "error_message": l.error_message,
            "environment": l.environment,
            "created_at": l.created_at.isoformat() if l.created_at else None,
        }
        for l in logs
    ]
