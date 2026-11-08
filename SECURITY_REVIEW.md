# AMIT AI CONCIERGE — SECURITY REVIEW & HARDENING AUDIT
**Enterprise Application Security Assessment**  
**Official Reference Website:** `https://amithospitality.com/`  
**Date:** November 8, 2026 | **Auditor:** Application Security & DevOps Lead  

---

## 1. EXECUTIVE SECURITY SUMMARY

This document provides a comprehensive security review of the **Amit AI Concierge** platform following Phase 9 infrastructure modernization and database migration hardening.

### Security Posture Matrix:
- **Authentication:** JWT with HS256, JTI tracking, automated token rotation, and explicit session revocation on logout.
- **Token Replay Protection:** Active. Attempting to consume an already-rotated refresh token immediately triggers `HTTP 401 Unauthorized`.
- **Authorization & RBAC:** Role hierarchies enforced at endpoint dependencies (`require_roles("SUPER_ADMIN", "ADMIN", "MANAGER", "STAFF")`).
- **Data Isolation:** Complete segregation between `DEMO` and `REAL` knowledge documents, menus, and reservation leads.
- **Tenant & Outlet Isolation:** Queries scoped strictly by `outlet_id`. Cross-outlet data leakage is prevented.
- **Injection Protection:** SQL injection eliminated through SQLAlchemy 2.0 parameterized queries and ORM object abstraction.
- **File Upload Security:** Strictly whitelisted extensions (`PDF, DOCX, XLSX, CSV, TXT`), 20MB payload ceiling, and path traversal sanitization.
- **Rate Limiting & DoS Mitigation:** Sliding-window rate limiting rejecting excess traffic with `HTTP 429 Too Many Requests`.

---

## 2. DETAILED SECURITY CONTROL ASSESSMENTS

### 2.1 JWT Token Lifecycle & Replay Protection
- **Token Claims:** Every token carries standard claims (`sub`, `role`, `exp`, `type`) and a cryptographically unique `jti` generated via `uuid.uuid4().hex`.
- **Rotation Architecture:**
  - When `/api/v1/auth/refresh` is invoked, the database verifies that the incoming `jti` is not in the [`revoked_tokens`](file:///c:/Users/india/Desktop/amit%20hospitality/backend/app/models/token.py) table.
  - If the token was previously consumed, the server flags a **Token Replay Attack** and terminates the session with `HTTP 401 Unauthorized`.
  - The valid refresh token is recorded as `ROTATED` in the revocation table and fresh tokens with new JTIs are generated.
- **Logout Invalidation:** `/api/v1/auth/logout` extracts the caller's active access token JTI and blacklists it with reason `LOGOUT`. Subsequent calls with that token are rejected.

### 2.2 Password Security & Hashing
- Utilizes PBKDF2 with bcrypt salt derivation (`bcrypt.hashpw` with 12 rounds of salt).
- Truncates passwords safely to 72 bytes to conform to standard bcrypt constraints while preventing denial-of-service through arbitrary payload sizes.
- Timing attack mitigation: `bcrypt.checkpw` performs constant-time comparisons.

### 2.3 Role-Based Access Control (RBAC)
- Enforced at the route dependency layer via [`require_roles`](file:///c:/Users/india/Desktop/amit%20hospitality/backend/app/utils/security.py):
  - `SUPER_ADMIN`: Environment switching, user creation, password resets.
  - `ADMIN`: Knowledge upload, document verification, outlet configuration.
  - `MANAGER`: Reservation review, lead assignment, analytics exports.
  - `STAFF`: Reservation status updates, lead status transitions.
- Tested: Attempting to access admin-restricted routes with a `STAFF` token immediately returns `HTTP 403 Forbidden`.

### 2.4 Multi-Outlet Tenant Isolation
- RAG retrieval in [`rag_service.py`](file:///c:/Users/india/Desktop/amit%20hospitality/backend/app/services/rag_service.py) scopes all document chunk searches to `(KnowledgeChunk.outlet_id == outlet_id) | (KnowledgeChunk.outlet_id == None)`.
- Prevents cross-contamination: Guests inquiring about *Amber Terrace Rooftop* cannot retrieve confidential pricing or policies belonging to *Saffron & Silk* or *The Velvet Cellar*.

### 2.5 File Upload Validation & Path Traversal Prevention
- **Whitelisting:** Enforces `ALLOWED_EXTENSIONS = {"PDF", "DOCX", "XLSX", "CSV", "TXT"}`. Files with executables, scripts, or unverified extensions (`.exe`, `.sh`, `.py`, `.bin`) are rejected with `HTTP 400 Bad Request`.
- **Payload Ceiling:** Capped at 20 MB (`MAX_UPLOAD_SIZE_BYTES = 20 * 1024 * 1024`). Files exceeding this size are unlinked from disk and rejected with `HTTP 413 Request Entity Too Large`.
- **Filename Sanitization:** Strips directory traversal sequences (`../`, `..\`) by computing `os.path.basename` and applying regex substitution `re.sub(r"[^\w\.-]", "_", base_name)` with unique timestamp prefixes.
- **Threadpool Execution:** File processing runs as a standard synchronous `def` so FastAPI executes CPU and disk tasks in an external worker thread without blocking the async event loop.

### 2.6 SQL Injection & Query Safety
- All dynamic query filters (e.g., date ranges, status filters, search queries) utilize SQLAlchemy ORM filter expressions (`.filter()`) or parameterized text constructs (`text("SELECT ... WHERE id = :id")`).
- Zero string-concatenated SQL queries exist in the codebase.

### 2.7 Cross-Site Scripting (XSS) & Content Security Policy (CSP)
- [`sanitize_input_text`](file:///c:/Users/india/Desktop/amit%20hospitality/backend/app/utils/security_middleware.py) strips script tags, HTML elements, and null bytes from incoming messages.
- Security middleware injects:
  - `X-Content-Type-Options: nosniff`
  - `X-XSS-Protection: 1; mode=block`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - `Content-Security-Policy`: Restricts frame ancestors to `https://amithospitality.com` and `https://*.amithospitality.com`.

### 2.8 Prompt Injection & Adversarial AI Interception
- [`detect_prompt_injection`](file:///c:/Users/india/Desktop/amit%20hospitality/backend/app/utils/security_middleware.py) identifies adversarial attempts to bypass guidelines or extract system prompts.
- Intercepted queries are handled safely without exposing internal reasoning or system prompt instructions.

### 2.9 Sensitive Information in Logs
- The platform configures structured logging that redacts passwords, tokens, API keys, and authorization headers from stdout and log files.

---

## 3. AUDIT CONCLUSION & COMPLIANCE VERIFICATION

The platform meets enterprise security standards for cloud production deployment. All automated tests in [`test_phase8_security.py`](file:///c:/Users/india/Desktop/amit%20hospitality/backend/tests/test_phase8_security.py) and [`test_phase9_postgres_migration.py`](file:///c:/Users/india/Desktop/amit%20hospitality/backend/tests/test_phase9_postgres_migration.py) passed.
