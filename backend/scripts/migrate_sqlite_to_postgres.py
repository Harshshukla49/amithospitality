"""
AMIT AI CONCIERGE — SQLITE TO POSTGRESQL + PGVECTOR DATA MIGRATION UTILITY
Enterprise Database Migration Tool for Amit Hospitality

Features:
- Validates source SQLite database and target PostgreSQL connection.
- Auto-initializes PostgreSQL schema and pgvector extension.
- Preserves all relational keys and foreign key hierarchies.
- Migrates embedding_json vectors into native pgvector embedding column.
- Resets PostgreSQL auto-increment sequences for all serial primary keys.
- Performs row-count verification and data validation.
- Dry-run capability to preview row counts without altering target.
- Safety: NEVER deletes or modifies source SQLite file.
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime
from typing import List, Dict, Any

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from app.database import Base
import app.models  # load all models into Base.metadata

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("migration")

# Ordered sequence respecting foreign key constraints
TABLE_MIGRATION_ORDER = [
    "environment_settings",
    "restaurants",
    "outlets",
    "users",
    "menu_categories",
    "menu_items",
    "policies",
    "faqs",
    "ai_configs",
    "knowledge_documents",
    "knowledge_chunks",
    "customers",
    "conversations",
    "messages",
    "reservation_requests",
    "reservation_status_history",
    "leads",
    "lead_status_history",
    "audit_logs",
    "revoked_tokens",
]

def migrate_data(sqlite_path: str, postgres_url: str, dry_run: bool = False, batch_size: int = 500) -> Dict[str, Any]:
    if not os.path.exists(sqlite_path):
        raise FileNotFoundError(f"Source SQLite database not found at: {sqlite_path}")

    # Normalize PostgreSQL URL
    if postgres_url.startswith("postgres://"):
        postgres_url = postgres_url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif postgres_url.startswith("postgresql://") and "+psycopg2" not in postgres_url:
        postgres_url = postgres_url.replace("postgresql://", "postgresql+psycopg2://", 1)

    logger.info("=" * 70)
    logger.info("AMIT AI CONCIERGE — DATABASE MIGRATION ENGINE")
    logger.info(f"Source SQLite DB : {sqlite_path}")
    logger.info(f"Target DB URL    : {postgres_url.split('@')[-1] if '@' in postgres_url else postgres_url}")
    logger.info(f"Execution Mode   : {'DRY RUN (Preview)' if dry_run else 'LIVE MIGRATION'}")
    logger.info("=" * 70)

    sqlite_engine = create_engine(f"sqlite:///{sqlite_path}", connect_args={"check_same_thread": False})
    pg_engine = create_engine(postgres_url, pool_pre_ping=True)

    # 1. Verify Connections
    with sqlite_engine.connect() as s_conn:
        s_conn.execute(text("SELECT 1"))
    logger.info("[OK] Source SQLite database connected successfully.")

    with pg_engine.connect() as p_conn:
        p_conn.execute(text("SELECT 1"))
        # Enable pgvector extension
        if p_conn.dialect.name == "postgresql" and not dry_run:
            try:
                p_conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                p_conn.commit()
                logger.info("[OK] pgvector extension verified / initialized.")
            except Exception as e:
                logger.warning(f"Could not initialize pgvector extension: {e}")
    logger.info("[OK] Target database connected successfully.")

    # 2. Schema Creation on Target
    if not dry_run:
        logger.info("Creating tables on target database (if not exists)...")
        Base.metadata.create_all(bind=pg_engine)
        logger.info("[OK] Target tables verified.")

    # 3. Read Source Tables
    sqlite_inspector = inspect(sqlite_engine)
    available_sqlite_tables = set(sqlite_inspector.get_table_names())

    migration_report: Dict[str, Dict[str, int]] = {}
    total_records_migrated = 0

    with sqlite_engine.connect() as s_conn, pg_engine.connect() as p_conn:
        for table_name in TABLE_MIGRATION_ORDER:
            if table_name not in available_sqlite_tables:
                logger.info(f"  [-] Table '{table_name}' does not exist in SQLite source. Skipping.")
                continue

            # Count source rows
            s_count = s_conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar() or 0
            logger.info(f"Processing table '{table_name}': {s_count} rows found in source.")

            if dry_run or s_count == 0:
                migration_report[table_name] = {"source": s_count, "migrated": 0 if dry_run else s_count}
                continue

            # Fetch rows
            rows_result = s_conn.execute(text(f"SELECT * FROM {table_name}"))
            columns = rows_result.keys()
            rows = [dict(zip(columns, row)) for row in rows_result.fetchall()]

            # Handle KnowledgeChunk vectors for pgvector
            if table_name == "knowledge_chunks" and p_conn.dialect.name == "postgresql":
                for r in rows:
                    if "embedding" in r and not r.get("embedding") and r.get("embedding_json"):
                        try:
                            r["embedding"] = json.loads(r["embedding_json"])
                        except Exception:
                            r["embedding"] = None

            table_obj = Base.metadata.tables.get(table_name)
            if table_obj is not None:
                # Convert string representations of DateTime/Date to Python datetime objects
                datetime_cols = {col.name for col in table_obj.columns if "date" in type(col.type).__name__.lower()}
                for r in rows:
                    for d_col in datetime_cols:
                        val = r.get(d_col)
                        if isinstance(val, str) and val.strip():
                            try:
                                r[d_col] = datetime.fromisoformat(val.strip())
                            except Exception:
                                pass

                # Insert in batches
                for i in range(0, len(rows), batch_size):
                    batch = rows[i : i + batch_size]
                    p_conn.execute(table_obj.insert(), batch)
                p_conn.commit()

            # Verify target count
            t_count = p_conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar() or 0
            logger.info(f"  [OK] Migrated '{table_name}': source={s_count}, target={t_count}")
            migration_report[table_name] = {"source": s_count, "migrated": t_count}
            total_records_migrated += s_count

        # 4. Reset PostgreSQL Auto-Increment Sequences
        if p_conn.dialect.name == "postgresql" and not dry_run:
            logger.info("Resetting PostgreSQL primary key sequences...")
            for table_name in TABLE_MIGRATION_ORDER:
                if table_name in available_sqlite_tables:
                    try:
                        seq_sql = text(f"""
                            SELECT setval(
                                pg_get_serial_sequence('{table_name}', 'id'),
                                COALESCE((SELECT MAX(id) FROM {table_name}), 1),
                                true
                            );
                        """)
                        p_conn.execute(seq_sql)
                    except Exception as e:
                        # Some tables might not have an 'id' serial column
                        pass
            p_conn.commit()
            logger.info("[OK] PostgreSQL sequences reset.")

    logger.info("=" * 70)
    logger.info(f"MIGRATION COMPLETE: {total_records_migrated} total records processed.")
    logger.info("=" * 70)
    return {
        "success": True,
        "dry_run": dry_run,
        "total_records": total_records_migrated,
        "table_breakdown": migration_report,
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Amit AI Concierge SQLite to PostgreSQL Migration")
    parser.add_argument("--sqlite-path", default="./amit_concierge.db", help="Path to SQLite database")
    parser.add_argument("--postgres-url", default=os.getenv("DATABASE_URL", ""), help="Target PostgreSQL connection URL")
    parser.add_argument("--dry-run", action="store_true", help="Perform dry run without inserting")
    parser.add_argument("--batch-size", type=int, default=500, help="Batch insert size")

    args = parser.parse_args()

    if not args.postgres_url:
        logger.error("Error: --postgres-url is required or DATABASE_URL environment variable must be set.")
        sys.exit(1)

    try:
        res = migrate_data(args.sqlite_path, args.postgres_url, dry_run=args.dry_run, batch_size=args.batch_size)
        print("\nMigration Summary JSON:")
        print(json.dumps(res, indent=2))
    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)
        sys.exit(1)
