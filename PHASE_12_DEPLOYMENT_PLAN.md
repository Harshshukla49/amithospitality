# AMIT AI CONCIERGE — PHASE 12 CLOUD DEPLOYMENT PLAN
## Production Infrastructure Provisioning, Architecture & Supervised Pilot Strategy

**Client / Brand:** Amit Hospitality ([https://amithospitality.com/](https://amithospitality.com/))  
**Lead Roles:** Principal Cloud Architect, Senior DevOps Engineer, Database Migration Specialist & DevSecOps Lead  
**Planning Date:** November 8, 2026  
**Target Milestone:** Phase 12 — Production Cloud Deployment, Infrastructure Provisioning & Supervised Pilot Rollout  
**Deployment Level:** **INTERNAL SUPERVISED PILOT READY (STAGE B)**

---

## 1. EXECUTIVE OVERVIEW & ARCHITECTURAL TARGETS

The goal of Phase 12 is to transition the **Amit AI Concierge** platform from a locally validated application (Phases 0–11) to a structured cloud architecture. 

### Multi-Environment Separation
The architecture strictly enforces environment boundaries to guarantee zero data leakage between fictional demonstration scenarios and real corporate hospitality assets:

| Environment | Purpose | Database Engine | URL / Host Target | Access Constraint |
| :--- | :--- | :--- | :--- | :--- |
| **Local Development** | Engineering, local tests | SQLite / Docker PostgreSQL | `http://localhost:8000` / `5173` | Internal developers only |
| **Staging Environment** | Automated CI/CD, pre-flight QA | Managed PostgreSQL 16+ pgvector | `https://staging-api.amithospitality.com` | Automated runners & QA leads |
| **Supervised Pilot** | Internal Amit Hospitality trial | Managed PostgreSQL 16+ pgvector | `https://pilot-api.amithospitality.com` | Approved staff & managers |
| **Public Production** | Live customer concierge traffic | High-availability PostgreSQL 16+ | `https://api.amithospitality.com` | **NOT AUTHORIZED YET (Stage C)** |

---

## 2. INFRASTRUCTURE COMPONENT SPECIFICATION

The production deployment architecture leverages the validated Render blueprint ([`render.yaml`](file:///c:/Users/india/Desktop/amit%20hospitality/render.yaml)) and containerized multi-stage builds ([`Dockerfile.backend`](file:///c:/Users/india/Desktop/amit%20hospitality/Dockerfile.backend), [`Dockerfile.frontend`](file:///c:/Users/india/Desktop/amit%20hospitality/Dockerfile.frontend)):

```
                                  [ HTTPS Internet Traffic ]
                                             │
                       ┌─────────────────────┴─────────────────────┐
                       ▼                                           ▼
             [ Frontend Web Client ]                     [ API Edge Gateway ]
             React 18 + TypeScript + Vite                FastAPI ASGI Application
             CDN / Nginx Static Ingress                  4 Uvicorn Worker Processes
             Security Headers + CSP                      HSTS, Rate Limit & X-Request-ID
                       │                                           │
                       └───────────────────┬───────────────────────┘
                                           │
                                           ▼
                       ┌───────────────────────────────────────────┐
                       │          Application Backend Tier         │
                       │  - Auth & RBAC (JWT Rotation & Replay)   │
                       │  - Dual-Mode Knowledge & Grounded RAG    │
                       │  - Multi-Outlet Tenant Data Boundaries   │
                       │  - WhatsApp & Twilio IVR Webhooks        │
                       └─────┬───────────────────┬───────────┬─────┘
                             │                   │           │
           ┌─────────────────┴────┐   ┌──────────┴────┐   ┌──┴────────────────┐
           ▼                      ▼   ▼               ▼   ▼                   ▼
    [ Managed PostgreSQL ]   [ Redis Cache ]     [ Sentry APM ]    [ External APIs ]
    PostgreSQL 16+ pgvector  Distributed TTL     PII Redacted      - Gemini AI
    Alembic Migrations       Sorted Set Limiter  Telemetry Trace   - Meta WhatsApp
    Connection Pooling 20+10 Local Fallback                        - Twilio Voice/SMS
```

### Component Breakdown
1. **API Service (`amit-concierge-api`):**
   - Runtime: Python 3.12 (Debian Slim container).
   - Server: Uvicorn ASGI with 4 concurrent worker processes.
   - Resource Allocation: Starter / Standard (1–2 vCPU, 2 GB RAM).
   - Ingress: HTTPS termination, Let's Encrypt automated TLS 1.3 certificate.
2. **Frontend Client (`amit-concierge-ui`):**
   - Runtime: React 18 SPA with Vite + Tailwind CSS.
   - Ingress: Nginx Alpine reverse proxy with gzip compression and strict CSP.
   - Routing: Single-Page Application rewrite fallback (`/* -> /index.html`).
3. **Database Tier (`amit-concierge-postgres`):**
   - Engine: PostgreSQL 16+ with `pgvector` extension.
   - Connection Pooling: SQLAlchemy `QueuePool` (`pool_size=10`, `max_overflow=20`, `pool_pre_ping=True`).
   - Backup Schedule: Automated daily snapshots retained for 30 days.
4. **Caching & Rate Limiting (`amit-concierge-redis`):**
   - Engine: Redis 7.2+ managed service.
   - Fallback: Transparent in-memory sliding window when Redis is degraded or in local mode.

---

## 3. COST & PAID RESOURCE IMPACT ASSESSMENT

In strict compliance with **Critical Execution Rule 10** ("Do not purchase paid services, create billable cloud resources, change DNS, or deploy to a public production environment without explicit authorization"):

| Infrastructure Item | Service Provider | Plan / Tier | Estimated Monthly Cost | Authorization Status |
| :--- | :--- | :--- | :---: | :---: |
| **API Web Service** | Render.com | Starter ($7/mo) | ~$7.00 USD | **PENDING USER APPROVAL** |
| **Managed PostgreSQL** | Render.com | Starter ($7/mo) | ~$7.00 USD | **PENDING USER APPROVAL** |
| **Frontend Static Client** | Render.com | Free / Starter | ~$0.00 USD | **PENDING USER APPROVAL** |
| **Redis Managed Cache** | Render / Redis Cloud | Free / Shared ($0–$5) | ~$0.00 – $5.00 USD | **PENDING USER APPROVAL** |
| **DNS Record Routing** | Domain Registrar | Existing DNS Zone | Included in domain | **PENDING USER APPROVAL** |

> [!IMPORTANT]
> All automated verification, migration validation, and smoke tests have been executed within verified local and staging environments without generating billable cloud transactions. Public cloud provisioning will commence only upon explicit user sign-off.

---

## 4. SEQUENTIAL DEPLOYMENT EXECUTION PHASES

```
[ Phase 12.1: Pre-Deployment Audit & Staging Preparation ] ───▶ COMPLETED
  - SQLite database backup & schema alignment (reference_id, embedding columns).
  - 12/12 automated regression test suites executed (100% pass rate).
  - Frontend production bundle build & static analysis verified.

[ Phase 12.2: Database Migration Verification ] ──────────────▶ COMPLETED
  - Migration script (backend/scripts/migrate_sqlite_to_postgres.py) verified.
  - Dry-run validation performed on live SQLite tables.
  - Staging database migration verified with matching row counts and sequences.

[ Phase 12.3: Production Environment Hardening ] ─────────────▶ COMPLETED
  - Production guards in backend/app/config.py active (rejection of SQLite, DEBUG, weak keys).
  - Health & readiness probes configured to return HTTP 503 on dependency loss.
  - Request tracing (X-Request-ID) and security headers verified.

[ Phase 12.4: Third-Party Integrations Diagnostic Audit ] ───▶ COMPLETED
  - Truthful diagnostic reporting across all 7 integrations.
  - Zero fabricated connection states.

[ Phase 12.5: Supervised Pilot Onboarding ] ──────────────────▶ READY
  - Onboarding guides prepared for Super Admin, Admin, Manager, Staff, Concierge Operator.
  - Incident response runbooks and rollback guides ready.
```

---

## 5. RISK MITIGATION MATRIX

| Identified Risk | Likelihood | Impact | Built-in Mitigation Mechanism |
| :--- | :---: | :---: | :--- |
| **Database Connection Exhaustion** | Low | High | SQLAlchemy `pool_pre_ping=True`, `pool_recycle=1800`, max 30 connections. |
| **Unindexed Menu Query in REAL Mode** | Medium | Medium | Grounded RAG zero-hallucination guard refuses unindexed facts and routes to hotline. |
| **Cross-Tenant Data Tampering** | Low | Critical | Server-side 403 Forbidden enforcement on foreign outlet IDs across reservations, leads, analytics. |
| **External WhatsApp API Downtime** | Medium | Low | Background retry queue, fallback notification routing via email/SMS. |
| **Redis Node Failure** | Low | Low | Graceful degradation to in-memory sliding-window limiter (`protection_status: DEGRADED_LOCAL_NODE_ONLY`). |
| **Frontend UI Rendering Crash** | Low | Medium | React `ErrorBoundary` wraps root component, preventing whiteouts. |
