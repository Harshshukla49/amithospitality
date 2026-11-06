# AMIT AI CONCIERGE — MASTER DEVELOPMENT ROADMAP
## Phased Implementation Plan & Verification Status
**Document Version:** 1.0.0  
**Current Phase:** Phase 0 (Audit, Architecture, Schema & Roadmapping)

---

## Roadmap Overview

```
[✓] PHASE 0: Project Audit, Architecture, Schema & Roadmapping
[ ] PHASE 1: Premium Frontend & User Experience (Luxury UI, Concierge, Admin Dashboard)
[ ] PHASE 2: Backend Core, Database Layer & Authentication
[ ] PHASE 3: Dual-Environment Knowledge Base Management (DEMO vs REAL)
[ ] PHASE 4: Grounded AI Concierge & RAG Engine (Zero Hallucination)
[ ] PHASE 5: Reservation Requests & Lead Management Workflow
[ ] PHASE 6: Admin Analytics & Business Intelligence Dashboard
[ ] PHASE 7: Advanced Modules (Embeddable Widget, Multi-language EN/HI, Human Handover)
[ ] PHASE 8: Security Hardening, Automated Testing Suite & Verification
[ ] PHASE 9: Docker Containerization, Deployment & Demonstration Readiness
```

---

## Detailed Phase Breakdown & Acceptance Criteria

### Phase 0: Project Audit & Architecture
- [x] Inspect workspace and environment tooling (Python, Node, Docker, Git).
- [x] Initialize Git repository with secure `.gitignore`.
- [x] Author comprehensive System Architecture (`docs/ARCHITECTURE.md`).
- [x] Author Database Schema & pgvector specification (`docs/DATABASE_SCHEMA.md`).
- [x] Author complete REST API specification (`docs/API_SPECIFICATION.md`).
- [x] Author master Environment Configuration template (`.env.example`).
- [x] Author master README (`README.md`).
- [x] Setup baseline project directory structure.

### Phase 1: Premium Frontend & User Experience
- [ ] Initialize React 18+ with TypeScript and Vite.
- [ ] Configure Tailwind CSS luxury palette (Obsidian, Charcoal, Champagne Gold, Cream).
- [ ] Implement responsive luxury Customer Concierge Chatbot UI:
  - Welcome screen with Amit Hospitality branding.
  - Restaurant/outlet selector.
  - Suggested luxury prompt chips ("View Signature Tasting Menu", "Book Rooftop Table", etc.).
  - Conversational message feed with markdown rendering and citation chips.
  - Interactive typing indicators and animated states.
  - Prominent, elegant DEMO MODE indicator badge.
  - Mobile bottom sheet / responsive drawer.
- [ ] Implement Admin Dashboard layout:
  - Collapsible navigation sidebar.
  - Header with environment toggle indicator, quick search, and profile menu.
  - Summary metric cards with trends.
  - Data tables with sorting, filtering, and pagination.
  - Modal dialogues and confirmation flows.

### Phase 2: Backend Core, Database Layer & Authentication
- [ ] Initialize FastAPI application with modern async lifespan and CORS.
- [ ] Implement SQLAlchemy 2.0 ORM models for all 19 entities.
- [ ] Implement SQLite dual-compatibility fallback with numpy cosine similarity for zero-dependency local verification, paired with native PostgreSQL + pgvector for production.
- [ ] Implement JWT token generator, refresh tokens, and password hashing (bcrypt).
- [ ] Implement RBAC dependencies (`Super Admin`, `Admin`, `Manager`, `Staff`).
- [ ] Implement Seed Data script (`backend/app/utils/seed_data.py`) with rich DEMO outlet menus, FAQs, policies, and default admin.
- [ ] Verify authentication endpoints with automated tests.

### Phase 3: Dual-Environment Knowledge Base Management (DEMO vs REAL)
- [ ] Implement document ingestion service supporting PDF, DOCX, XLSX, CSV, and TXT.
- [ ] Build chunking engine with metadata tagging (`environment`, `outlet_id`, `category`).
- [ ] Build manual knowledge entry UI and API (custom policies, FAQs, timings).
- [ ] Implement secure Environment Switch API with confirmation token and audit logging.
- [ ] Implement automatic cache invalidation on environment transitions.
- [ ] Verify strict isolation: confirm zero query leakage between DEMO and REAL stores.

### Phase 4: Grounded AI Concierge & RAG Engine
- [ ] Implement AI Provider abstraction supporting Google Gemini (with fallbacks for offline/mock evaluation).
- [ ] Build vector retrieval engine with outlet and environment filtering.
- [ ] Formulate strict hospitality grounding system prompts with anti-hallucination guardrails.
- [ ] Support English and Hindi conversational queries.
- [ ] Implement conversation session persistence and message history tracking.
- [ ] Add guest feedback capture (thumbs up/down + comments).

### Phase 5: Reservation Requests & Lead Management Workflow
- [ ] Build luxury guest reservation booking form with date, time, party size, seating preference, and special requests.
- [ ] Implement stateful reservation workflow (`NEW` -> `PENDING` -> `ACCEPTED` -> `REJECTED` -> `CANCELLED`).
- [ ] Build staff reservation management drawer with internal notes and status updates.
- [ ] Build Event & Lead capture module for private dining and celebrations.
- [ ] Implement export functionality (CSV/Excel).
- [ ] Add explicit DEMO disclaimers for simulated reservation requests.

### Phase 6: Admin Analytics & Business Intelligence Dashboard
- [ ] Build real-time analytics aggregation queries.
- [ ] Render interactive charts: conversation volume, lead pipeline, popular dishes, busiest reservation windows.
- [ ] Implement Unanswered Questions tracker to spotlight knowledge gaps.
- [ ] Provide date-range and outlet-specific filtering.

### Phase 7: Advanced Modules & Integrations
- [ ] Build embeddable standalone website widget (`concierge-widget.js`) with isolated styles.
- [ ] Implement Hindi and English language auto-detection and translation assistance.
- [ ] Implement Human Handover escalation workflow with staff notification triggers.
- [ ] Implement Voice Assistant interface stub with browser Web Speech API.

### Phase 8: Security Hardening, Automated Testing Suite & Verification
- [ ] Run comprehensive automated pytest suite covering:
  - Authentication and RBAC violations.
  - DEMO vs REAL isolation invariants.
  - Reservation state transitions.
  - RAG vector retrieval filtering.
- [ ] Implement rate limiting, secure headers, and file upload MIME verification.
- [ ] Validate responsive layouts on simulated mobile, tablet, and desktop viewports.

### Phase 9: Docker Containerization, Deployment & Demonstration Readiness
- [ ] Author production `Dockerfile.backend` and `Dockerfile.frontend`.
- [ ] Author `docker-compose.yml` for unified multi-container orchestration.
- [ ] Author detailed Deployment & Disaster Recovery Guide.
- [ ] Create step-by-step Demonstration Script showcasing DEMO -> REAL transition, menu updates, and live AI grounding.
