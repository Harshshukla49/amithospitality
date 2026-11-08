# AMIT AI CONCIERGE — DATABASE MIGRATION GUIDE
**SQLite to PostgreSQL + pgvector Migration & Operation Manual**  
**Enterprise Hospitality Platform for Amit Hospitality**  
**Official Reference Website:** `https://amithospitality.com/`  

---

## 1. ARCHITECTURE OVERVIEW

The **Amit AI Concierge** platform uses a dual-engine database architecture:
- **Development & Offline Testing:** SQLite 3 (`amit_concierge.db`) with localized stringified vector embedding storage (`embedding_json`) and Python-based cosine similarity.
- **Production & Staging:** PostgreSQL 16+ with the `pgvector` extension for native vector indexing and sub-millisecond semantic search over knowledge documents and menu items.

---

## 2. PREREQUISITES & ENVIRONMENT SETUP

### 2.1 Managed PostgreSQL Requirements
- PostgreSQL version $\ge 15.0$ (version 16 recommended).
- `pgvector` extension installed on the database host.
- Python packages installed (defined in [`backend/requirements.txt`](file:///c:/Users/india/Desktop/amit%20hospitality/backend/requirements.txt)):
  ```bash
  pip install psycopg2-binary pgvector alembic
  ```

### 2.2 Enabling pgvector Manually (if required)
If your database user is not a superuser, ensure your database administrator executes:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

---

## 3. STEP-BY-STEP MIGRATION WORKFLOW

### Step 1: Backup Source SQLite Database
Before starting any migration, generate an archive copy:
```bash
python backend/scripts/backup_db.py ./backups
```
This produces a snapshot such as `./backups/backup_sqlite_20261108_183000.db`.

### Step 2: Configure Target PostgreSQL Connection
Set the `DATABASE_URL` environment variable:
```bash
export DATABASE_URL="postgresql+psycopg2://postgres:your_secure_password@localhost:5432/amit_concierge"
```
*(On Windows PowerShell, use `$env:DATABASE_URL="..."`)*

### Step 3: Run Alembic Schema Upgrade
Apply the initial schema and pgvector definitions on the target database:
```bash
cd backend
python -m alembic upgrade head
```

### Step 4: Perform Dry-Run Migration
Validate source connectivity and obtain preview row counts without altering the target database:
```bash
python backend/scripts/migrate_sqlite_to_postgres.py \
  --sqlite-path backend/amit_concierge.db \
  --postgres-url "$DATABASE_URL" \
  --dry-run
```
Expected output:
```text
2026-11-08 [INFO] Execution Mode : DRY RUN (Preview)
2026-11-08 [INFO] [OK] Source SQLite database connected successfully.
2026-11-08 [INFO] [OK] Target database connected successfully.
2026-11-08 [INFO] Processing table 'outlets': 3 rows found in source.
...
2026-11-08 [INFO] MIGRATION COMPLETE: 0 total records processed.
```

### Step 5: Execute Live Migration
Transfer all relational rows, foreign keys, and vector embeddings:
```bash
python backend/scripts/migrate_sqlite_to_postgres.py \
  --sqlite-path backend/amit_concierge.db \
  --postgres-url "$DATABASE_URL" \
  --batch-size 500
```
This utility:
1. Sequentially streams tables in foreign-key dependency order.
2. Converts SQLite ISO strings to native `datetime` objects.
3. Automatically populates `knowledge_chunks.embedding` using vectors from `embedding_json`.
4. Resets all PostgreSQL serial sequences using `SELECT setval(pg_get_serial_sequence(...))` so subsequent `INSERT` operations generate contiguous IDs without conflict.
5. Verifies source count vs. target count.
6. **NEVER** deletes or modifies the source SQLite file.

---

## 4. VERIFICATION & VALIDATION CHECKS

Execute the health check endpoint to confirm connectivity and response latency:
```bash
curl http://localhost:8000/api/v1/health
```
Expected JSON response:
```json
{
  "status": "healthy",
  "app_name": "Amit AI Concierge",
  "app_env": "production",
  "version": "1.0.0",
  "database": {
    "status": "healthy",
    "dialect": "postgresql",
    "latency_ms": 2.15,
    "connected": true
  },
  "default_environment": "DEMO"
}
```

### PostgreSQL Semantic Vector Index Verification
Verify that the `embedding` column exists and contains 256-dimensional vectors:
```sql
SELECT id, document_id, length(embedding_json), embedding 
FROM knowledge_chunks 
WHERE embedding IS NOT NULL 
LIMIT 1;
```

To create an IVFFlat or HNSW cosine similarity index for production scale:
```sql
CREATE INDEX IF NOT EXISTS ix_knowledge_chunks_embedding 
ON knowledge_chunks 
USING hnsw (embedding vector_cosine_ops);
```

---

## 5. ROLLBACK & DISASTER RECOVERY PROCEDURES

If migration fails or data discrepancies occur during cutover:

1. **Immediate Rollback to SQLite:**
   Update `.env`:
   ```dotenv
   DATABASE_URL=sqlite:///./amit_concierge.db
   ```
   Restart backend service. Because the SQLite file was untouched during migration, system operations continue uninterrupted.

2. **Target Cleanup (if re-attempting):**
   ```sql
   DROP SCHEMA public CASCADE;
   CREATE SCHEMA public;
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
   Then re-run:
   ```bash
   python -m alembic upgrade head
   python backend/scripts/migrate_sqlite_to_postgres.py ...
   ```
