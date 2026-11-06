# AMIT AI CONCIERGE — REST API SPECIFICATION
## Comprehensive API Blueprint & Endpoint Contracts
**API Version:** v1  
**Base Path:** `/api/v1`  
**Protocol:** HTTPS / JSON  
**Auth Scheme:** Bearer JWT (`Authorization: Bearer <token>`)

---

## 1. Global Response & Error Conventions

### 1.1. Success Response Envelope
```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "environment": "DEMO",
    "timestamp": "2026-11-06T20:15:00Z"
  }
}
```

### 1.2. Error Response Envelope
```json
{
  "success": false,
  "error": {
    "code": "INVALID_ENVIRONMENT_TRANSITION",
    "message": "Only Super Admins may switch between DEMO and REAL modes.",
    "details": null
  }
}
```

---

## 2. Authentication & User Management Endpoints

| Method | Endpoint | Access Level | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/login` | Public | Authenticates credentials and returns JWT access & refresh tokens. |
| `POST` | `/api/v1/auth/logout` | Authenticated | Revokes current session token. |
| `GET` | `/api/v1/auth/me` | Authenticated | Returns current authenticated user profile, role, and permissions. |
| `POST` | `/api/v1/auth/refresh` | Public | Refreshes expired access token using valid refresh token. |
| `GET` | `/api/v1/users` | Super Admin | Lists all staff and management accounts. |
| `POST` | `/api/v1/users` | Super Admin | Creates a new staff or manager account. |

---

## 3. Environment Isolation & Control Endpoints

| Method | Endpoint | Access Level | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/environment/active` | Public / Admin | Returns active environment (`DEMO` or `REAL`), stats, and disclaimer details. |
| `POST` | `/api/v1/environment/switch` | Super Admin / Admin | Switches active system environment. Flushes caches and logs audit event. |

#### Request Body (`POST /api/v1/environment/switch`):
```json
{
  "target_environment": "REAL",
  "reason": "Transitioning from client demo to verified staging data.",
  "confirm_acknowledgment": true
}
```

---

## 4. Outlets, Menus & Catalog Endpoints

| Method | Endpoint | Access Level | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/outlets` | Public | Lists active outlets for current active environment. |
| `GET` | `/api/v1/outlets/{id}` | Public | Retrieves detailed outlet info (timings, dress code, cuisine). |
| `POST` | `/api/v1/outlets` | Admin | Adds a new outlet or dining space. |
| `GET` | `/api/v1/menus` | Public | Retrieves menus and items for an outlet (filtered by active environment). |
| `POST` | `/api/v1/menus/items` | Admin / Manager | Creates a new menu item with pricing and allergens. |
| `PUT` | `/api/v1/menus/items/{id}` | Admin / Manager | Updates pricing, descriptions, or availability. |
| `DELETE` | `/api/v1/menus/items/{id}` | Admin / Manager | Deactivates or removes a menu item. |

---

## 5. Knowledge Base & Document Ingestion Endpoints

| Method | Endpoint | Access Level | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/knowledge/documents` | Admin / Staff | Lists documents for specified environment (`DEMO` or `REAL`). |
| `POST` | `/api/v1/knowledge/upload` | Admin | Uploads PDF, DOCX, XLSX, CSV, or TXT for automated chunking and indexing. |
| `GET` | `/api/v1/knowledge/documents/{id}/chunks` | Admin | Inspects extracted chunks and vector embedding statuses. |
| `POST` | `/api/v1/knowledge/manual` | Admin | Manually creates a verified policy, FAQ, or information chunk. |
| `POST` | `/api/v1/knowledge/reindex` | Admin | Triggers re-embedding and vector re-indexing for all active documents. |
| `DELETE` | `/api/v1/knowledge/documents/{id}` | Admin | Deletes or deactivates a document and its indexed vectors. |

---

## 6. AI Concierge & Chat Endpoints

