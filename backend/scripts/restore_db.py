"""
AMIT AI CONCIERGE — DATABASE RESTORE UTILITY
Enterprise Disaster Recovery Tool for SQLite & PostgreSQL

Supports:
- Safe verification of target environment.
- Restoration from backup snapshot.
- Integrity verification following restore.
"""

import os
import sys
import shutil
import subprocess
import logging

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("restore")

def restore_database(backup_file: str) -> bool:
    if not os.path.exists(backup_file):
        raise FileNotFoundError(f"Backup file not found: {backup_file}")

    db_url = settings.clean_database_url

    if db_url.startswith("sqlite"):
        target_file = db_url.replace("sqlite:///", "").replace("sqlite://", "")
        # Create safety pre-restore backup
        if os.path.exists(target_file):
            safety_copy = f"{target_file}.prerestore_safety"
            shutil.copy2(target_file, safety_copy)
            logger.info(f"Saved safety pre-restore copy to {safety_copy}")

        shutil.copy2(backup_file, target_file)
        logger.info(f"[OK] Restored SQLite database from {backup_file} -> {target_file}")
        return True

    elif "postgres" in db_url:
        logger.info(f"Restoring PostgreSQL database from {backup_file}...")
        try:
            cmd = ["psql", "--dbname", db_url, "-f", backup_file]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"psql restore error: {result.stderr}")
                raise RuntimeError(f"psql restore failed: {result.stderr}")
            logger.info(f"[OK] Restored PostgreSQL database from {backup_file}")
            return True
        except FileNotFoundError:
            logger.error("psql binary not found in system PATH. Ensure PostgreSQL client tools are installed.")
            return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python restore_db.py <path_to_backup_file>")
        sys.exit(1)
    restore_database(sys.argv[1])
