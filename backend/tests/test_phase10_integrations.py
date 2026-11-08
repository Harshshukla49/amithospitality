import os
import sys
import hmac
import hashlib
import time

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException

from app.database import Base
from app.models.user import User
from app.models.outlet import Outlet
from app.models.audit import EnvironmentSetting
from app.config import settings

# Phase 10 Services
from app.services.gemini_service import GeminiService, gemini_service
from app.services.whatsapp_service import WhatsAppService, whatsapp_service
from app.services.voice_service import TwilioVoiceService, voice_service
from app.services.notification_service import NotificationService, notification_service
from app.services.redis_service import RedisService, redis_service
from app.utils.monitoring import (
    sentry_before_send,
    scrub_sensitive_dict,
    init_sentry,
    test_sentry_connection,
)
from app.routers.integrations import get_integrations_status, test_single_integration
from app.routers.whatsapp import verify_whatsapp_webhook

def setup_test_db():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    return db

def test_phase10_integrations():
    print("\n================================================================================")
    print("   PHASE 10: ENTERPRISE INTEGRATIONS & PRODUCTION CONNECTIVITY VERIFICATION")
    print("================================================================================")
    db = setup_test_db()

    # Create admin user for API authorization tests
    admin_user = User(
        email="architect@amithospitality.com",
        password_hash="mock_hashed_password",
        full_name="Lead Architect",
        role="SUPER_ADMIN",
        is_active=True,
    )
    db.add(admin_user)
    db.commit()

    # --------------------------------------------------------------------------
    # 1. Google Gemini AI Integration
    # --------------------------------------------------------------------------
    print("\n>>> 1. Verifying Google Gemini AI Production Service...")
    g_service = GeminiService()
    
    # 1.1 Verify prompt grounding structure
    grounded_prompt = g_service.format_grounded_prompt(
        system_instruction="You are Amit Concierge.",
        context_chunks=["Amber Terrace opens at 5:00 PM.", "Dress code is smart casual."],
        user_message="When does Amber Terrace open?",
        chat_history=[{"role": "user", "parts": ["Hello"]}, {"role": "model", "parts": ["Welcome!"]}],
    )
    assert "You are Amit Concierge." in grounded_prompt
    assert "Amber Terrace opens at 5:00 PM." in grounded_prompt
    assert "When does Amber Terrace open?" in grounded_prompt
    print("  [OK] Grounded prompt formatting and contextual assembly verified.")

    # 1.2 Verify token computation
    tokens = g_service.calculate_token_usage("Short query text", "Detailed output response text.")
    assert tokens["prompt_tokens"] > 0
    assert tokens["completion_tokens"] > 0
    assert tokens["total_tokens"] == tokens["prompt_tokens"] + tokens["completion_tokens"]
    print(f"  [OK] Token usage calculation verified ({tokens['total_tokens']} tokens).")

    # 1.3 Verify connection test truthfulness
    gemini_diag = g_service.test_connection()
    assert "name" in gemini_diag
    assert gemini_diag["status"] in ["CONNECTED", "NOT CONFIGURED", "DISCONNECTED"]
    if not g_service.is_configured:
        assert gemini_diag["status"] == "NOT CONFIGURED"
        assert gemini_diag["connected"] is False
    print(f"  [OK] Gemini connection diagnostics: {gemini_diag['status']}")

    # --------------------------------------------------------------------------
    # 2. Meta WhatsApp Business Cloud API
    # --------------------------------------------------------------------------
    print("\n>>> 2. Verifying Meta WhatsApp Cloud API Service...")
    w_service = WhatsAppService()

    # 2.1 Webhook Verification Challenge
    expected_token = settings.WHATSAPP_VERIFY_TOKEN or "amit_concierge_whatsapp_verify_token_2026"
    challenge_response = verify_whatsapp_webhook(
        hub_mode="subscribe",
        hub_verify_token=expected_token,
        hub_challenge="1155992288",
    )
    assert challenge_response.body.decode("utf-8") == "1155992288"

    try:
        verify_whatsapp_webhook(
            hub_mode="subscribe",
            hub_verify_token="invalid_token_999",
            hub_challenge="1155992288",
        )
        assert False, "Invalid token should raise 403"
    except HTTPException as e:
        assert e.status_code == 403
    print("  [OK] Webhook verification challenge (hub.challenge) and auth verified.")

    # 2.2 HMAC-SHA256 Signature Verification
    app_secret = "meta_app_secret_test_key_99"
    payload_bytes = b'{"object":"whatsapp_business_account","entry":[]}'
    valid_sig = "sha256=" + hmac.new(app_secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()

    assert w_service.verify_signature(payload_bytes, valid_sig, secret=app_secret) is True
    assert w_service.verify_signature(payload_bytes, "sha256=tampered_signature", secret=app_secret) is False
    assert w_service.verify_signature(b'{"tampered":true}', valid_sig, secret=app_secret) is False
    print("  [OK] HMAC-SHA256 webhook payload signature verification verified.")

    # 2.3 Deduplication using wamid
    assert w_service.is_message_duplicate("wamid.HBgLM...1") is False
    w_service.record_processed_message("wamid.HBgLM...1")
    assert w_service.is_message_duplicate("wamid.HBgLM...1") is True
    print("  [OK] Inbound message deduplication (wamid cache) verified.")

    # 2.4 Diagnostic Connection Test
    wa_diag = w_service.test_connection()
    assert wa_diag["status"] in ["CONNECTED", "NOT CONFIGURED", "DISCONNECTED"]
    print(f"  [OK] WhatsApp connection diagnostics: {wa_diag['status']}")

    # --------------------------------------------------------------------------
    # 3. Twilio Telephony & Voice Concierge
    # --------------------------------------------------------------------------
    print("\n>>> 3. Verifying Twilio Voice & IVR Concierge...")
    v_service = TwilioVoiceService()

    # 3.1 Welcome TwiML
    welcome_xml = v_service.build_welcome_twiml(language="en-IN")
    assert "<Response>" in welcome_xml
    assert '<Gather input="speech"' in welcome_xml
    assert '<Say voice="Polly.Aditi"' in welcome_xml
    esc_num = settings.ESCALATION_PHONE_NUMBER or "+911140509900"
    assert f"<Dial>{esc_num}</Dial>" in welcome_xml
    print("  [OK] Incoming call welcome TwiML assembly verified.")

    # 3.2 Speech Recognition Routing & Escalation
    escalate_xml = v_service.build_interaction_twiml("I need to speak to the manager please")
    assert f"<Dial>{esc_num}</Dial>" in escalate_xml
    assert "Senior Guest Relations Concierge" in escalate_xml

    reserve_xml = v_service.build_interaction_twiml("I want to book a dinner table tonight")
    assert "dining reservation" in reserve_xml
    assert "Amber Terrace" in reserve_xml

    policy_xml = v_service.build_interaction_twiml("What is the dress code and valet timing?")
    assert "Amber Terrace" in policy_xml
    assert "valet parking" in policy_xml
    print("  [OK] Conversational voice speech intent recognition & routing verified.")

    # 3.3 Diagnostic Connection Test
    voice_diag = v_service.test_connection()
    assert voice_diag["status"] in ["CONNECTED", "NOT CONFIGURED", "DISCONNECTED"]
    print(f"  [OK] Twilio Voice connection diagnostics: {voice_diag['status']}")

    # --------------------------------------------------------------------------
    # 4. Email & SMS Transactional Communication
    # --------------------------------------------------------------------------
    print("\n>>> 4. Verifying Transactional Email & SMS Dispatchers...")
    n_service = NotificationService()

    # 4.1 HTML Email Template Generation
    req_email_html = n_service.build_reservation_request_email(
        ref_id="AMIT-RES-2026-9901",
        guest_name="Vikramaditya Singhania",
        outlet_name="Amber Terrace Rooftop",
        date_str="2026-11-20",
        time_str="20:00",
        guests_count=4,
        is_demo=True,
    )
    assert "AMIT-RES-2026-9901" in req_email_html
    assert "Vikramaditya Singhania" in req_email_html
    assert "Amber Terrace Rooftop" in req_email_html
    assert "DEMO SIMULATION NOTICE" in req_email_html

    status_email_html = n_service.build_reservation_status_email(
        ref_id="AMIT-RES-2026-9901",
        guest_name="Vikramaditya Singhania",
        outlet_name="Amber Terrace Rooftop",
        status="ACCEPTED",
        notes="Window table reserved",
        is_demo=False,
    )
    assert "ACCEPTED" in status_email_html
    assert "Window table reserved" in status_email_html
    print("  [OK] Branded responsive HTML transactional email templates verified.")

    # 4.2 Deduplication / Idempotency
    idemp_key = "idemp_msg_test_001"
    assert n_service.is_duplicate(idemp_key) is False
    n_service.record_sent_key(idemp_key)
    assert n_service.is_duplicate(idemp_key) is True
    print("  [OK] Email and SMS message deduplication verified.")

    # 4.3 Email & SMS Connection Tests
    email_diag = n_service.test_email_connection()
    assert email_diag["status"] in ["CONNECTED", "NOT CONFIGURED", "DISCONNECTED"]
    sms_diag = n_service.test_sms_connection()
    assert sms_diag["status"] in ["CONNECTED", "NOT CONFIGURED", "DISCONNECTED"]
    print(f"  [OK] Email diagnostics: {email_diag['status']} | SMS diagnostics: {sms_diag['status']}")

    # --------------------------------------------------------------------------
    # 5. Redis Distributed Cache & Rate Limiting
    # --------------------------------------------------------------------------
    print("\n>>> 5. Verifying Redis Distributed Cache & Rate Limiting...")
    r_service = RedisService()

    # 5.1 In-Memory & Distributed Key-Value Caching
    r_service.set("test_cache_key", "hospitality_val_99", ttl_seconds=60)
    assert r_service.get("test_cache_key") == "hospitality_val_99"
    r_service.delete("test_cache_key")
    assert r_service.get("test_cache_key") is None
    print("  [OK] Key-value caching (set, get, delete, TTL) verified.")

    # 5.2 Sliding Window Rate Limiting
    r_service.reset_limits()
    test_ip = "192.168.1.100"
    for i in range(5):
        allowed, retry_after = r_service.check_rate_limit(test_ip, limit=5, window_seconds=60)
        assert allowed is True, f"Request {i+1} should be allowed"

    # 6th request must be blocked
    blocked, retry_after = r_service.check_rate_limit(test_ip, limit=5, window_seconds=60)
    assert blocked is False
    assert retry_after >= 1
    print(f"  [OK] Sliding window rate limiter enforced block (retry after {retry_after}s).")

    # 5.3 Operating Mode & Diagnostics
    assert r_service.active_mode in ["DISTRIBUTED_REDIS", "IN_MEMORY_FALLBACK"]
    redis_diag = r_service.test_connection()
    assert redis_diag["status"] in ["CONNECTED", "NOT CONFIGURED", "DISCONNECTED"]
    print(f"  [OK] Redis operational mode: {r_service.active_mode} (Diagnostics: {redis_diag['status']})")

    # --------------------------------------------------------------------------
    # 6. Sentry Application Observability & PII Scrubber
    # --------------------------------------------------------------------------
    print("\n>>> 6. Verifying Sentry Observability & PII Security Scrubber...")
    # Test PII and credential scrubbing
    dirty_event = {
        "request": {
            "headers": {
                "Authorization": "Bearer secret_jwt_token_here_12345",
                "Cookie": "session_id=abcd1234efgh",
                "X-Twilio-Signature": "sig123456",
                "User-Agent": "Mozilla/5.0",
            },
            "data": {
                "username": "amit_guest",
                "password": "SuperSecretPassword123!",
                "whatsapp_token": "EAAxxx...",
                "notes": "Please reserve quiet table",
            },
        },
        "user": {
            "email": "vip_guest@amithospitality.com",
            "ip_address": "203.0.113.195",
        },
        "breadcrumbs": {
            "values": [
                {"data": {"api_key": "gemini_secret_998877"}},
            ]
        },
    }

    clean_event = sentry_before_send(dirty_event, {})
    assert clean_event["request"]["headers"]["Authorization"] == "[REDACTED_CREDENTIAL]"
    assert clean_event["request"]["headers"]["Cookie"] == "[REDACTED_CREDENTIAL]"
    assert clean_event["request"]["headers"]["User-Agent"] == "Mozilla/5.0"
    assert clean_event["request"]["data"]["password"] == "[REDACTED_CREDENTIAL]"
    assert clean_event["request"]["data"]["whatsapp_token"] == "[REDACTED_CREDENTIAL]"
    assert clean_event["request"]["data"]["notes"] == "Please reserve quiet table"
    assert clean_event["user"]["email"] == "[REDACTED_EMAIL]"
    assert clean_event["user"]["ip_address"] == "203.0.0.0"
    assert clean_event["breadcrumbs"]["values"][0]["data"]["api_key"] == "[REDACTED_CREDENTIAL]"
    print("  [OK] Sentry before_send PII & credential scrubber sanitized all sensitive tokens.")

    # 6.2 Safe No-Op init
    init_sentry()
    sentry_diag = test_sentry_connection()
    assert sentry_diag["status"] in ["CONNECTED", "NOT CONFIGURED"]
    print(f"  [OK] Sentry monitoring diagnostics: {sentry_diag['status']}")

    # --------------------------------------------------------------------------
    # 7. Admin Integrations Hub API Endpoints
    # --------------------------------------------------------------------------
    print("\n>>> 7. Verifying Admin Integrations Hub API Endpoints...")
    all_status = get_integrations_status(current_user=admin_user)
    assert "integrations" in all_status
    services = all_status["integrations"]

    expected_services = [
        "gemini_api",
        "whatsapp_cloud_api",
        "twilio_voice",
        "email_service",
        "sms_service",
        "redis_cache",
        "sentry_monitoring",
    ]
    for exp_svc in expected_services:
        assert exp_svc in services, f"Missing service in status API: {exp_svc}"
        assert "name" in services[exp_svc]
        assert "status" in services[exp_svc]
        assert "required_params" in services[exp_svc]
    print("  [OK] Integrations Hub status returns all 7 core services with parameters.")

    # 7.2 Individual Live Diagnostic Endpoints
    testable_ids = ["gemini", "whatsapp", "voice", "email", "sms", "redis", "sentry"]
    for tid in testable_ids:
        diag_res = test_single_integration(service_id=tid, current_user=admin_user)
        assert "status" in diag_res
        assert "name" in diag_res
        assert diag_res["status"] in ["CONNECTED", "NOT CONFIGURED", "DISCONNECTED"]
    print(f"  [OK] All {len(testable_ids)} individual diagnostic endpoints executed successfully.")

    # 7.3 Invalid service ID raises 400
    try:
        test_single_integration(service_id="invalid_unknown_svc", current_user=admin_user)
        assert False, "Should raise 400"
    except HTTPException as e:
        assert e.status_code == 400
    print("  [OK] Invalid service diagnostic rejection (400 Bad Request) verified.")

    print("\n================================================================================")
    print("  PHASE 10: ALL 7 ENTERPRISE INTEGRATIONS & APIS VERIFIED (100% PASS)")
    print("================================================================================\n")

if __name__ == "__main__":
    test_phase10_integrations()
