import os
import sys

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.user import User
from app.models.audit import AuditLog, EnvironmentSetting
from app.models.reservation import ReservationRequest
from app.models.lead import Lead
from app.models.knowledge import KnowledgeDocument
from app.models.conversation import Conversation
from app.routers.analytics import get_dashboard_kpis, export_analytics_summary_csv
from app.routers.audit import get_audit_logs, export_audit_logs_csv

def setup_test_db():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    return db

def test_phase6_analytics_and_audit():
    print("\n--- BEGIN PHASE 6: ANALYTICS & AUDIT COMPLIANCE TESTS ---")
    db = setup_test_db()

    # 1. Setup Admin user
    admin_user = User(
        email="compliance_officer@amithospitality.com",
        full_name="Chief Compliance Officer",
        password_hash="fakehashedpassword",
        role="SUPER_ADMIN",
        is_active=True,
    )
    db.add(admin_user)
    db.commit()
    print("  [OK] Super Admin compliance officer created.")

    # 2. Seed environment setting
    env_setting = EnvironmentSetting(
        active_environment="DEMO",
        updated_by_name="Chief Compliance Officer",
        switch_reason="Initial setup for audit testing",
    )
    db.add(env_setting)

    # 3. Seed some audit logs across environments
    log1 = AuditLog(
        user_id=admin_user.id,
        user_name=admin_user.full_name,
        user_role="SUPER_ADMIN",
        action="SWITCH_ENVIRONMENT",
        entity_type="ENVIRONMENT",
        environment="DEMO",
        details="Switched environment to DEMO mode for demonstration",
    )
    log2 = AuditLog(
        user_id=admin_user.id,
        user_name=admin_user.full_name,
        user_role="SUPER_ADMIN",
        action="DOCUMENT_UPLOAD",
        entity_type="DOCUMENT",
        environment="REAL",
        details="Uploaded verified corporate menu PDF",
    )
    log3 = AuditLog(
        user_id=admin_user.id,
        user_name=admin_user.full_name,
        user_role="SUPER_ADMIN",
        action="RESERVATION_STATUS_UPDATE",
        entity_type="RESERVATION",
        environment="DEMO",
        details="Accepted VIP reservation #101",
    )
    db.add_all([log1, log2, log3])

    # 4. Seed reservations and leads
    res1 = ReservationRequest(
        environment="DEMO",
        outlet_id=1,
        outlet_name="Amber Terrace Rooftop",
        guest_name="Aarav Sharma",
        guest_phone="+91 98765 43210",
        guest_count=4,
        reservation_date="2026-11-20",
        reservation_time="20:00",
        seating_preference="ROOFTOP",
        status="NEW",
    )
    res2 = ReservationRequest(
        environment="REAL",
        outlet_id=1,
        outlet_name="Amber Terrace Rooftop",
        guest_name="Verified Guest",
        guest_phone="+91 99999 88888",
        guest_count=2,
        reservation_date="2026-11-21",
        reservation_time="19:30",
        seating_preference="INDOOR",
        status="NEW",
    )
    lead1 = Lead(
        environment="DEMO",
        outlet_id=1,
        outlet_name="Amber Terrace Rooftop",
        name="Vikram Mehta",
        phone="+91 98765 11111",
        email="vikram@example.com",
        enquiry_type="CORPORATE_EVENT",
        guest_count=80,
        target_date="2026-12-15",
        status="NEW",
    )
    doc1 = KnowledgeDocument(
        environment="DEMO",
        title="Demo Rooftop Guidelines",
        file_name="demo_rooftop.pdf",
        file_type="PDF",
        file_size_bytes=12000,
        is_active=True,
    )
    db.add_all([res1, res2, lead1, doc1])
    db.commit()
    print("  [OK] Test data seeded (Audit logs, reservations, leads, documents).")

    # 5. Verify get_dashboard_kpis
    kpis = get_dashboard_kpis(db=db)
    print(f"  [OK] Retrieved KPIs: Active Env={kpis.active_environment}, Pending Res={kpis.pending_reservations}, Leads={kpis.total_leads}, Active Docs={kpis.active_documents}")
    assert kpis.active_environment == "DEMO"
    assert kpis.pending_reservations == 1  # Only DEMO res1
    assert kpis.total_leads == 1
    assert kpis.active_documents == 1
    assert len(kpis.frequent_queries) >= 5
    assert len(kpis.unanswered_questions) >= 3

    # 6. Verify export_analytics_summary_csv
    analytics_csv_response = export_analytics_summary_csv(current_user=admin_user, db=db)
    assert analytics_csv_response.media_type == "text/csv"
    csv_text = analytics_csv_response.body.decode("utf-8")
    assert "AMIT AI CONCIERGE — EXECUTIVE ANALYTICS REPORT" in csv_text
    assert "Pending Table Reservations" in csv_text
    assert "TOP FREQUENT GUEST INQUIRIES" in csv_text
    assert "KNOWLEDGE GAPS & UNANSWERED QUESTIONS" in csv_text
    print("  [OK] Analytics summary CSV export verified.")

    # 7. Verify get_audit_logs listing
    all_logs = get_audit_logs(limit=50, action=None, environment=None, current_user=admin_user, db=db)
    assert len(all_logs) == 3
    print(f"  [OK] All audit logs retrieved: count={len(all_logs)}")

    # 8. Verify audit log filtering by environment
    demo_logs = get_audit_logs(limit=50, action=None, environment="DEMO", current_user=admin_user, db=db)
    assert len(demo_logs) == 2
    for l in demo_logs:
        assert l["environment"] == "DEMO"
    print("  [OK] Audit log environment filtering verified (DEMO only returned DEMO records).")

    real_logs = get_audit_logs(limit=50, action=None, environment="REAL", current_user=admin_user, db=db)
    assert len(real_logs) == 1
    assert real_logs[0]["environment"] == "REAL"
    print("  [OK] Audit log environment filtering verified (REAL only returned REAL records).")

    # 9. Verify audit log filtering by action
    action_logs = get_audit_logs(limit=50, action="DOCUMENT_UPLOAD", environment=None, current_user=admin_user, db=db)
    assert len(action_logs) == 1
    assert action_logs[0]["action"] == "DOCUMENT_UPLOAD"
    print("  [OK] Audit log action filtering verified.")

    # 10. Verify export_audit_logs_csv
    audit_csv_resp = export_audit_logs_csv(environment="DEMO", current_user=admin_user, db=db)
    assert audit_csv_resp.media_type == "text/csv"
    audit_csv_content = audit_csv_resp.body.decode("utf-8")
    assert "ID,Timestamp,Administrator,Role,Action,Entity Type,Environment,Details" in audit_csv_content
    assert "SWITCH_ENVIRONMENT" in audit_csv_content
    assert "RESERVATION_STATUS_UPDATE" in audit_csv_content
    # REAL record shouldn't be in DEMO export
    assert "DOCUMENT_UPLOAD" not in audit_csv_content
    print("  [OK] Audit trail CSV export with environment filter verified.")

    print("\n--- PHASE 6: ALL TESTS PASSED SUCCESSFULLY! ---\n")

if __name__ == "__main__":
    test_phase6_analytics_and_audit()
