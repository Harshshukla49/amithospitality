# AMIT AI CONCIERGE — PHASE 20.1 VERIFICATION & AUDIT REPORT
## Security, Data Integrity & Production Reliability Audit

**Audit Status**: **PASS (ALL IDENTIFIED RISKS REMEDIATED & VERIFIED)**  
**Audit Date**: November 10, 2026  
**Repository**: `https://github.com/Harshshukla49/amithospitality.git`  
**Base Working Branch**: `phase-20-guest-self-service`  
**Audit Branch**: `phase-20-1-security-audit`  

---

## 1. Executive Summary & Audit Verdict

An exhaustive, evidence-based security, data integrity, and reliability audit of **Phase 20 (Unified Guest CRM & Secure Self-Service Experience)** was conducted directly against the backend codebase, database schemas, and frontend test suites.

### Final Verdict: **PASS**
All vulnerabilities and data integrity risks identified during the initial code inspection have been addressed with production-grade mitigations, covered with regression tests, and verified across **18 out of 18 backend test suites (100% pass)** and **4 out of 4 frontend test suites (18/18 tests pass)**.

---

## 2. Key Audit Findings & Remediations

### 2.1 OTP Cryptography & Offline Brute-Force Resistance
* **Audit Issue**: The Phase 20 implementation used unsalted `hashlib.sha256(otp_code)` for storing 6-digit OTPs. Because a 6-digit number has only $10^6$ combinations (100,000 to 999,999), an attacker with database read access could precompute a rainbow table or brute-force the plaintext OTP in under 1 second.
* **Remediation**:
  - Implemented `compute_otp_hmac(reference_id, otp_code)` which computes an **HMAC-SHA256** keyed with the server's private `JWT_SECRET_KEY` and cryptographically bound to the unique reservation `reference_id`:
    $$\text{token\_hash} = \text{HMAC-SHA256}(K=\text{JWT\_SECRET\_KEY}, M=\text{"otp:"} + \text{ref\_id} + \text{":"} + \text{otp})$$
  - Binds the verification token strictly to that specific booking. An OTP hash cannot be transferred, replayed, or precomputed without the server's secret.
  - Implemented constant-time comparison via `secrets.compare_digest` to prevent timing attacks.
  - Added a **60-second resend cooldown** (`HTTP 429`) to prevent OTP spamming.
  - Retained single-use invalidation (`is_used=True`) and hard lockout after 5 incorrect attempts.

### 2.2 Operating Hours Validation Logic
* **Audit Issue**: `GuestSelfService.modify_verified_reservation` contained the condition:
  `if target_time < open_t and target_time > close_t: raise HTTPException(...)`.
  Because of the logical `and`, this condition was mathematically impossible for standard hours (e.g., `< 12:00` AND `> 23:30`), completely bypassing operating-hour enforcement for self-service modifications!
* **Remediation**:
  - Rewrote the validation to properly evaluate daytime hours ($O \le T \le C$) and overnight hours (e.g. $18:00$ to $02:00$, where $T \ge O \lor T \le C$).
  - Verified with boundary tests: times like `04:00 AM` for a rooftop open `18:00` to `02:00` are strictly rejected with `HTTP 400`.

### 2.3 Guest Identity & Shared Household Disambiguation
* **Audit Issue**: Phase 20 deduplication matched solely on normalized phone or email without checking names. If a husband and wife (e.g., Rajesh Sharma and Priya Sharma) shared a household landline or family email, Priya's reservation was merged into Rajesh's profile, risking allergen cross-contamination (e.g. inheriting peanut allergies).
* **Remediation**:
  - Upgraded `GuestCrmService.resolve_or_create_guest_profile`:
    1. First looks for an exact identity match on contact **and** matching name.
    2. If the contact matches an existing profile with a *different* name, the system detects a shared household contact, creates an isolated profile for the individual, and sets `is_shared_contact = True`.
    3. Guarantees that dietary restrictions, medical allergies, and dining preferences remain strictly separated between distinct diners.
  - Added an in-process synchronization lock (`_resolution_lock = threading.Lock()`) around profile creation to eliminate duplicate profile creation under concurrent traffic.

### 2.4 Financial & Visit Metric Integrity
* **Audit Issue**: Phase 20 initialized `total_visits = 1` and incremented `total_visits` upon every booking reservation request, counting unverified, cancelled, and rejected requests as completed dining visits.
* **Remediation**:
  - Introduced `GuestCrmService.recompute_guest_metrics(db, guest_id)`:
    - `total_visits`: Total booking inquiries/visits logged in CRM.
    - `completed_visits`: Strictly reservations with lifecycle status `COMPLETED`.
    - `total_spend`: Real verified spend with currency `INR` and monetary precision rounded to 2 decimal places.
  - Automatically triggers metric recomputation when a reservation transitions to or from `COMPLETED`.
  - Disallows unverified booking estimates from being presented as actual settled revenue.

