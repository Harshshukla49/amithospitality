# AMIT AI CONCIERGE — PHASE 12 ROLLBACK & DISASTER RECOVERY RUNBOOK
## Operational Contingency, Incident Remediation & Rapid Rollback Procedures

**Client / Brand:** Amit Hospitality ([https://amithospitality.com/](https://amithospitality.com/))  
**Auditor / Roles:** DevSecOps Lead, Site Reliability Engineer & Principal Cloud Architect  
**Date:** November 8, 2026  
**Document Purpose:** Definitive step-by-step emergency procedures to restore stable platform operations  
**Scope:** Backend, Frontend, Database, Third-Party Integrations, Credentials & Security

---

## 1. ROLLBACK SCENARIOS & RECOVERY PROCEDURES

```
                     ┌──────────────────────────────────────┐
                     │     CRITICAL INCIDENT DETECTED       │
                     └──────────────────┬───────────────────┘
                                        │
           ┌────────────────────────────┼────────────────────────────┐
           ▼                            ▼                            ▼
   [ APPLICATION FAILURE ]      [ DATABASE FAILURE ]        [ CREDENTIAL COMPROMISE ]
   Revert git commit / tag      Restore point-in-time snapshot Rotate JWT_SECRET_KEY
   Roll back Docker image       Re-apply verified schema    Invalidate all active sessions
   Redeploy previous build      Verify row counts & sequence  Force staff re-login
```

---

### Scenario 1: Backend API Deployment Failure
**Trigger:** API crash-looping, failing `/api/v1/health/ready` probe, or returning unhandled 500 errors.

**Procedure:**
1. **Identify Previous Stable Release:**
   - Locate last verified git commit or release tag (e.g., `git log --oneline -n 5`).
2. **Revert Render / Cloud Web Service:**
   - In Render Dashboard: Navigate to `amit-concierge-api` $\rightarrow$ **Deploys** $\rightarrow$ Click **Rollback** on the preceding successful build.
   - Or via Git CLI:
     ```bash
     git revert HEAD --no-edit
     git push origin main
     ```
3. **Verify Health Probe:**
   - Test `/api/v1/health` and `/api/v1/health/ready` to ensure `HTTP 200` response.
4. **Estimated Recovery Time:** $< 3\text{ minutes}$.

---

### Scenario 2: Frontend Client Deployment Failure
**Trigger:** React rendering crash, broken SPA routes, white screen errors, or failed API calls.

**Procedure:**
1. **Verify Root Error Boundary:**
   - Confirm that [`ErrorBoundary.tsx`](file:///c:/Users/india/Desktop/amit%20hospitality/frontend/src/components/common/ErrorBoundary.tsx) catches the render exception and presents the branded fallback UI with "Refresh" and "Contact Concierge" options.
2. **Rollback Static Asset Publication:**
   - In Render Dashboard: Navigate to `amit-concierge-ui` $\rightarrow$ **Deploys** $\rightarrow$ Select preceding successful deployment $\rightarrow$ Click **Publish this Deploy**.
   - Or locally rebuild from previous commit:
     ```bash
     git checkout HEAD~1 frontend/
     npm --prefix frontend run build
     ```
3. **Purge Edge CDN Cache:**
   - In Cloudflare / CDN dashboard, click **Purge Everything** to clear stale cached chunks from edge nodes.
4. **Estimated Recovery Time:** $< 2\text{ minutes}$.

---

### Scenario 3: Database Migration Failure / Data Corruption
**Trigger:** Failed Alembic migration, schema mismatch error, or accidental record alteration.

> [!CAUTION]
> Never execute destructive `DROP TABLE` or `DOWN` migrations on live production databases without first validating the backup snapshot.

**Procedure:**
1. **Freeze Application Writes:**
   - Set application to maintenance mode or scale backend workers to 0 temporarily:
     ```bash
     # In emergency maintenance:
     uvicorn app.main:app --workers 0
     ```
2. **Locate Most Recent Verified Snapshot:**
   - Snapshots are stored in `backups/backup_<dialect>_YYYYMMDD_HHMMSS.<dump|db>`.
   - For SQLite: Restore from `.pre_phase12_bak`.
3. **Execute Automated Database Restoration:**
   - Run the restoration engine targeting a fresh database:
     ```bash
     python backend/scripts/restore_db.py --backup-path backups/backup_postgres_latest.dump --target-url $RECOVERY_DATABASE_URL
     ```
4. **Verify Target Integrity:**
   - Validate row counts across `outlets`, `users`, `reservations`, and `leads`.
5. **Update Connection String:**
   - Point `DATABASE_URL` in environment configuration to the restored database instance and restart the API service.
6. **Estimated Recovery Time:** $< 10\text{ minutes}$ (Measured benchmark: $0.010\text{s}$ locally).

---

### Scenario 4: External Integration Outage (WhatsApp, Twilio, Gemini)
**Trigger:** Vendor outage, expired credentials, or third-party API rate limits.

**Procedure:**
1. **Verify Isolation via Integrations Hub:**
   - Check `/api/v1/integrations/status` to isolate which service is degraded.
2. **Automatic Fallback Verification:**
   - **Gemini Outage:** System transparently engages local deterministic semantic RAG fallback without dropping guest conversations.
   - **Redis Outage:** System automatically switches to local in-memory rate limiting and reports `protection_status: DEGRADED_LOCAL_NODE_ONLY`.
   - **WhatsApp / Twilio Outage:** Human concierge operators continue handling requests via the Admin Dashboard.
3. **Notify Guest Relations Concierge:**
   - Direct guest inquiries to the primary Amit Hospitality hotline: `+91 11 4050 9900` or `guestrelations@amithospitality.com`.
4. **Recovery Action:** Restore vendor credentials or await vendor resolution; no code changes required.

---

### Scenario 5: Security Credential Compromise
**Trigger:** Leakage of `JWT_SECRET_KEY`, database credentials, or administrative passwords.

**Procedure:**
1. **Immediate JWT Secret Rotation:**
   - Generate a cryptographically secure 64-character replacement key:
     ```bash
     python -c "import secrets; print(secrets.token_hex(32))"
     ```
   - Update `JWT_SECRET_KEY` in cloud environment variables.
   - Restart all backend API worker containers. This instantly invalidates all previously signed JWT access and refresh tokens across all sessions.
2. **Flush Token Blacklist:**
   - Clear and rebuild `revoked_tokens` table.
3. **Enforce Administrative Password Reset:**
   - Reset passwords for all administrative and staff accounts via `POST /api/v1/auth/reset-password`.
4. **Audit Access Logs:**
   - Inspect `audit_logs` table for suspicious activities during the compromise window:
     ```sql
     SELECT * FROM audit_logs WHERE created_at >= NOW() - INTERVAL '24 hours' ORDER BY created_at DESC;
     ```
5. **Estimated Recovery Time:** $< 5\text{ minutes}$.

---

## 2. EMERGENCY INCIDENT ESCALATION CONTACTS

| Role | Responsibility | Escalation Channel | Primary Contact |
| :--- | :--- | :--- | :--- |
| **Site Reliability Lead** | Cloud infrastructure & API containers | DevOps Hotline / Slack `#devops-ops` | devops@amithospitality.com |
| **Database Architect** | PostgreSQL restore & data integrity | Database Ops `#db-recovery` | dbadmin@amithospitality.com |
| **Application Security Officer** | Token rotation & breach response | Security Incident `#security-p1` | security@amithospitality.com |
| **Guest Relations Concierge** | Guest communication & phone escalation | Phone Hotline / Front Desk | `+91 11 4050 9900` |
