import time
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional

from app.config import settings
from app.models.user import User
from app.utils.security import require_roles, get_current_user_optional
from app.services.gemini_service import gemini_service
from app.services.whatsapp_service import whatsapp_service
from app.services.voice_service import voice_service
from app.services.notification_service import notification_service
from app.services.redis_service import redis_service
from app.utils.monitoring import test_sentry_connection

router = APIRouter(prefix="/api/v1/integrations", tags=["Integrations & Third-Party Services"])

@router.get("/status")
def get_integrations_status(
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> Dict[str, Any]:
    """
    Inspect and report operational readiness of all 7 core external enterprise integrations.
    Zero fabrication: Strictly evaluates whether active environment variables are present.
    Public monitoring probes receive sanitized status without private configuration details.
    """
    is_privileged = current_user is not None and current_user.role in ("SUPER_ADMIN", "ADMIN", "MANAGER")
    gemini_configured = gemini_service.is_configured
    whatsapp_configured = whatsapp_service.is_configured
    voice_configured = voice_service.is_configured
    email_configured = notification_service.is_email_configured
    sms_configured = notification_service.is_sms_configured
    redis_configured = redis_service.is_configured
    sentry_configured = bool(settings.SENTRY_DSN and len(settings.SENTRY_DSN.strip()) > 8 and not settings.SENTRY_DSN.startswith("your_"))

    return {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "app_env": settings.APP_ENV,
        "default_environment": settings.DEFAULT_ENVIRONMENT,
        "integrations": {
            "gemini_api": {
                "id": "gemini",
                "name": "Google Gemini Generative AI",
                "category": "Artificial Intelligence",
                "status": "CONFIGURED" if gemini_configured else "NOT CONFIGURED",
                "active_model": settings.GEMINI_MODEL,
                "offline_fallback": "Local Deterministic Semantic Fallback active",
                "required_params": ["GEMINI_API_KEY", "GEMINI_MODEL"],
                "action_required": None if gemini_configured else "Set GEMINI_API_KEY in environment variables.",
            },
            "whatsapp_cloud_api": {
                "id": "whatsapp",
                "name": "Meta WhatsApp Business Cloud API",
                "category": "Omnichannel Messaging",
                "status": "CONFIGURED" if whatsapp_configured else "NOT CONFIGURED",
                "phone_number_id": settings.WHATSAPP_PHONE_NUMBER_ID if (is_privileged and whatsapp_configured) else None,
                "required_params": ["WHATSAPP_TOKEN", "WHATSAPP_PHONE_NUMBER_ID", "WHATSAPP_VERIFY_TOKEN", "WHATSAPP_APP_SECRET"] if is_privileged else [],
                "action_required": (None if whatsapp_configured else "Set Meta Cloud API credentials in environment.") if is_privileged else None,
            },
            "twilio_voice": {
                "id": "voice",
                "name": "Twilio Telephony & Voice Concierge",
                "category": "Interactive Voice Response",
                "status": "CONFIGURED" if voice_configured else "NOT CONFIGURED",
                "phone_number": settings.TWILIO_PHONE_NUMBER if (is_privileged and voice_configured) else None,
                "required_params": ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_PHONE_NUMBER"] if is_privileged else [],
                "action_required": (None if voice_configured else "Set Twilio Account SID, Auth Token, and Phone Number.") if is_privileged else None,
            },
            "email_service": {
                "id": "email",
                "name": "Transactional Email (SendGrid / SMTP)",
                "category": "Customer & Staff Notifications",
                "status": "CONFIGURED" if email_configured else "NOT CONFIGURED",
                "provider": ("SendGrid" if (settings.SENDGRID_API_KEY and len(settings.SENDGRID_API_KEY) > 15) else ("SMTP" if settings.SMTP_HOST else "None")) if is_privileged else "Configured Provider",
                "sender_email": settings.SMTP_FROM_EMAIL if is_privileged else None,
                "required_params": (["SENDGRID_API_KEY"] if settings.SENDGRID_API_KEY else ["SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD"]) if is_privileged else [],
                "action_required": (None if email_configured else "Set SENDGRID_API_KEY or SMTP host credentials.") if is_privileged else None,
            },
            "sms_service": {
                "id": "sms",
                "name": "Twilio SMS Notification Dispatcher",
                "category": "Direct Mobile Alerts",
                "status": "CONFIGURED" if sms_configured else "NOT CONFIGURED",
                "sender_phone": settings.TWILIO_PHONE_NUMBER if (is_privileged and sms_configured) else None,
                "required_params": ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_PHONE_NUMBER"] if is_privileged else [],
                "action_required": (None if sms_configured else "Configure Twilio credentials for SMS dispatch.") if is_privileged else None,
            },
            "redis_cache": {
                "id": "redis",
                "name": "Redis Distributed Cache & Rate Limiting",
                "category": "Performance & Scalability",
                "status": "CONFIGURED" if redis_configured else "NOT CONFIGURED (Using In-Memory Sliding-Window Fallback)",
                "mode": redis_service.active_mode,
                "required_params": ["REDIS_URL"],
                "action_required": None if redis_configured else "Optional: Set REDIS_URL for multi-instance cluster synchronization.",
            },
            "sentry_monitoring": {
                "id": "sentry",
                "name": "Sentry Application Telemetry & Error APM",
                "category": "Production Observability",
                "status": "CONFIGURED" if sentry_configured else "NOT CONFIGURED",
                "environment": settings.APP_ENV,
                "required_params": ["SENTRY_DSN"],
                "action_required": None if sentry_configured else "Optional: Set SENTRY_DSN for production error tracking.",
            },
        },
        "disclaimer": "Credentials are never rendered in plain text. Status represents live runtime capability with graceful local fallbacks.",
    }

@router.post("/test/{service_id}")
def test_single_integration(
    service_id: str,
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN")),
) -> Dict[str, Any]:
    """
    Execute live diagnostic connectivity test against an external integration.
    Never fabricates connection state: Returns truthful connectivity verification.
    """
    sid = service_id.lower().strip()

    if sid in ("gemini", "gemini_api"):
        return gemini_service.test_connection()
    elif sid in ("whatsapp", "whatsapp_cloud_api"):
        return whatsapp_service.test_connection()
    elif sid in ("voice", "twilio_voice"):
        return voice_service.test_connection()
    elif sid in ("email", "email_service"):
        return notification_service.test_email_connection()
    elif sid in ("sms", "sms_service"):
        return notification_service.test_sms_connection()
    elif sid in ("redis", "redis_cache"):
        return redis_service.test_connection()
    elif sid in ("sentry", "sentry_monitoring"):
        return test_sentry_connection()
    else:
        raise HTTPException(status_code=400, detail=f"Unknown integration service: '{service_id}'")
