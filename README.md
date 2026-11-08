# Amit AI Concierge
## Enterprise AI Hospitality Management & Customer Concierge Platform

Amit AI Concierge is an advanced, production-oriented hospitality technology solution designed for luxury dining and hospitality brands like **Amit Hospitality** (https://amithospitality.com/).

It features an intelligent AI customer concierge, an executive management portal, dual-environment knowledge isolation (**DEMO vs. REAL Mode**), reservation request workflows, private event lead tracking, and real-time business intelligence.

---

## Key Features

1. **Dual-Environment Knowledge Isolation (DEMO & REAL):**
   - **DEMO Mode:** Includes realistic, fictional sample dining outlets, menus, dishes, prices, hours, and policies. Explicitly tagged as `DEMO DATA` so that it can never be mistaken for real company information.
   - **REAL Mode:** Dedicated repository for verified Amit Hospitality documents (PDF, DOCX, XLSX, CSV, TXT) and manually verified menu items and policies.
   - **Zero-Contamination Guarantee:** Hard architectural separation across relational tables, vector spaces, and system prompts. Switching environments purges caches, logs an immutable audit trail, and instantly alters AI retrieval scope.

2. **Luxury AI Guest Concierge:**
   - Multi-turn conversation with sub-second response times.
   - Strictly grounded RAG (Retrieval-Augmented Generation) preventing hallucinations.
   - Dual-language support (English & Hindi).
   - Seamless outlet switching, menu recommendations, dietary filtering, and reservation initiation.
   - Graceful fallback: If verified information is missing in REAL mode, the concierge politely defers to human staff rather than guessing.
   - Zero booking confirmation fabrication: Informs guests clearly that reservation submissions generate unique tracking IDs (`REF-RES-...`) awaiting human maître d' table review and allocation.

3. **Hospitality Operations Management (Phase 5 Complete):**
   - **Reservations Request & Maître d' Workflow:** Customer reservation form, capacity overflow detection, unique reference ID tracking (`REF-RES-YYYYMMDD-XXXX`), full status lifecycle (`NEW`, `PENDING`, `UNDER_REVIEW`, `ACCEPTED`, `COMPLETED`, `REJECTED`, `CANCELLED`), staff assignment, internal notes, and status transition audit history.
   - **Event & Lead Management Pipeline:** Tracks inquiries for private parties, corporate events, birthday celebrations, group bookings, wedding buyouts, and callbacks (`REF-LEAD-YYYYMMDD-XXXX`). Supports both AI chatbot and manual staff entry, stage transitions (`NEW`, `CONTACTED`, `QUALIFIED`, `FOLLOW_UP_REQUIRED`, `CONVERTED`, `CLOSED`), and CSV exports.
   - **Knowledge Base Studio:** Multi-format document uploader with automatic text extraction, semantic chunking, and vector indexing.
   - **Business Analytics:** Real-time metrics on guest inquiries, popular dishes, reservation trends, and unanswered question tracking.
   - **Security & RBAC:** Role-based access control (`Super Admin`, `Admin`, `Manager`, `Staff`) backed by secure JWT tokens.

---

## Technology Stack

- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Framer Motion, Lucide Icons.
- **Backend:** Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0, Uvicorn.
- **Database:** PostgreSQL 16 with `pgvector` (production) / SQLite dual-compatibility (zero-dependency development).
- **AI & RAG:** Google Gemini API / OpenAI / Local embeddings provider abstraction with cosine similarity retrieval.
- **Document Processing:** PyMuPDF (`fitz`), python-docx, openpyxl, pandas.
- **Containerization:** Docker & Docker Compose.

---

## Project Structure

```
amit-hospitality/
├── docs/                      # Comprehensive Architecture, Schema & Roadmaps
│   ├── ARCHITECTURE.md
│   ├── DATABASE_SCHEMA.md
│   ├── API_SPECIFICATION.md
│   └── DEVELOPMENT_ROADMAP.md
├── backend/                   # FastAPI Python Application
│   ├── app/
│   │   ├── models/            # SQLAlchemy ORM Models
│   │   ├── schemas/           # Pydantic Schemas
│   │   ├── routers/           # API Endpoints
│   │   ├── services/          # RAG, Document Parsing, Auth Services
│   │   └── utils/             # Security, Seed Data, Helpers
│   └── tests/                 # Automated Pytest Suite
├── frontend/                  # React + Vite + TypeScript Application
│   ├── src/
│   │   ├── components/        # Luxury Concierge & Admin UI
│   │   ├── context/           # Auth, Environment, & Chat State
│   │   └── pages/             # Guest and Management Views
│   └── widget/                # Standalone Embeddable Script
├── docker-compose.yml         # Container orchestration
└── .env.example               # Environment configuration template
```

---

## Quickstart Guide

### Prerequisites
- Node.js 18+ (tested with v24.15)
- Python 3.11+ (tested with v3.12.10)
- Git

### 1. Backend Setup
```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
cp ../.env.example .env

# Run database migrations and seed default demo data:
python -m app.utils.seed_data

# Start the FastAPI server:
uvicorn app.main:app --reload --port 8000
```
API Documentation will be available at: http://localhost:8000/docs

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Customer Concierge & Management Portal will be available at: http://localhost:5173

### 3. Master Test Verification
To run all automated test suites across all 7 development phases:
```bash
cd backend
python tests/run_all_tests.py
```

### 4. Embeddable Widget Integration
To embed the Amit AI Concierge onto any webpage on `https://amithospitality.com/`:
```html
<!-- Drop this single script tag into your website body -->
<script src="http://localhost:5173/widget.js" 
        data-outlet="amber-terrace" 
        data-accent-color="#D4AF37" 
        data-position="bottom-right"></script>
```
Test page available at: http://localhost:5173/embed-test.html

---

## Default Administrator Credentials
- **Email:** `admin@amithospitality.com`
- **Password:** `AmitConcierge2026!Secure`
- **Default Mode:** `DEMO MODE` (sample data preloaded)

---

## Executive Demonstration Walkthrough
For the complete 10-minute stakeholder presentation script and feature-by-feature demonstration guide, please refer to [docs/EXECUTIVE_DEMO_WALKTHROUGH.md](file:///c:/Users/india/Desktop/amit%20hospitality/docs/EXECUTIVE_DEMO_WALKTHROUGH.md).
