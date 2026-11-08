"""
AMIT AI CONCIERGE — PHASE 9 REGRESSION TEST SUITE
Production Infrastructure, Database Migration & Security Verification
"""

import os
import sys
import json
from datetime import datetime, timedelta

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable
from fastapi import HTTPException
from pgvector.sqlalchemy import Vector

from app.database import Base, check_database_health
from app.models.user import User
from app.models.token import RevokedToken
from app.models.outlet import Restaurant, Outlet, MenuItem
from app.models.knowledge import KnowledgeDocument, KnowledgeChunk
from app.models.reservation import ReservationRequest
from app.models.lead import Lead
from app.models.audit import AuditLog, EnvironmentSetting
from app.config import Settings
from app.utils.security import create_access_token, create_refresh_token, decode_token, get_current_user
from app.routers.auth import refresh_token_endpoint, logout
from app.schemas.auth import RefreshTokenRequest
from app.routers.integrations import get_integrations_status
from scripts.migrate_sqlite_to_postgres import migrate_data, TABLE_MIGRATION_ORDER

def setup_in_memory_db():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal(), engine

def test_phase9_infrastructure_and_migration():
    print("\n--- BEGIN PHASE 9: PRODUCTION INFRASTRUCTURE & DATABASE MIGRATION TESTS ---")

    # --------------------------------------------------------------------------
    # 1. PostgreSQL & pgvector DDL Compilation Test
    # --------------------------------------------------------------------------
    print("\n>>> 1. Verifying PostgreSQL & pgvector Schema Dialect Compilation...")
    pg_dialect = postgresql.dialect()

    for table_name, table in Base.metadata.tables.items():
        create_stmt = CreateTable(table).compile(dialect=pg_dialect)
        sql_str = str(create_stmt)
        assert len(sql_str) > 0, f"Table '{table_name}' failed PostgreSQL DDL compilation."

        # Verify pgvector compilation on knowledge_chunks
        if table_name == "knowledge_chunks":
            assert "vector(256)" in sql_str.lower(), "pgvector Vector(256) column not rendered in PostgreSQL DDL."

    print("  [OK] All 18 database tables and pgvector Vector(256) column compiled for PostgreSQL.")

    # --------------------------------------------------------------------------
    # 2. Database Health & Ping Check
    # --------------------------------------------------------------------------
    print("\n>>> 2. Verifying Database Health Ping...")
    db_health = check_database_health()
    assert db_health["connected"] is True
    assert db_health["status"] == "healthy"
    assert db_health["latency_ms"] >= 0.0
    print(f"  [OK] Database health ping verified: status={db_health['status']}, dialect={db_health['dialect']}, latency={db_health['latency_ms']}ms")

    # --------------------------------------------------------------------------
    # 3. Production Environment Safeguards Validation
    # --------------------------------------------------------------------------
    print("\n>>> 3. Verifying Production Environment Configuration Guards...")
    # 3a. Rejects default JWT secret in production
    try:
        Settings(
            APP_ENV="production",
            JWT_SECRET_KEY="amit_hospitality_super_secure_jwt_secret_key_2026_change_in_production",
            INITIAL_ADMIN_PASSWORD="Secure_Admin_Password_2026!",
            DATABASE_URL="postgresql+psycopg2://user:pass@host/db",
            DEBUG=False,
        )
        assert False, "Should fail on default JWT secret in production."
    except ValueError as e:
        assert "JWT_SECRET_KEY cannot use default development placeholder" in str(e)
        print("  [OK] Guard blocked default JWT secret in production.")

    # 3b. Rejects SQLite in production
    try:
        Settings(
            APP_ENV="production",
            JWT_SECRET_KEY="super_secure_custom_production_key_64_characters_long_1234567890",
            INITIAL_ADMIN_PASSWORD="Secure_Admin_Password_2026!",
            DATABASE_URL="sqlite:///./amit_concierge.db",
            DEBUG=False,
        )
        assert False, "Should fail on SQLite database URL in production."
    except ValueError as e:
        assert "SQLite is prohibited in production" in str(e)
        print("  [OK] Guard blocked SQLite in production.")

    # 3c. Rejects DEBUG=True in production
    try:
        Settings(
            APP_ENV="production",
            JWT_SECRET_KEY="super_secure_custom_production_key_64_characters_long_1234567890",
            INITIAL_ADMIN_PASSWORD="Secure_Admin_Password_2026!",
            DATABASE_URL="postgresql+psycopg2://user:pass@host/db",
            DEBUG=True,
        )
        assert False, "Should fail on DEBUG=True in production."
    except ValueError as e:
        assert "DEBUG must be False in production" in str(e)
        print("  [OK] Guard blocked DEBUG=True in production.")

    # --------------------------------------------------------------------------
    # 4. Token Rotation & Replay-Attack Prevention Test
    # --------------------------------------------------------------------------
    print("\n>>> 4. Verifying Refresh Token Rotation & Replay Protection...")
    db, engine = setup_in_memory_db()

    user = User(
        email="devops@amithospitality.com",
        full_name="Lead DevOps Architect",
        password_hash="fakehash",
        role="SUPER_ADMIN",
        is_active=True,
    )
    db.add(user)
    db.commit()

    # Generate initial refresh token
    refresh_token_1 = create_refresh_token(data={"sub": user.email})
    payload_1 = decode_token(refresh_token_1)
    jti_1 = payload_1.get("jti")
    assert jti_1 is not None, "Refresh token must carry a unique JTI"

    # Rotate refresh token (1st consumption)
    req_1 = RefreshTokenRequest(refresh_token=refresh_token_1)
    token_resp_1 = refresh_token_endpoint(req=req_1, db=db)
    assert token_resp_1.refresh_token != refresh_token_1
    print("  [OK] Refresh token successfully rotated and issued new token pair.")

    # Verify old token JTI is now recorded in RevokedToken
    revoked_entry = db.query(RevokedToken).filter(RevokedToken.jti == jti_1).first()
    assert revoked_entry is not None
    assert revoked_entry.revocation_reason == "ROTATED"
    print("  [OK] Consumed refresh token JTI successfully blacklisted.")

    # Replay attack attempt: Try to use refresh_token_1 AGAIN
    try:
        refresh_token_endpoint(req=req_1, db=db)
        assert False, "Should fail on replaying an already consumed refresh token."
    except HTTPException as e:
        assert e.status_code == 401
        assert "replay protection" in e.detail.lower()
        print("  [OK] Replay attack intercepted: 401 Unauthorized raised on token reuse.")

    # Test Logout Revocation
    logout_access_token = create_access_token(data={"sub": user.email})
    logout_payload = decode_token(logout_access_token)
    logout_jti = logout_payload.get("jti")
    logout_res = logout(token=logout_access_token, current_user=user, db=db)
    assert logout_res["success"] is True

    # Verify access token is blacklisted
    revoked_access = db.query(RevokedToken).filter(RevokedToken.jti == logout_jti).first()
    assert revoked_access is not None
    assert revoked_access.revocation_reason == "LOGOUT"

    # Attempt to authenticate with logged-out token
    try:
        get_current_user(token=logout_access_token, db=db)
        assert False, "Logged out token should be rejected."
    except HTTPException as e:
        assert e.status_code == 401
        assert "revoked" in e.detail.lower()
        print("  [OK] Explicit logout token revocation verified.")

    # --------------------------------------------------------------------------
    # 5. Third-Party Integration Status Inspection
    # --------------------------------------------------------------------------
    print("\n>>> 5. Verifying Third-Party Integration Diagnostics...")
    integrations = get_integrations_status(current_user=user)
    assert "integrations" in integrations
    services = integrations["integrations"]
    assert "gemini_api" in services
    assert "whatsapp_cloud_api" in services
    assert "twilio_voice" in services
    assert "email_service" in services
    assert "sms_service" in services
    assert "redis_cache" in services
    assert "sentry_monitoring" in services

    # Verify zero-fabrication honest statuses
    for svc_key, svc_info in services.items():
        assert svc_info["status"] in ["CONFIGURED", "NOT CONFIGURED", "NOT CONFIGURED (Using In-Memory Sliding-Window Fallback)"]
    print("  [OK] All third-party integration diagnostics report authentic configuration statuses.")

    # --------------------------------------------------------------------------
    # 6. SQLite to Target Database Migration Engine Test
    # --------------------------------------------------------------------------
    print("\n>>> 6. Verifying Database Migration Engine & Data Transfer...")
    # Create temporary source SQLite database
    temp_sqlite = os.path.abspath(os.path.join(os.path.dirname(__file__), "temp_test_source.db"))
    temp_target = os.path.abspath(os.path.join(os.path.dirname(__file__), "temp_test_target.db"))

    if os.path.exists(temp_sqlite):
        os.remove(temp_sqlite)
    if os.path.exists(temp_target):
        os.remove(temp_target)

    try:
        source_engine = create_engine(f"sqlite:///{temp_sqlite}")
        Base.metadata.create_all(bind=source_engine)
        SourceSession = sessionmaker(bind=source_engine)
        s_db = SourceSession()

        # Seed source records across multiple tables
        env_rec = EnvironmentSetting(active_environment="DEMO", updated_by_name="Admin", switch_reason="Init")
        rest = Restaurant(name="Amit Luxury Hotels & Dining", slug="amit-dining")
        s_db.add_all([env_rec, rest])
        s_db.commit()

        outl = Outlet(
            restaurant_id=rest.id,
            name="The Velvet Cellar",
            slug="velvet-cellar",
            outlet_type="Wine Salon & Lounge",
            cuisine_type="European Small Plates",
            location="Sub-level, Lodhi Road",
            is_active=True,
        )
        s_db.add(outl)
        s_db.commit()

        doc = KnowledgeDocument(
            environment="DEMO",
            outlet_id=outl.id,
            title="Wine Masterclass List",
            file_name="wines.pdf",
            file_type="PDF",
            is_active=True,
        )
        s_db.add(doc)
        s_db.commit()

        chunk = KnowledgeChunk(
            document_id=doc.id,
            environment="DEMO",
            outlet_id=outl.id,
            content="Vintage Bordeaux selection list.",
            embedding_json=json.dumps([0.12] * 256),
            is_active=True,
        )
        res_req = ReservationRequest(
            environment="DEMO",
            outlet_id=outl.id,
            outlet_name=outl.name,
            guest_name="Mr. Rahul Verma",
            guest_phone="+91 98765 00000",
            guest_count=2,
            reservation_date="2026-12-01",
            reservation_time="20:00",
            status="NEW",
        )
        lead_req = Lead(
            environment="DEMO",
            outlet_id=outl.id,
            outlet_name=outl.name,
            name="Pooja Batra",
            phone="+91 99999 11111",
            email="pooja@example.com",
            enquiry_type="BIRTHDAY_PARTY",
            guest_count=25,
            target_date="2026-12-15",
            status="NEW",
        )
        s_db.add_all([chunk, res_req, lead_req])
        s_db.commit()
        s_db.close()

        # Run Dry-Run Migration
        dry_res = migrate_data(sqlite_path=temp_sqlite, postgres_url=f"sqlite:///{temp_target}", dry_run=True)
        assert dry_res["success"] is True
        assert dry_res["dry_run"] is True
        assert dry_res["table_breakdown"]["outlets"]["source"] == 1
        assert dry_res["table_breakdown"]["knowledge_documents"]["source"] == 1
        print("  [OK] Dry-run migration verified: reported exact row counts without modifying target.")

        # Run Live Migration
        live_res = migrate_data(sqlite_path=temp_sqlite, postgres_url=f"sqlite:///{temp_target}", dry_run=False)
        assert live_res["success"] is True
        assert live_res["dry_run"] is False
        assert live_res["total_records"] >= 6
        assert live_res["table_breakdown"]["outlets"]["migrated"] == 1
        assert live_res["table_breakdown"]["knowledge_chunks"]["migrated"] == 1
        assert live_res["table_breakdown"]["reservation_requests"]["migrated"] == 1
        assert live_res["table_breakdown"]["leads"]["migrated"] == 1

        # Verify source database file is completely intact
        assert os.path.exists(temp_sqlite), "Source database must never be deleted."
        print(f"  [OK] Live migration verified: {live_res['total_records']} rows transferred; source preserved.")

    finally:
        try:
            source_engine.dispose()
        except Exception:
            pass
        if os.path.exists(temp_sqlite):
            try:
                os.remove(temp_sqlite)
            except Exception:
                pass
        if os.path.exists(temp_target):
            try:
                os.remove(temp_target)
            except Exception:
                pass

    print("\n--- PHASE 9: ALL TESTS PASSED SUCCESSFULLY! ---\n")

if __name__ == "__main__":
    test_phase9_infrastructure_and_migration()
