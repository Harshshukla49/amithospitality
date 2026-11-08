# AMIT AI CONCIERGE — PRODUCTION ENVIRONMENT GUIDE
**Configuration Profiles, Security Rules & Environment Separation**  
**Enterprise Hospitality Platform for Amit Hospitality**  
**Official Reference Website:** `https://amithospitality.com/`  

---

## 1. ENVIRONMENT PROFILES OVERVIEW

The **Amit AI Concierge** platform enforces strict architectural boundaries across four distinct runtime profiles:

| Configuration Variable | 1. Local Development | 2. Demo Environment | 3. Staging Environment | 4. Production Environment |
|---|---|---|---|---|
| `APP_ENV` | `development` | `demo` | `staging` | `production` |
| `DEFAULT_ENVIRONMENT` | `DEMO` | `DEMO` | `REAL` | `REAL` (or `DEMO` for sales) |
| `DATABASE_URL` | SQLite (`sqlite:///...`) | PostgreSQL or SQLite | PostgreSQL + pgvector | PostgreSQL + pgvector |
| `DEBUG` | `true` | `false` | `false` | `false` |
| `JWT_SECRET_KEY` | Dev Placeholder Allowed | Dedicated 64-char key | Dedicated 64-char key | Unique 64-char key ($\ge 32$) |
| `INITIAL_ADMIN_PASSWORD` | Default allowed | Custom generated | Custom generated | Strong unique ($\ge 12$ chars) |
| `RATE_LIMIT_PER_MINUTE` | 120 | 60 | 60 | 60 |
| `DB_POOL_SIZE` | N/A | 10 | 15 | 20 (with 10 overflow) |

---

## 2. PRODUCTION SAFEGUARDS ENFORCED AT STARTUP

When `APP_ENV=production`, the application executes startup assertions in [`config.py`](file:///c:/Users/india/Desktop/amit%20hospitality/backend/app/config.py). If any of the following checks fail, the process terminates immediately:

1. **Placeholder JWT Secret Rejection:**
   If `JWT_SECRET_KEY` equals `"amit_hospitality_super_secure_jwt_secret_key_2026_change_in_production"` or has length $< 32$ characters, the server raises `ValueError`.
2. **Default Admin Password Rejection:**
   If `INITIAL_ADMIN_PASSWORD` equals `"AmitConcierge2026!Secure"`, startup is halted.
3. **SQLite Prohibited in Production:**
   `DATABASE_URL` cannot start with `sqlite`. A PostgreSQL connection string is strictly required.
4. **Debug Mode Prohibited:**
   `DEBUG` must evaluate to `False`. Stack traces are suppressed from client responses.

---

## 3. DEMO VS. REAL MODE ISOLATION ARCHITECTURE

The application implements dual knowledge and reservation environments:

### Demo Mode Rules
- Fictional business data only (sample menus, tasting prices, demo policies).
- Watermark requirement: Every AI response generated from demo data includes `[DEMO DATA — Fictional Information for Demonstration Only]`.
- Requests submitted in Demo mode are tagged with `environment = "DEMO"` and never trigger real SMS, email, or table confirmations.

### Real Mode Rules
- Relies exclusively on verified Amit Hospitality documents, uploaded and verified by authorized administrators.
- If verified documentation does not exist for an inquiry, the AI states that verified company information is currently unavailable and directs the guest to official human channels (`guestrelations@amithospitality.com`).
- Requests submitted in Real mode are saved with `environment = "REAL"` for processing by hotel staff.

### Switching Modes
- Controlled via `POST /api/v1/environment/switch`.
- Mode changes require `SUPER_ADMIN` authorization and a mandatory audit reason.
- Every switch is logged to [`audit_logs`](file:///c:/Users/india/Desktop/amit%20hospitality/backend/app/models/audit.py).
- Switching modes does **NOT** delete or alter existing knowledge in either environment.

---

## 4. SECURE SECRETS & CREDENTIALS MANAGEMENT

### Generating Cryptographic Secrets
Generate a 256-bit random hex key for production:
```bash
openssl rand -hex 32
```
Example output:
```text
f8b1c43d7890e12a4567bcde34f12890abcdef1234567890abcdef1234567890
```

### Environment Variable Checklist for Production
```dotenv
APP_ENV=production
APP_NAME="Amit AI Concierge"
DEBUG=false
PORT=8000
HOST=0.0.0.0
DEFAULT_ENVIRONMENT=DEMO

# Security
JWT_SECRET_KEY=f8b1c43d7890e12a4567bcde34f12890abcdef1234567890abcdef1234567890
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_DAYS=7
INITIAL_ADMIN_EMAIL=admin@amithospitality.com
INITIAL_ADMIN_PASSWORD=K8#v9!Lm@4Pq$wR7

# Database (PostgreSQL + pgvector)
DATABASE_URL=postgresql+psycopg2://amit_admin:StrongPasswordHere@host:5432/amit_concierge
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=1800

# CORS
ALLOWED_ORIGINS="https://amit-concierge-ui.onrender.com,https://amithospitality.com,https://*.amithospitality.com"
UPLOAD_DIR=/var/data/uploads

# External Services
AI_PROVIDER=gemini
GEMINI_API_KEY=AIzaSy...your_gemini_api_key...
GEMINI_MODEL=gemini-1.5-flash
EMBEDDING_MODEL=text-embedding-004

# Meta WhatsApp Business Cloud API
WHATSAPP_TOKEN=EAAG...
WHATSAPP_PHONE_NUMBER_ID=10987654321
WHATSAPP_VERIFY_TOKEN=amit_whatsapp_verify_token_2026
WHATSAPP_APP_SECRET=meta_app_secret_here

# Twilio Telephony & SMS
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=auth_token_here
TWILIO_PHONE_NUMBER=+1234567890

# Guest Relations Hotline & Escalation Numbers
HOTLINE_PHONE_NUMBER="+91 11 4050 9900"
HOTLINE_EMAIL="guestrelations@amithospitality.com"
ESCALATION_PHONE_NUMBER="+911140509900"

# Transactional Notifications
SENDGRID_API_KEY=SG...
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=SG...
SMTP_FROM_EMAIL=concierge@amithospitality.com

# Caching & Observability
REDIS_URL=rediss://default:password@host:port/0
SENTRY_DSN=https://key@o123456.ingest.sentry.io/project
```

---

## 5. HEALTH PROBES & CONTAINER ORCHESTRATION

Production cloud container orchestrators (Kubernetes, AWS ECS, Render, GCP Cloud Run) must be configured with these probes:

1. **Liveness Probe:**
   - Path: `/api/v1/health/live`
   - Port: `8000`
   - Initial Delay: `10s`
   - Period: `10s`
   - Expected Response: `HTTP 200 {"live": True}`
2. **Readiness Probe:**
   - Path: `/api/v1/health/ready`
   - Port: `8000`
   - Initial Delay: `15s`
   - Period: `5s`
   - Failure Threshold: `3`
   - Expected Response: `HTTP 200 {"ready": True, "status": "healthy"}`
   - Unhealthy Response: `HTTP 503 {"ready": False, "status": "unhealthy", "reason": "Database unreachable"}`
3. **Observability & Diagnostics:**
   - Path: `/api/v1/health` (Detailed database latency and dialect)
   - Path: `/api/v1/integrations/status` (Operational status across all 7 external integrations)

