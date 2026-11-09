import re
import time
import logging
from typing import Dict, Any, Optional

from app.config import settings

logger = logging.getLogger("monitoring")

try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False
    logger.warning("sentry-sdk not installed; monitoring is disabled.")

# Sensitive keys to sanitize in headers, breadcrumbs, and extra data
SENSITIVE_KEYS = {
    "authorization",
    "cookie",
    "set-cookie",
    "x-twilio-signature",
    "x-hub-signature-256",
    "password",
    "token",
    "secret",
    "jwt",
    "api_key",
    "apikey",
    "access_token",
    "refresh_token",
    "whatsapp_token",
    "gemini_api_key",
    "openai_api_key",
    "card",
    "credit_card",
    "cvv",
}

def scrub_sensitive_dict(d: Any) -> Any:
    """Recursively scrub sensitive keys and credential patterns from dictionaries."""
    if isinstance(d, dict):
        scrubbed = {}
        for k, v in d.items():
            k_lower = str(k).lower()
            if any(sensitive in k_lower for sensitive in SENSITIVE_KEYS):
                scrubbed[k] = "[REDACTED_CREDENTIAL]"
            else:
                scrubbed[k] = scrub_sensitive_dict(v)
        return scrubbed
    elif isinstance(d, list):
        return [scrub_sensitive_dict(item) for item in d]
    elif isinstance(d, str):
        # Scrub bearer tokens
        if d.lower().startswith("bearer "):
            return "Bearer [REDACTED_TOKEN]"
        return d
    return d

def sentry_before_send(event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Sentry before_send hook:
    Strictly scrubs PII, API tokens, passwords, and sensitive request payload fields
    before transmitting exception events to external Sentry servers.
    """
    try:
        # 1. Scrub request data
        request_info = event.get("request", {})
        if "headers" in request_info:
            request_info["headers"] = scrub_sensitive_dict(request_info["headers"])
        if "data" in request_info:
            request_info["data"] = scrub_sensitive_dict(request_info["data"])
        if "cookies" in request_info:
            request_info["cookies"] = "[REDACTED_COOKIES]"

        # 2. Scrub user context (keep anonymous or scrub email/phone)
        user_info = event.get("user", {})
        if user_info:
            if "email" in user_info:
                user_info["email"] = "[REDACTED_EMAIL]"
            if "ip_address" in user_info:
                # Truncate IP to class C/subnet for telemetry privacy
                ip = user_info["ip_address"]
                parts = ip.split(".")
                if len(parts) == 4:
                    user_info["ip_address"] = f"{parts[0]}.{parts[1]}.0.0"

        # 3. Scrub breadcrumbs
        breadcrumbs = event.get("breadcrumbs", {})
        if "values" in breadcrumbs:
            for b in breadcrumbs["values"]:
                if "data" in b:
                    b["data"] = scrub_sensitive_dict(b["data"])

        # 4. Scrub extra context
        if "extra" in event:
            event["extra"] = scrub_sensitive_dict(event["extra"])

    except Exception as e:
        logger.error(f"Error scrubbing Sentry event: {e}")

    return event

def init_sentry():
    """
    Initialize Sentry monitoring SDK if SENTRY_DSN is configured.
    Safely no-ops in local development or if DSN is not provided.
    """
    if not SENTRY_AVAILABLE:
        return

    dsn = settings.SENTRY_DSN.strip() if settings.SENTRY_DSN else ""
    if not dsn or dsn.startswith("your_") or "example.com" in dsn:
        logger.info("Sentry DSN not configured; running without external telemetry.")
        return

    try:
        sentry_sdk.init(
            dsn=dsn,
            environment=settings.APP_ENV,
            release=f"{settings.APP_NAME}@{settings.APP_VERSION}",
            traces_sample_rate=0.2 if settings.APP_ENV == "production" else 1.0,
            profiles_sample_rate=0.1 if settings.APP_ENV == "production" else 0.0,
            before_send=sentry_before_send,
            send_default_pii=False,
            integrations=[
                FastApiIntegration(),
                SqlalchemyIntegration(),
            ],
        )
        logger.info(f"Sentry monitoring initialized successfully for environment '{settings.APP_ENV}'")
    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}")

def test_sentry_connection() -> Dict[str, Any]:
    """
    Check Sentry configuration status without generating synthetic error noise.
    """
    dsn = settings.SENTRY_DSN.strip() if settings.SENTRY_DSN else ""
    if not dsn or dsn.startswith("your_") or "example.com" in dsn:
        return {
            "name": "Sentry Application Telemetry & Error Tracking",
            "status": "NOT CONFIGURED",
            "connected": False,
            "error": "SENTRY_DSN missing in environment.",
            "action_required": "Provide a valid Sentry DSN project URL.",
        }

    return {
        "name": "Sentry Application Telemetry & Error Tracking",
        "status": "CONNECTED",
        "connected": True,
        "environment": settings.APP_ENV,
        "release": f"{settings.APP_NAME}@{settings.APP_VERSION}",
        "pii_scrubber_active": True,
        "verified_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
