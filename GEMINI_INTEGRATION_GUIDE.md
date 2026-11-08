# Google Gemini AI Production Integration Guide
## Amit AI Concierge — Amit Hospitality (https://amithospitality.com/)

---

### 1. Architectural Overview
Amit AI Concierge leverages Google's Gemini models (`gemini-1.5-flash` by default, configurable via `GEMINI_MODEL`) to deliver grounded, conversational hospitality concierge services for Amit Hospitality's luxury restaurants, rooftop lounges, and private dining rooms.

Key engineering highlights:
- **Strict Context Grounding:** Every prompt is assembled with vetted chunks extracted from the active environment (`DEMO` vs. `REAL`).
- **Prompt Injection Defense:** Input is scrutinized before inference to prevent jailbreaks, persona overrides, and data exfiltration.
- **Resilient Fallback:** When `GEMINI_API_KEY` is absent or API quotas are exceeded, the platform seamlessly switches to deterministic local semantic search.
- **Token Tracking & Latency Telemetry:** Response metadata records token counts and API round-trip latency.

---

### 2. Configuration & Credentials

Add the following keys to your `.env` or deployment secrets vault:

```env
AI_PROVIDER=gemini
GEMINI_API_KEY=AIzaSy...your_actual_gemini_api_key
GEMINI_MODEL=gemini-1.5-flash
EMBEDDING_MODEL=text-embedding-004
```

To acquire a key:
1. Navigate to [Google AI Studio](https://aistudio.google.com/).
2. Click **Create API Key** within your designated Google Cloud project.
3. Paste the key into `GEMINI_API_KEY` in `.env`.

---

### 3. Service Interface & Usage

The service is encapsulated in [`backend/app/services/gemini_service.py`](file:///c:/Users/india/Desktop/amit%20hospitality/backend/app/services/gemini_service.py):

```python
from app.services.gemini_service import gemini_service

result = gemini_service.generate_grounded_response(
    prompt="Do you have rooftop seating and what is the dress code?",
    system_instruction="You are the luxury concierge for Amit Hospitality...",
    environment="REAL",
    history=[...],
    max_retries=2,
    timeout=10,
)

if result:
    print("Reply:", result["reply"])
    print("Tokens:", result["tokens_used"])
    print("Latency:", result["latency_ms"], "ms")
```

---

### 4. Multilingual & Hinglish Support
Gemini 1.5 Flash natively understands English, Hindi, and colloquial Hinglish (e.g., *"Table book karni hai 4 logon ke liye Friday shaam ko"*). The system prompt instructs the model to reply in the exact language or tone selected by the guest while strictly preserving hospitality standards.

---

### 5. Diagnostics & Verification
Administrators can run live connection diagnostics via the Admin Dashboard or via REST API:
```bash
curl -X POST http://localhost:8000/api/v1/integrations/test/gemini \
  -H "Authorization: Bearer <ADMIN_JWT_TOKEN>"
```
Expected response:
```json
{
  "name": "Google Gemini Generative AI",
  "status": "CONNECTED",
  "connected": true,
  "model": "gemini-1.5-flash",
  "latency_ms": 284.1,
  "verified_at": "2026-11-08T18:45:00Z"
}
```
If credentials are not supplied, the endpoint truthfully returns `NOT CONFIGURED` with zero synthetic fabrication.
