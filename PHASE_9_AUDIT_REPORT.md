# AMIT AI CONCIERGE — PHASE 9 AUDIT REPORT
**Production Infrastructure & Database Migration Audit**  
**Official Reference Website:** `https://amithospitality.com/`  
**Date:** November 8, 2026 | **Auditor:** Senior DevOps Architect & Application Security Engineer  

---

## 1. PROJECT ARCHITECTURE & REPOSITORY AUDIT

### 1.1 Overview & System Components
- **System Name:** Amit AI Concierge
- **Organization:** Amit Hospitality
- **Current Completion:** Phase 0–8 verified (8/8 backend test suites, frontend 0-error build)
- **Frontend Stack:** React 18, Vite, TypeScript, Tailwind CSS, Framer Motion, Lucide Icons
- **Backend Stack:** Python 3.12, FastAPI, SQLAlchemy 2.0 ORM, Alembic, Pydantic v2
- **Source Database:** SQLite (`amit_concierge.db`)
- **Target Database:** PostgreSQL 16+ with `pgvector` extension

### 1.2 Audited Configuration Files
- [`backend/requirements.txt`](file:///c:/Users/india/Desktop/amit%20hospitality/backend/requirements.txt):
  - Verified inclusion of `alembic>=1.13.1`, `psycopg2-binary>=2.9.9`, and `pgvector>=0.2.5`.
  - Installed and verified all PostgreSQL and migration binaries in the virtual environment.
- [`frontend/package.json`](file:///c:/Users/india/Desktop/amit%20hospitality/frontend/package.json):
  - Dependencies: React 18, TypeScript 5.5, Vite 5.4, Lucide React, Axios. Builds cleanly via `npm run build`.
- [`.env.example`](file:///c:/Users/india/Desktop/amit%20hospitality/.env.example):
  - Previously lacked complete separation between local, demo, staging, and production profiles.
  - Remediated to provide granular environment parameters, database pooling, and integration placeholders.
- [`docker-compose.yml`](file:///c:/Users/india/Desktop/amit%20hospitality/docker-compose.yml):
  - Includes `pgvector/pgvector:pg16` image, backend API container, and frontend web container.
- Containerization Assets:
  - Discovered that [`Dockerfile.frontend`](file:///c:/Users/india/Desktop/amit%20hospitality/Dockerfile.frontend) specified `COPY nginx.conf /etc/nginx/conf.d/default.conf`, but [`frontend/nginx.conf`](file:///c:/Users/india/Desktop/amit%20hospitality/frontend/nginx.conf) was missing. Generated a hardened, production-ready Nginx configuration with security headers and SPA routing.

---

## 2. DATABASE MODELS & SQLITE DEPENDENCY AUDIT

### 2.1 Complete Relational Model Inventory (18 Tables)
| Model Class | Database Table | Key Attributes & Foreign Keys | SQLite Affinity / PostgreSQL Type |
|---|---|---|---|
| `EnvironmentSetting` | `environment_settings` | `active_environment`, `switch_reason` | Text / VARCHAR |
| `AuditLog` | `audit_logs` | `action`, `user_role`, `environment`, `details` | Foreign Key to `users.id` |
| `Restaurant` | `restaurants` | `name`, `slug`, `description` | Primary parent entity |
| `Outlet` | `outlets` | `restaurant_id`, `name`, `slug`, `outlet_type`, `dress_code` | Foreign Key to `restaurants.id` |
| `MenuCategory` | `menu_categories` | `outlet_id`, `name`, `display_order` | Foreign Key to `outlets.id` |
| `MenuItem` | `menu_items` | `outlet_id`, `environment`, `name`, `price` | Foreign Key to `outlets.id` |
| `User` | `users` | `email`, `password_hash`, `role`, `is_active` | RBAC core table |
| `AIConfiguration` | `ai_configs` | `provider`, `model_name`, `temperature` | Mode-specific settings |
| `KnowledgeDocument` | `knowledge_documents` | `outlet_id`, `environment`, `title`, `file_path` | Foreign Key to `outlets.id` |
| `KnowledgeChunk` | `knowledge_chunks` | `document_id`, `content`, `embedding_json`, `embedding` | Foreign Key to `knowledge_documents.id`; `vector(256)` |
| `Policy` | `policies` | `outlet_id`, `environment`, `policy_type` | Foreign Key to `outlets.id` |
| `FAQ` | `faqs` | `outlet_id`, `environment`, `question`, `answer` | Foreign Key to `outlets.id` |
| `Customer` | `customers` | `phone`, `name`, `email` | Unique phone index |
| `Conversation` | `conversations` | `customer_id`, `outlet_id`, `environment` | Foreign Key to `customers.id`, `outlets.id` |
| `Message` | `messages` | `conversation_id`, `sender_type`, `content` | Foreign Key to `conversations.id` |
| `ReservationRequest` | `reservation_requests` | `reference_id`, `outlet_id`, `guest_name`, `status` | Foreign Key to `outlets.id` |
| `ReservationStatusHistory` | `reservation_status_history` | `reservation_id`, `changed_by_user_id`, `new_status` | Foreign Key to `reservation_requests.id`, `users.id` |
| `Lead` | `leads` | `reference_id`, `outlet_id`, `name`, `enquiry_type`, `status` | Foreign Key to `outlets.id` |
| `LeadStatusHistory` | `lead_status_history` | `lead_id`, `changed_by_user_id`, `new_status` | Foreign Key to `leads.id`, `users.id` |
| `RevokedToken` | `revoked_tokens` | `jti`, `token_type`, `user_id`, `expires_at` | Token revocation & replay defense |

### 2.2 SQLite Dependencies Identified & Remediated
1. **Thread Check:** SQLite requires `connect_args={"check_same_thread": False}`. PostgreSQL rejects this argument. Remediated in [`database.py`](file:///c:/Users/india/Desktop/amit%20hospitality/backend/app/database.py) with conditional connection arguments.
2. **Connection Pooling:** SQLite operates best with `NullPool` or `StaticPool`. PostgreSQL requires production pool settings (`pool_size=20`, `max_overflow=10`, `pool_pre_ping=True`, `pool_recycle=1800`). Added production engine configuration.
3. **Semantic Embeddings:** SQLite stored vector embeddings as JSON strings (`embedding_json`). PostgreSQL supports native vector similarity via `pgvector`. Added `embedding = Column(Vector(256), nullable=True)` to [`KnowledgeChunk`](file:///c:/Users/india/Desktop/amit%20hospitality/backend/app/models/knowledge.py), maintaining dual compatibility.
4. **URL Normalization:** Cloud platforms (Render, Heroku, Supabase) often inject `postgres://` URLs, which SQLAlchemy 2.0 rejects. Implemented automatic URL normalization to `postgresql+psycopg2://` in [`Settings.clean_database_url`](file:///c:/Users/india/Desktop/amit%20hospitality/backend/app/config.py).

---

## 3. SECURITY & TOKEN LIFECYCLE AUDIT

### 3.1 Deficiencies Discovered
1. **Unchecked Token Replay:** Refresh tokens were stateless JWTs. A stolen or already-used refresh token could be replayed repeatedly until expiration.
2. **Default Secrets in Production:** `Settings` previously defaulted `JWT_SECRET_KEY` and `INITIAL_ADMIN_PASSWORD` to development placeholders without verifying that `APP_ENV != "production"`.
3. **Missing Token Revocation on Logout:** Stateless token issuance meant users logging out left tokens valid until their expiration timestamp.

### 3.2 Remediations Implemented
1. Added unique `jti` (JWT ID) generation via `uuid.uuid4().hex` to all access and refresh tokens.
2. Created the [`RevokedToken`](file:///c:/Users/india/Desktop/amit%20hospitality/backend/app/models/token.py) table to record consumed, rotated, and logged-out token identifiers.
3. Implemented token rotation in [`auth.py`](file:///c:/Users/india/Desktop/amit%20hospitality/backend/app/routers/auth.py): When a refresh token is presented, its JTI is marked as `ROTATED`. If presented again, the system detects a token replay attack and raises `401 Unauthorized`.
4. Enhanced [`logout`](file:///c:/Users/india/Desktop/amit%20hospitality/backend/app/routers/auth.py) to revoke the caller's active token session.
5. Added Pydantic model validation in [`config.py`](file:///c:/Users/india/Desktop/amit%20hospitality/backend/app/config.py) to block startup in production mode if placeholder secrets, default passwords, or SQLite URLs are detected.

---

## 4. DEPLOYMENT & PRODUCTION READINESS AUDIT

- **Alembic Migrations:** Initialized and configured [`backend/alembic`](file:///c:/Users/india/Desktop/amit%20hospitality/backend/alembic) with automated `CREATE EXTENSION IF NOT EXISTS vector;` execution for PostgreSQL.
- **Data Migration Script:** Created [`scripts/migrate_sqlite_to_postgres.py`](file:///c:/Users/india/Desktop/amit%20hospitality/backend/scripts/migrate_sqlite_to_postgres.py) with batching, date parsing, sequence resets, and dry-run verification.
- **Render Blueprint:** Created [`render.yaml`](file:///c:/Users/india/Desktop/amit%20hospitality/render.yaml) for single-click deployment of PostgreSQL + pgvector, FastAPI web service, and React static frontend.
- **Third-Party Readiness:** Created [`integrations.py`](file:///c:/Users/india/Desktop/amit%20hospitality/backend/app/routers/integrations.py) diagnostic endpoint to report live configuration status for Gemini, WhatsApp, Twilio, Email, SMS, and Redis without fabricating fake connections.