### 2.5 Reservation Modification Rejection Integrity
* **Audit Issue**: In `crm.py`, when a manager rejected a staged modification request (e.g. guest requesting 12 seats), the reservation was unconditionally transitioned to `ACCEPTED`. If the reservation was previously `CONFIRMED` or `NEW`, rejecting the party size increase corrupted the booking's prior status.
* **Remediation**:
  - Added `old_status` column to `ReservationModificationRequest`.
  - When a manager rejects a modification, the system reverts the reservation to `mod.old_status` (e.g. `CONFIRMED` $\to$ `UNDER_REVIEW` $\to$ `CONFIRMED`).
  - Added `NEW` to permitted target statuses from `UNDER_REVIEW` in `ALLOWED_TRANSITIONS`.

### 2.6 Notification Stale Claim Recovery & Max Retries
* **Audit Issue**: In `notification_service.py`, worker interruptions or crashes during atomic claiming could leave records in `CLAIMED` status indefinitely, or indefinitely retry every 60s without an attempt ceiling.
* **Remediation**:
  - Added `recover_stale_claims(max_age_seconds=180)`: automatically detects abandoned worker claims and transitions them to `FAILED` (for controlled retry) or `FAILED_PERMANENT` if `attempts >= 3`.
  - Added exponential backoff: $30\text{s} \times 2^{\text{attempts}-1}$ on subsequent failed retries.
  - Verified with 10 concurrent threads: exactly 1 worker wins the atomic database claim, and duplicate deliveries are suppressed.

### 2.7 Multi-Tenant RBAC & Guest Token Access Boundaries
* **Audit Issue**: Defense-in-depth: guest session JWTs had `type: "guest_access"`. While `get_current_user` failed due to missing user email, there was no explicit rejection guard for guest tokens on staff endpoints.
* **Remediation**:
  - Added explicit check in `get_current_user`: immediately raises `HTTP 403 Forbidden` if `payload.get("type") == "guest_access"`.
  - Added revocation check (`RevokedToken`) and strict scope validation (`scope == f"guest:reservation:{reference_id}"`) in `verify_guest_session_token`.
  - Verified multi-tenant cross-outlet isolation: Staff and Managers of Outlet 1 receive `HTTP 403 Forbidden` when attempting to inspect or modify guests/bookings of Outlet 2.

---

## 3. Database Migration Summary

**Migration**: `a1b2c3d4e5f6_005_phase20_1_security_and_financial_integrity.py`  
**Revises**: `9c0d1e2f3a4b` (Phase 20)

### Added Columns:
1. `guest_profiles.currency`: `VARCHAR(10)`, default `'INR'`.
2. `guest_profiles.is_shared_contact`: `BOOLEAN`, default `0`.
3. `reservation_modification_requests.old_status`: `VARCHAR(30)`, nullable.
4. `notification_logs.attempts`: `INTEGER`, default `1`.

All migrations utilize Alembic batch mode for seamless compatibility across both SQLite and PostgreSQL.

---

## 4. Test Evidence & Automated Verification

### 4.1 Master Regression Test Suite (Backend)
Command: `backend/venv/Scripts/python.exe -u backend/tests/run_all_tests.py`  
**Result: ALL 18 TEST SUITES PASSED (100%)**

| Suite | Name | Duration | Status |
|:---:|:---|:---:|:---:|
| 1 | Phase 2 — Direct Auth & Database Verification | 4.15s | **PASSED** |
| 2 | Phase 3 — Knowledge Base Management & Document Pipeline | 4.33s | **PASSED** |
| 3 | Phase 4 — AI Chatbot, Intent Detection & Grounded RAG | 4.57s | **PASSED** |
| 4 | Phase 5 — Reservation & Lead Management Workflows | 5.42s | **PASSED** |
| 5 | Phase 5 — Comprehensive Reservation & Lead Pipeline | 5.29s | **PASSED** |
| 6 | Phase 6 — Analytics, BI Reporting & Audit Trail Compliance | 3.61s | **PASSED** |
| 7 | Phase 7 — Multi-Outlet & Multilingual Concierge | 3.22s | **PASSED** |
| 8 | Phase 8 — Security Hardening, Prompt Injection & Rate Limiting | 3.55s | **PASSED** |
| 9 | Phase 9 — Production Infrastructure & Database Migration | 5.11s | **PASSED** |
| 10 | Phase 10 — Real AI, WhatsApp, Voice, Email & Enterprise Integrations | 3.71s | **PASSED** |
| 11 | Phase 11 — Enterprise QA, Security Validation & Reliability | 5.61s | **PASSED** |
| 12 | Phase 12 — Cloud Deployment, Infrastructure & Production Smoke | 6.40s | **PASSED** |
| 13 | Phase 14 — Real HTTP Integration, RBAC, Multi-Outlet Isolation & Streaming CSV | 5.72s | **PASSED** |
| 14 | Phase 15 — Database Reliability, Atomic Transactions & 20-Worker Concurrency | 5.76s | **PASSED** |
| 15 | Phase 17 — External Enterprise Integrations (Gemini, WhatsApp, Twilio, SendGrid, Redis, Sentry) | 3.24s | **PASSED** |
| 16 | Phase 19 — Live Outlets API, Multi-Outlet RBAC & Reservation Notification System | 5.83s | **PASSED** |
| 17 | Phase 20 — Unified Guest CRM & Secure Self-Service Experience | 6.10s | **PASSED** |
| 18 | **Phase 20.1 — Security, Data Integrity & Reliability Audit** | **3.90s** | **PASSED** |
| **TOTAL** | **18 Suites Executed** | **85.51s** | **100% PASSED** |

