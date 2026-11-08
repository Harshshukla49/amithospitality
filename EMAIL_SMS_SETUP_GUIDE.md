# Transactional Email & SMS Notification Setup Guide
## Amit AI Concierge — Amit Hospitality (https://amithospitality.com/)

---

### 1. Overview
The Notification Service powers transactional guest and staff alerts across email and SMS. It provides branded, luxury-styled HTML emails and concise SMS notifications for:
- Guest reservation request receipts (with prominent DEMO disclaimer when in DEMO mode).
- Table confirmation / status change updates (ACCEPTED, CANCELLED, UNDER_REVIEW).
- Event & banquet lead acknowledgments.
- Internal manager and concierge alert dispatches.

Engineering features:
- **Dual Email Providers:** SendGrid Web API v3 with automatic fallback to standard SMTP (STARTTLS).
- **Twilio SMS:** Transactional SMS via Twilio Messages REST API.
- **Deduplication / Idempotency:** Prevents duplicate sends on network retries using idempotency keys.
- **Safety Shields:** In DEMO mode, confirmation emails explicitly highlight that the reservation is a simulated demonstration.

---

### 2. Environment Configuration

Add the following variables to `.env`:

```env
# SendGrid Configuration (Recommended)
SENDGRID_API_KEY=SG...your_sendgrid_api_key

# SMTP Configuration (Fallback)
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=SG...your_sendgrid_api_key
SMTP_FROM_EMAIL=concierge@amithospitality.com

# Twilio SMS Configuration
TWILIO_ACCOUNT_SID=AC...your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890
```

---

### 3. Service Interface & Usage

Defined in [`backend/app/services/notification_service.py`](file:///c:/Users/india/Desktop/amit%20hospitality/backend/app/services/notification_service.py):

```python
from app.services.notification_service import notification_service

# 1. Send Transactional Email
email_html = notification_service.build_reservation_request_email(
    ref_id="AMIT-RES-2026-9901",
    guest_name="Vikramaditya Singhania",
    outlet_name="Amber Terrace Rooftop",
    date_str="2026-11-20",
    time_str="20:00",
    guests_count=4,
    is_demo=False,
)

notification_service.send_email(
    to_email="guest@example.com",
    subject="Your Reservation Request — Amit Hospitality",
    html_content=email_html,
    idempotency_key="res_AMIT-RES-2026-9901_created",
)

# 2. Send Transactional SMS
notification_service.send_sms(
    to_phone="+919811000000",
    message_text="Amit Hospitality: Table request AMIT-RES-2026-9901 received for Amber Terrace. Our concierge will contact you shortly.",
    idempotency_key="sms_AMIT-RES-2026-9901_created",
)
```

---

### 4. Router & Endpoints

Defined in [`backend/app/routers/notifications.py`](file:///c:/Users/india/Desktop/amit%20hospitality/backend/app/routers/notifications.py):

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/notifications/email/send` | Dispatches transactional email (requires auth). |
| `POST` | `/api/v1/notifications/sms/send` | Dispatches transactional SMS (requires auth). |
| `POST` | `/api/v1/notifications/test-email` | Live connectivity test for SendGrid / SMTP. |
| `POST` | `/api/v1/notifications/test-sms` | Live connectivity test for Twilio SMS. |

---

### 5. Diagnostics & Verification

Execute live diagnostic tests:
```bash
# Test Email Connectivity
curl -X POST http://localhost:8000/api/v1/integrations/test/email \
  -H "Authorization: Bearer <ADMIN_JWT_TOKEN>"

# Test SMS Connectivity
curl -X POST http://localhost:8000/api/v1/integrations/test/sms \
  -H "Authorization: Bearer <ADMIN_JWT_TOKEN>"
```
Truthful response when unconfigured:
```json
{
  "name": "Transactional Email (SendGrid/SMTP)",
  "status": "NOT CONFIGURED",
  "connected": false,
  "error": "SENDGRID_API_KEY or SMTP credentials missing in environment",
  "action_required": "Provide SENDGRID_API_KEY or configure SMTP_HOST/USER/PASSWORD."
}
```
Zero fabrication is enforced across all endpoints.
