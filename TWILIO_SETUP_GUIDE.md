# Twilio Voice & Telephony Concierge Setup Guide
## Amit AI Concierge — Amit Hospitality (https://amithospitality.com/)

---

### 1. Overview
The Twilio Voice integration provides an automated interactive voice response (IVR) and voice concierge for Amit Hospitality's phone lines. When guests call the main reservation number, an Amazon Polly neural voice (`Polly.Aditi` in Indian English `en-IN`) greets them, listens to their dining requirements via speech recognition, provides outlet policies and table booking assistance, and can escalate directly to the front desk or manager via live call forwarding (`<Dial>+911140509900</Dial>`).

Engineering features:
- **TwiML Generation:** Generates valid, schema-compliant `<Response>`, `<Gather input="speech">`, `<Say>`, and `<Dial>` XML trees.
- **Speech-to-Text Processing:** Transcribes guest speech and extracts intents (reservation, timing, dress code, human manager escalation).
- **HMAC-SHA1 Signature Verification:** Validates `X-Twilio-Signature` against `TWILIO_AUTH_TOKEN`.
- **Live Connection Diagnostics:** Queries the Twilio Accounts REST API to inspect active status, account friendly name, and round-trip latency.

---

### 2. Environment Configuration

Add the following variables to `.env`:

```env
TWILIO_ACCOUNT_SID=AC...your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890
```

---

### 3. Twilio Console Configuration

1. **Purchase or Configure a Phone Number:**
   - In the [Twilio Console](https://console.twilio.com/), navigate to **Phone Numbers > Manage > Active Numbers**.
2. **Configure Voice Webhook:**
   - Under **Voice Configuration**, set **A CALL COMES IN** to:
     - URL: `https://your-domain.com/api/v1/voice/incoming`
     - HTTP Method: `POST`
3. **Configure Speech Gather Action URL:**
   - The platform automatically routes speech capture to `https://your-domain.com/api/v1/voice/interact`.
4. **Configure Status Callback:**
   - Call status events (call duration, completed, etc.) route to `https://your-domain.com/api/v1/voice/status`.

---

### 4. Router & Endpoints

Defined in [`backend/app/routers/voice.py`](file:///c:/Users/india/Desktop/amit%20hospitality/backend/app/routers/voice.py):

| Method | Endpoint | Return Type | Description |
|--------|----------|-------------|-------------|
| `POST` | `/api/v1/voice/incoming` | `application/xml` | Generates welcome TwiML with neural voice speech gather. |
| `POST` | `/api/v1/voice/interact` | `application/xml` | Processes transcribed speech and returns conversational TwiML or `<Dial>`. |
| `POST` | `/api/v1/voice/status` | `application/json` | Records call completion and telemetry. |
| `POST` | `/api/v1/voice/test-connection` | `application/json` | Verifies live account credentials against Twilio REST API. |

---

### 5. Escalation & Fallback Behavior

If the caller requests a human manager or if speech recognition cannot determine intent after repeated attempts, the concierge responds:
> *"Connecting you with our Senior Guest Relations Concierge right away. Please hold."*
and executes:
```xml
<Response>
    <Say voice="Polly.Aditi" language="en-IN">Connecting you with our Senior Guest Relations Concierge right away. Please hold.</Say>
    <Dial>+911140509900</Dial>
</Response>
```

---

### 6. Diagnostics & Verification
Administrators can run live connection diagnostics via the Admin Dashboard or via REST API:
```bash
curl -X POST http://localhost:8000/api/v1/integrations/test/voice \
  -H "Authorization: Bearer <ADMIN_JWT_TOKEN>"
```
Expected response:
```json
{
  "name": "Twilio Telephony & Voice AI",
  "status": "CONNECTED",
  "connected": true,
  "account_name": "Amit Hospitality Concierge",
  "account_status": "active",
  "phone_number": "+1234567890",
  "latency_ms": 312.4,
  "verified_at": "2026-11-08T18:45:00Z"
}
```
If unconfigured, returns `NOT CONFIGURED` with explicit parameter guidance.