### 4.2 Phase 20.1 Dedicated Security Audit Suite
Script: `backend/tests/test_phase20_1_security_audit.py`  
- Test 1: OTP HMAC Cryptography, Rainbow Table Resistance & Attempt Lockouts — **PASSED**
- Test 2: Guest JWT Scope Isolation, IDOR Defense & Admin Protection — **PASSED**
- Test 3: Shared Family Phone Disambiguation & Concurrency Safety — **PASSED**
- Test 4: Completed Visit Metrics & Financial Precision — **PASSED**
- Test 5: Reservation Lifecycle, Manager Rejection & Operating Hours — **PASSED**
- Test 6: Atomic Claim Concurrency, Stale Recovery & Max Retries — **PASSED**
- Test 7: Multi-Tenant Isolation & Role Boundaries — **PASSED**

### 4.3 Frontend Test Suite & Bundle Verification
Command: `npm --prefix frontend run test -- --run`  
**Result: 4 passed files (18 / 18 tests passed) in 12.58s**
- `GuestSelfService.test.tsx` (4 tests passed)
- `GuestCrm.test.tsx` (4 tests passed)
- `OutletsPage.test.tsx` (4 tests passed)
- `Router.test.tsx` (6 tests passed)

Command: `npm --prefix frontend run build`  
**Result: Zero errors in 8.19s**
- `dist/index.html`: 1.38 kB
- `dist/assets/index-D472w7ve.css`: 44.38 kB
- `dist/assets/index-Dc9l9adE.js`: 474.92 kB

---

## 5. Files Changed in Phase 20.1

1. `backend/app/models/guest.py`: Added `currency`, `is_shared_contact` to `GuestProfile`; added `old_status` to `ReservationModificationRequest`.
2. `backend/app/models/notification.py`: Added `attempts` to `NotificationLog`.
3. `backend/app/schemas/guest.py`: Added `currency` and `is_shared_contact` fields to `GuestProfileResponse`.
4. `backend/app/services/guest_self_service.py`: Implemented HMAC-SHA256 OTP hashing with server secret binding, 60s resend cooldown, strict canonical contact matching, operating hours validation fix (day and overnight hours), and stored `old_status`.
5. `backend/app/services/guest_crm_service.py`: Added shared household disambiguation, thread-safe in-process resolution lock, and `recompute_guest_metrics`.
6. `backend/app/services/reservation_lifecycle_service.py`: Added `NEW` to allowed targets from `UNDER_REVIEW`; added `UNDER_REVIEW` to allowed targets from `ACCEPTED` and `CONFIRMED`; added automatic metrics recomputation on `COMPLETED`.
7. `backend/app/services/notification_service.py`: Added max 3-attempt ceiling, exponential backoff, and `recover_stale_claims`.
8. `backend/app/routers/crm.py`: Restored `mod.old_status` upon manager rejection.
9. `backend/app/routers/guest.py`: Added scope check and token revocation check in `verify_guest_session_token`.
10. `backend/app/utils/security.py`: Blocked guest tokens from `get_current_user`.
11. `backend/alembic/versions/a1b2c3d4e5f6_005_phase20_1_security_and_financial_integrity.py`: Created migration.
12. `backend/tests/test_phase20_1_security_audit.py`: Created comprehensive 7-suite test file.
13. `backend/tests/run_all_tests.py`: Added Phase 20.1 to master runner.
14. `backend/scripts/update_db_phase20_1.py`: Database synchronization utility.

---

## 6. Recommended Phase 21 Architecture

1. **Real-Time Table Seating Engine**: Dynamic floor plan allocation with server station load balancing.
2. **Server-Sent Events (SSE) / WebSockets**: Real-time push updates for table readiness directly to guest self-service screens without 15s REST polling.
3. **Guest Feedback & Net Promoter Score (NPS)**: Post-dining automated survey pipeline tied to verified `COMPLETED` reservations.
4. **Kitchen Display System (KDS) Integration**: Real-time course tracking and VIP dietary alert broadcasting.
