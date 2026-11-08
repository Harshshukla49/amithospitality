# Amit AI Concierge — Incident Response & Business Continuity Guide
## Enterprise Hospitality Platform for Amit Hospitality (https://amithospitality.com/)

---

### 1. Incident Management Overview

This document outlines the standard operating procedures (SOPs) for responding to operational interruptions, external cloud service outages, and cybersecurity incidents affecting the Amit AI Concierge platform.

**Severity Levels:**
- **SEV-1 (Critical):** Core reservation database unavailable, active data exposure, or complete concierge outage across all communication channels.
- **SEV-2 (Major):** Degradation of an external third-party provider (e.g., Meta WhatsApp API down, Gemini API rate-limited) with active fallback handling.
- **SEV-3 (Minor):** Non-blocking performance anomalies or single-outlet notification delays.

---

### 2. Outage Response Procedures

#### 2.1 AI Provider Outage (Google Gemini API)
- **Symptom:** AI chat turns fail with HTTP 429, 503, or timeout; Gemini connection diagnostic reports `DISCONNECTED`.
- **System Behavior:**
  - Automatic exponential backoff retries (1.0s, 2.0s).
  - Seamless fallback to the local deterministic semantic search engine.
  - Zero hallucination guard activates: informs guest that verified records cannot be generated and routes to Guest Relations.
- **Operator Action:**
  1. Inspect Google Cloud Console / AI Studio status dashboard.
  2. Verify API quota and billing account status.
  3. If primary key exhausted, rotate `GEMINI_API_KEY` in environment variables or configure `OPENAI_API_KEY` as secondary fallback.
  4. Platform operates safely indefinitely on local semantic fallback without guest-facing crashes.

#### 2.2 Meta WhatsApp Cloud API Outage
- **Symptom:** Inbound messages not received; outbound messages fail with Graph API errors; webhook delivery retries spike.
- **System Behavior:**
  - Inbound webhook deduplication (`wamid`) suppresses duplicate retries.
  - Webhook returns HTTP 200 immediately to prevent Meta from disabling the webhook subscription.
  - Errors logged to Sentry with PII sanitized.
- **Operator Action:**
  1. Check Meta for Developers Status Page ([metastatus.com](https://metastatus.com/)).
  2. Verify system user token expiration in Meta Business Manager.
  3. Enable human staff monitoring on the Amit Hospitality front desk phone (+91 11 4050 9900).
  4. Ensure website chatbot drawer remains primary customer engagement point.

#### 2.3 Twilio Voice & IVR Outage
- **Symptom:** Incoming calls drop or fail to execute speech gather; status callback reports failed calls.
- **System Behavior:**
  - TwiML fallback immediately dials configured escalation line (`settings.ESCALATION_PHONE_NUMBER`).
- **Operator Action:**
  1. Check Twilio Status Dashboard ([status.twilio.com](https://status.twilio.com/)).
  2. Verify phone balance and regulatory compliance documents for Indian telecommunications.
  3. Ensure physical PBX / Front Desk phone lines are manned by human concierge staff.

#### 2.4 Transactional Email / SMS Outage
- **Symptom:** Confirmation emails or SMS alerts fail to dispatch; notification diagnostic reports `DISCONNECTED`.
- **System Behavior:**
  - SendGrid failures automatically fall back to standard SMTP (STARTTLS).
  - Idempotency keys prevent double sending when services recover.
  - Guest bookings remain saved in database with `PENDING` review status.
- **Operator Action:**
  1. Check SendGrid or Twilio account billing and sender reputation.
  2. Staff can view all new requests in Admin Reservations / Leads dashboards and contact guests directly.

#### 2.5 Redis Outage or Unavailability
- **Symptom:** Redis connection error; connection diagnostic reports `IN_MEMORY_FALLBACK` and `DEGRADED_LOCAL_NODE_ONLY`.
- **System Behavior:**
  - Seamless fallback to thread-safe local in-memory sliding window rate limiting.
  - Diagnostic dashboard alerts administrator of degraded multi-instance sync.
- **Operator Action:**
  1. Restart Redis container or check cloud managed Redis host (AWS ElastiCache, Render KeyDB, Redis Cloud).
  2. Verify network security group and TLS connection strings (`rediss://`).
  3. Application continues running safely in local mode without rate limiting gaps.

#### 2.6 Database Outage (PostgreSQL)
- **Symptom:** Health check `/api/v1/health` reports `"status": "unhealthy"`; backend routes return HTTP 500.
- **System Behavior:**
  - Read/write operations halted; health probes signal Kubernetes / cloud orchestrator not to route traffic.
- **Operator Action:**
  1. Inspect PostgreSQL service status and disk space.
  2. Restore from most recent automated backup snapshot via `python scripts/restore_db.py <backup_file>`.
  3. Execute database connection test via `/api/v1/health` to confirm restoration.

---

### 3. Security Incident & Data Breach Response

#### 3.1 Suspected Customer Data Exposure or Credential Compromise
In compliance with the **Digital Personal Data Protection (DPDP) Act 2023** and enterprise security standards:

1. **Immediate Containment:**
   - Invalidate all active JWT tokens by rotating `JWT_SECRET_KEY` in environment variables.
   - Force all active sessions to terminate immediately.
   - Rotate database credentials and external API tokens (`WHATSAPP_TOKEN`, `SENDGRID_API_KEY`, `TWILIO_AUTH_TOKEN`).
2. **Forensic Audit:**
   - Export and inspect immutable compliance logs via `GET /api/v1/audit/logs`.
   - Identify affected user accounts, outlets, and IP address origins.
   - Verify whether unredacted customer data was transmitted to external servers.
3. **Mandatory Reporting (DPDP Act 2023):**
   - Report the data breach to the **Data Protection Board of India (DPBI)** and affected data principals in accordance with statutory guidelines.
   - Document root cause analysis (RCA) and mitigation measures implemented.

---

### 4. Emergency Contacts

| Role | Contact Entity | Details |
|------|----------------|---------|
| General Manager / Concierge Desk | Amit Hospitality Front Desk | `+91 11 4050 9900` / `guestrelations@amithospitality.com` |
| Principal Application Architect | Amit Engineering Operations | `admin@amithospitality.com` |
| Security & Compliance Officer | Data Protection Office | `privacy@amithospitality.com` |
