"""
AMIT AI CONCIERGE — PRODUCTION & STAGING DATABASE MIGRATION RUNNER
Enterprise Migration Orchestration for Amit Hospitality (https://amithospitality.com/)

Guarantees safe, single-instance database schema upgrades:
1. Verifies database connectivity with exponential backoff retries.
2. Acquires PostgreSQL advisory lock (pg_advisory_lock) to prevent concurrent migration races.
3. Automatically snapshots SQLite databases prior to applying DDL changes.
4. Executes Alembic 'upgrade head' within an isolated, monitored session.
5. Validates current database revision against migration head.
6. Fails fast with exit code 1 if migration fails, preventing application startup on corrupt schemas.
"""

import os
import sys
import time
import logging
from typing import Optional
from sqlalchemy import create_engine, text
from alembic.config import Config
from alembic import command
from alembic.script import ScriptDirectory

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("migration_runner")

ADVISORY_LOCK_ID = 98234187  # Unique enterprise 64-bit integer lock ID for Amit Concierge migrations

def get_database_url() -> str:
    """Extract and normalize target database URL."""
    backend_dir = os.path.abspath(os.path.dirname(__file__))
    sys.path.insert(0, backend_dir)
    from app.config import settings
    return settings.clean_database_url

def wait_for_database(db_url: str, max_retries: int = 15, delay_seconds: float = 2.0) -> bool:
    """Poll database until accessible or timeout is reached."""
    logger.info("Verifying database connectivity...")
    engine = create_engine(db_url, pool_pre_ping=True)
    for attempt in range(1, max_retries + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info(f"Database connection verified successfully on attempt {attempt}.")
            return True
        except Exception as ex:
            logger.warning(f"Database not ready (attempt {attempt}/{max_retries}): {ex}. Retrying in {delay_seconds}s...")
            time.sleep(delay_seconds)
    logger.error("Failed to connect to database within the timeout period.")
    return False

def acquire_migration_lock(engine) -> bool:
    """Acquire PostgreSQL advisory lock if running on PostgreSQL."""
    if engine.dialect.name == "postgresql":
        logger.info(f"Acquiring PostgreSQL advisory lock ({ADVISORY_LOCK_ID}) to prevent concurrent migrations...")
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT pg_try_advisory_lock({ADVISORY_LOCK_ID})")).scalar()
            if not result:
                logger.warning("Another process is currently running migrations. Waiting for advisory lock...")
                conn.execute(text(f"SELECT pg_advisory_lock({ADVISORY_LOCK_ID})"))
            logger.info("Advisory lock acquired.")
            return True
    return False

def release_migration_lock(engine):
    """Release PostgreSQL advisory lock."""
    if engine.dialect.name == "postgresql":
        try:
            with engine.connect() as conn:
                conn.execute(text(f"SELECT pg_advisory_unlock({ADVISORY_LOCK_ID})"))
            logger.info("PostgreSQL advisory lock released.")
        except Exception as ex:
            logger.warning(f"Error releasing advisory lock: {ex}")

def backup_sqlite_if_applicable(db_url: str):
    """Create timestamped copy if using SQLite database."""
    if db_url.startswith("sqlite:///"):
        sqlite_file = db_url.replace("sqlite:///", "")
        if os.path.exists(sqlite_file):
            import shutil
            backup_path = f"{sqlite_file}.pre_migration.{int(time.time())}.bak"
            shutil.copy2(sqlite_file, backup_path)
            logger.info(f"Created pre-migration SQLite backup at: {backup_path}")

def run_migrations():
    """Main execution entrypoint for pre-boot database migrations."""
    db_url = get_database_url()
    logger.info(f"Starting schema migration for database engine: {db_url.split('://')[0]}")

    if not wait_for_database(db_url):
        logger.error("Aborting migration: Target database unreachable.")
        sys.exit(1)

    backup_sqlite_if_applicable(db_url)

    engine = create_engine(db_url)
    lock_acquired = False

    try:
        lock_acquired = acquire_migration_lock(engine)

        backend_dir = os.path.abspath(os.path.dirname(__file__))
        ini_path = os.path.join(backend_dir, "alembic.ini")
        script_loc = os.path.join(backend_dir, "alembic")

        cfg = Config(ini_path)
        cfg.set_main_option("script_location", script_loc)
        cfg.set_main_option("sqlalchemy.url", db_url)

        script = ScriptDirectory.from_config(cfg)
        head_rev = script.get_current_head()
        logger.info(f"Target migration head revision: {head_rev}")

        # Schema detection safeguard: If tables already exist but alembic_version is empty
        from sqlalchemy import inspect
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        has_version_stamp = False
        if "alembic_version" in existing_tables:
            with engine.connect() as conn:
                res = conn.execute(text("SELECT version_num FROM alembic_version")).fetchall()
                has_version_stamp = len(res) > 0

        if not has_version_stamp and "users" in existing_tables:
            if "guest_profiles" in existing_tables:
                gp_cols = [c["name"] for c in inspector.get_columns("guest_profiles")]
                if "is_shared_contact" in gp_cols:
                    logger.info("Existing schema matches Phase 20.1 head. Stamping revision a1b2c3d4e5f6...")
                    command.stamp(cfg, "a1b2c3d4e5f6")
                else:
                    logger.info("Existing schema matches Phase 20. Stamping revision 9c0d1e2f3a4b...")
                    command.stamp(cfg, "9c0d1e2f3a4b")
            else:
                logger.info("Existing schema matches baseline. Stamping revision 266d4294e882...")
                command.stamp(cfg, "266d4294e882")

        logger.info("Executing Alembic upgrade head...")
        command.upgrade(cfg, "head")

        # Verify current revision in database matches target head
        with engine.connect() as conn:
            current_rev = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()

        if current_rev != head_rev:
            logger.error(f"Migration verification failed: DB revision is '{current_rev}', expected '{head_rev}'.")
            sys.exit(1)

        logger.info(f"Database schema successfully verified at head revision: {current_rev}")

    except Exception as ex:
        logger.error(f"FATAL: Database migration failed: {ex}", exc_info=True)
        sys.exit(1)
    finally:
        if lock_acquired:
            release_migration_lock(engine)

if __name__ == "__main__":
    run_migrations()
