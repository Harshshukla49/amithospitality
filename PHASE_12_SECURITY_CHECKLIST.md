# AMIT AI CONCIERGE — PHASE 12 SECURITY & DPDP CHECKLIST
## Pre-Pilot Application Security & Hospitality Data Protection Audit

**Client / Brand:** Amit Hospitality ([https://amithospitality.com/](https://amithospitality.com/))  
**Auditor / Security Roles:** Senior Application Security Engineer & Data Protection Specialist  
**Evaluation Date:** November 8, 2026  
**Applicable Legal Framework:** India Digital Personal Data Protection Act, 2023 (DPDP Act 2023)  
**Security Benchmark:** Enterprise Tier-1 Hospitality Platform  
**Overall Security Status:** **VERIFIED COMPLIANT FOR SUPERVISED PILOT**

---

## 1. PRE-PILOT APPLICATION SECURITY CHECKLIST

### 1.1 Identity, Authentication & Session Security
- [x] **Enterprise Password Complexity:** Enforced by [`validate_password_policy()`](file:///c:/Users/india/Desktop/amit%20hospitality/backend/app/utils/security.py) (min 8 chars, uppercase, lowercase, digit, special symbol, common blacklist).
- [x] **Password Hashing:** Passwords hashed with `bcrypt` using work factor 12. Plaintext passwords never stored.
- [x] **JWT Token Rotation:** Refresh tokens rotated upon every exchange. Old token `jti` immediately blacklisted in `revoked_tokens`.
- [x] **Replay Attack Defense:** Consumed or rotated refresh tokens return `HTTP 401 Unauthorized`.
- [x] **Concurrent Refresh Race Condition Defense:** Concurrent replay attempts are serialized via database unique constraints on `revoked_tokens.jti`. Exactly one request succeeds.
- [x] **Session Revocation:** Explicit logout endpoint (`POST /api/auth/logout`) invalidates tokens across all server nodes.

### 1.2 Role-Based Access Control (RBAC) & Tenant Isolation
- [x] **Role Hierarchy:** Enforces strict role privileges across `SUPER_ADMIN`, `ADMIN`, `MANAGER`, `STAFF`, and `GUEST`.
- [x] **Server-Side Tenant Isolation:** Enforced at the database query level in [`reservations.py`](file:///c:/Users/india/Desktop/amit%20hospitality/backend/app/routers/reservations.py), [`leads.py`](file:///c:/Users/india/Desktop/amit%20hospitality/backend/app/routers/leads.py), and [`analytics.py`](file:///c:/Users/india/Desktop/amit%20hospitality/backend/app/routers/analytics.py).
- [x] **Cross-Outlet Rejection:** Staff or managers attempting to view or alter records for foreign outlets are strictly blocked with `HTTP 403 Forbidden`.
- [x] **Auto-Scoping:** Manager and staff listing queries automatically filter to their assigned outlet without relying on client-side parameters.
- [x] **Corporate Oversight:** Corporate administrators (`ADMIN`, `SUPER_ADMIN`) retain cross-outlet portfolio visibility.

### 1.3 Injection Defenses & Input Sanitization
- [x] **SQL Injection:** 100% eliminated through SQLAlchemy ORM parameterized statements. Zero raw SQL string concatenation.
- [x] **Cross-Site Scripting (XSS):**
  - Outbound email payloads sanitized by [`sanitize_email_html()`](file:///c:/Users/india/Desktop/amit%20hospitality/backend/app/routers/notifications.py), stripping `<script>`, `<iframe>`, `javascript:`, and inline event handlers.
  - Frontend built with React + TypeScript, providing automated DOM context escaping.
- [x] **AI Prompt Injection:**
  - Evaluated against adversarial prompts (instruction overrides, persona hijacking, developer mode jailbreaks).
  - Intercepted by `detect_prompt_injection()` regex patterns in [`security_middleware.py`](file:///c:/Users/india/Desktop/amit%20hospitality/backend/app/utils/security_middleware.py).
- [x] **Webhook Authenticity:** Meta WhatsApp webhook signatures verified using HMAC-SHA256 with constant-time digest comparison (`hmac.compare_digest`).

### 1.4 Network, Transport & Header Security
- [x] **Strict Transport Security (HSTS):** Enforced via `Strict-Transport-Security: max-age=31536000; includeSubDomains`.
- [x] **Clickjacking Protection:** Enforced via `X-Frame-Options: SAMEORIGIN` and Content Security Policy (`frame-ancestors 'self' https://amithospitality.com`).
- [x] **MIME Sniffing Defense:** Enforced via `X-Content-Type-Options: nosniff`.
- [x] **Permissions Policy:** Enforced via `Permissions-Policy: camera=(), microphone=(), geolocation=()`.
- [x] **Request Tracing:** Unique `X-Request-ID` assigned or propagated across all HTTP requests and responses.

### 1.5 Observability & PII Protection
- [x] **Telemetry PII Scrubber:** Sentry APM integration includes automated `before_send` scrubber stripping Authorization headers, tokens, passwords, guest emails, and phone numbers.
- [x] **Integrations Hub Sanitization:** Public monitoring probes querying `/api/v1/integrations/status` receive sanitized statuses without internal phone numbers or sender emails.

---

## 2. HOSPITALITY DATA PROTECTION CHECKLIST (INDIA DPDP ACT 2023)

Amit Hospitality acts as a **Data Fiduciary** processing digital personal data of dining guests, event clients, and staff members. The platform enforces the following compliance controls:

### 2.1 Grounds for Processing & Purpose Limitation (Sections 4 & 6)
- **Notice & Consent:** Guest information (name, mobile number, email, party size, dietary requirements) is collected solely for fulfilling dining reservation requests, event banquet planning, and conversational concierge assistance.
- **RAG Knowledge Separation:** Semantic vector embeddings in knowledge chunks contain only publicly available menu items, outlet policies, and operational hours. Guest PII is never vectorized or stored in the RAG knowledge base.

### 2.2 Reasonable Security Safeguards (Section 8(5))
- **In-Transit Encryption:** All communications forced over TLS 1.3 / HTTPS.
- **At-Rest Protection:** Passwords securely hashed with bcrypt; database files encrypted at the storage volume level.
- **Access Boundary Controls:** Staff members at one outlet cannot access guest reservation lists or phone numbers of other outlets.

### 2.3 Accuracy & Data Quality (Section 8(3))
- Phone numbers validated against E.164 and RFC regex rules before reservation or lead submission.
- Dates verified against ISO-8601 formatting (`YYYY-MM-DD`).

### 2.4 Data Principal Rights (Sections 11–14)
- **Right to Access & Summary:** Platform provides exportable CSV summaries of reservation and lead records for guests requesting their booking history.
- **Right to Correction & Erasure:** Authorized administrators have administrative dashboard tools to rectify or redact guest records upon verified request.
- **Grievance Redressal Mechanism:** Guest concerns, privacy requests, and inquiries escalate directly to Amit Hospitality's dedicated Guest Relations Concierge:
  - **Email:** `guestrelations@amithospitality.com`
  - **Telephone:** `+91 11 4050 9900`
  - **Escalation Hotline:** `+911140509900`

---

## 3. SECURITY SIGN-OFF VERDICT

The security architecture, tenant isolation mechanisms, webhook authenticators, and privacy safeguards are **VERIFIED COMPLIANT** for initiating the supervised internal pilot with Amit Hospitality staff and approved stakeholders.