| Method | Endpoint | Access Level | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/chat/sessions` | Public | Initializes a new guest concierge session. |
| `POST` | `/api/v1/chat/messages` | Public | Submits guest query, runs grounded RAG against active environment, and streams/returns answer. |
| `GET` | `/api/v1/chat/sessions/{session_id}/history` | Public / Admin | Retrieves conversation history for active session. |
| `POST` | `/api/v1/chat/feedback` | Public | Collects guest thumbs up/down rating and comment on AI response. |
| `POST` | `/api/v1/chat/handover` | Public | Initiates human handover request for guest assistance. |

#### Request Body (`POST /api/v1/chat/messages`):
```json
{
  "session_id": "conv_9f81a7b8e",
  "outlet_id": 1,
  "message": "Do you have outdoor seating and what is the dress code for dinner?",
  "language": "EN"
}
```

#### Response:
```json
{
  "success": true,
  "data": {
    "reply": "At Amber Terrace, we offer panoramic outdoor rooftop seating with skyline views. Our dinner dress code is Smart Casual (collared shirts and tailored footwear recommended; sportswear is prohibited).",
    "environment": "DEMO",
    "is_demo": true,
    "citations": [
      {
        "document_title": "Amber Terrace Policies & Seating Guide",
        "category": "POLICY"
      }
    ],
    "suggested_actions": [
      "Book a rooftop table",
      "View dinner cocktail menu",
      "Check valet parking policy"
    ]
  }
}
```

---

## 7. Reservations & Table Requests Endpoints

| Method | Endpoint | Access Level | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/reservations` | Public | Submits guest reservation request (validated & tagged with environment). |
| `GET` | `/api/v1/reservations` | Staff / Admin | Lists reservation requests filtered by outlet, status, date, and environment. |
| `GET` | `/api/v1/reservations/{id}` | Staff / Admin | Retrieves full reservation details and guest contact notes. |
| `PATCH` | `/api/v1/reservations/{id}/status` | Staff / Admin | Updates status (`NEW`, `PENDING`, `ACCEPTED`, `REJECTED`, `CANCELLED`). |
| `POST` | `/api/v1/reservations/{id}/notes` | Staff / Admin | Adds staff internal coordination note. |
| `GET` | `/api/v1/reservations/export` | Admin | Exports reservation records to CSV/Excel. |

---

## 8. Leads & Event Inquiries Endpoints

| Method | Endpoint | Access Level | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/leads` | Public | Submits inquiry for private dining, weddings, corporate events. |
| `GET` | `/api/v1/leads` | Staff / Admin | Lists leads filtered by status, outlet, and date range. |
| `PATCH` | `/api/v1/leads/{id}/status` | Staff / Admin | Updates lead status (`CONTACTED`, `QUALIFIED`, `PROPOSAL_SENT`, `WON`, `LOST`). |
| `GET` | `/api/v1/leads/export` | Admin | Exports leads to CSV/Excel. |

---

## 9. Analytics & Business Intelligence Endpoints

| Method | Endpoint | Access Level | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/analytics/dashboard` | Admin / Manager | Returns KPIs: Total conversations, leads, booking requests, conversion rates. |
| `GET` | `/api/v1/analytics/frequent-queries` | Admin | Top customer questions, dietary queries, and outlet interest distribution. |
| `GET` | `/api/v1/analytics/unanswered` | Admin | Unanswered queries or low-confidence RAG lookups to guide knowledge expansion. |

---

## 10. Audit & Compliance Endpoints

| Method | Endpoint | Access Level | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/audit/logs` | Super Admin / Admin | Comprehensive audit log of all environment switches, knowledge alterations, and user actions. |

---

## 11. Website Embed Widget Endpoints

| Method | Endpoint | Access Level | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/widget/config/{outlet_slug}` | Public | Returns widget theme, branding, allowed domains, and active environment notice. |
| `GET` | `/api/v1/widget/loader.js` | Public | Serves the lightweight CDN loader script. |
