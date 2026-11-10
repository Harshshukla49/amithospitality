import tempfile
import os
import shutil
import sqlite3
from alembic.config import Config
from alembic import command

def verify_alembic_chain():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db = os.path.join(tmpdir, "disposable_migration_test.db")
        os.environ["DATABASE_URL"] = f"sqlite:///{test_db}"
        
        backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        ini_path = os.path.join(backend_dir, "alembic.ini")
        script_loc = os.path.join(backend_dir, "alembic")
        
        cfg = Config(ini_path)
        cfg.set_main_option("script_location", script_loc)
        cfg.set_main_option("sqlalchemy.url", f"sqlite:///{test_db}")
        
        print(">>> 1. Testing Alembic upgrade head from empty DB...")
        command.upgrade(cfg, "head")
        
        con = sqlite3.connect(test_db)
        tables = [t[0] for t in con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        print(f"  [OK] Created {len(tables)} tables: {tables}")
        assert "guest_profiles" in tables
        assert "guest_verifications" in tables
        assert "reservation_modification_requests" in tables
        assert "guest_access_audits" in tables
        assert "notification_logs" in tables
        
        # Verify columns
        gp_cols = [c[1] for c in con.execute("PRAGMA table_info(guest_profiles)").fetchall()]
        print("  [OK] guest_profiles columns:", gp_cols)
        assert "currency" in gp_cols
        assert "is_shared_contact" in gp_cols
        assert "phone_normalized" in gp_cols
        
        rm_cols = [c[1] for c in con.execute("PRAGMA table_info(reservation_modification_requests)").fetchall()]
        print("  [OK] reservation_modification_requests columns:", rm_cols)
        assert "old_status" in rm_cols
        
        nl_cols = [c[1] for c in con.execute("PRAGMA table_info(notification_logs)").fetchall()]
        print("  [OK] notification_logs columns:", nl_cols)
        assert "attempts" in nl_cols
        
        res_cols = [c[1] for c in con.execute("PRAGMA table_info(reservation_requests)").fetchall()]
        assert "guest_profile_id" in res_cols
        
        # Seed test data to verify data preservation during downgrade/upgrade
        con.execute(
            "INSERT INTO guest_profiles (guest_uuid, environment, full_name, phone, phone_normalized, currency, is_shared_contact) "
            "VALUES ('GST-TEST1', 'DEMO', 'Test Guest', '+919999999999', '+919999999999', 'INR', 0)"
        )
        con.commit()
        guest_count = con.execute("SELECT COUNT(*) FROM guest_profiles").fetchone()[0]
        assert guest_count == 1
        con.close()
        
        print(">>> 2. Testing Alembic downgrade to Phase 20 (9c0d1e2f3a4b)...")
        command.downgrade(cfg, "9c0d1e2f3a4b")
        con = sqlite3.connect(test_db)
        gp_cols_downgraded = [c[1] for c in con.execute("PRAGMA table_info(guest_profiles)").fetchall()]
        assert "currency" not in gp_cols_downgraded
        # Confirm existing row was preserved across batch alter table
        preserved_count = con.execute("SELECT COUNT(*) FROM guest_profiles").fetchone()[0]
        assert preserved_count == 1, "Data must be preserved across batch alter downgrade"
        con.close()
        print("  [OK] Downgrade to Phase 20 successful. Existing data preserved.")
        
        print(">>> 3. Testing Alembic re-upgrade to head...")
        command.upgrade(cfg, "head")
        con = sqlite3.connect(test_db)
        gp_cols_reupgraded = [c[1] for c in con.execute("PRAGMA table_info(guest_profiles)").fetchall()]
        assert "currency" in gp_cols_reupgraded
        con.close()
        print("  [OK] Re-upgrade to head successful.")

        print(">>> 4. Testing full rollback to base...")
        command.downgrade(cfg, "base")
        con = sqlite3.connect(test_db)
        remaining_tables = [t[0] for t in con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        print(f"  [OK] Tables after full rollback to base: {remaining_tables}")
        assert "guest_profiles" not in remaining_tables
        assert "reservation_requests" not in remaining_tables
        con.close()
        print("  [OK] Full downgrade to base successful.")

        print(">>> 5. Testing fresh re-upgrade from base to head...")
        command.upgrade(cfg, "head")
        con = sqlite3.connect(test_db)
        final_tables = [t[0] for t in con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        assert "guest_profiles" in final_tables
        assert "reservation_modification_requests" in final_tables
        con.close()
        print("  [OK] Clean re-upgrade from base to head successful.")

if __name__ == "__main__":
    verify_alembic_chain()
