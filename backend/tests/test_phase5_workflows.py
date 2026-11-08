import sys
import os
import io
import csv
import pytest

# Ensure utf-8 encoding on Windows console
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.user import User
from app.models.outlet import Outlet
from app.models.reservation import ReservationRequest
from app.models.lead import Lead
from app.models.audit import EnvironmentSetting, AuditLog
from app.routers.reservations import (
    create_reservation,
    list_reservations,
    update_reservation_status,
    export_reservations_csv,
)
from app.routers.leads import (
    create_lead,
    list_leads,
    update_lead_status,
    export_leads_csv,
)
from app.schemas.reservation import ReservationCreate, ReservationStatusUpdate
from app.schemas.lead import LeadCreate, LeadStatusUpdate

TEST_DB_PATH = os.path.join(backend_dir, "test_phase5.db")
if os.path.exists(TEST_DB_PATH):
    try:
        os.remove(TEST_DB_PATH)
    except Exception:
        pass

engine = create_engine(f"sqlite:///{TEST_DB_PATH}", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def setup_module():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        admin = User(
            id=1,
            email="admin@amithospitality.com",
            password_hash="testhash",
            full_name="Vikram Sharma",
            role="SUPER_ADMIN",
            is_active=True,
        )
        db.add(admin)

        outlet = Outlet(
            id=1,
            name="Amber Terrace Rooftop",
            slug="amber-terrace",
            outlet_type="Rooftop Lounge",
            cuisine_type="Pan-Asian",
            opening_time="17:30",
            closing_time="01:30",
            dress_code="Smart Casual",
            seating_capacity=50,  # Small capacity to test occupancy warning
            location="MG Road",
            description="Luxury rooftop",
        )
        db.add(outlet)

        setting = EnvironmentSetting(
            active_environment="DEMO",
            updated_by_name="Tester",
            switch_reason="Phase 5 setup",
        )
        db.add(setting)
        db.commit()
    finally:
        db.close()

def teardown_module():
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass

# 1. Test Standard Reservation Creation
def test_create_reservation_standard():
    db = TestingSessionLocal()
    try:
        req = ReservationCreate(
            outlet_id=1,
            guest_name="Kavita Krishnan",
            guest_phone="+91 98201 11223",
            guest_email="kavita@investments.in",
            guest_count=4,
            reservation_date="2026-11-15",
            reservation_time="20:00",
            seating_preference="ROOFTOP",
            special_requests="Anniversary dinner. Window table requested.",
        )
        res = create_reservation(req=req, db=db)
        assert res.id is not None
        assert res.status == "NEW"
        assert res.guest_name == "Kavita Krishnan"
        assert res.capacity_warning is None
    finally:
        db.close()

# 2. Test Reservation Capacity Warning Trigger
def test_create_reservation_capacity_overflow():
    db = TestingSessionLocal()
    try:
        # Seating capacity of outlet 1 is 50. Request 55 guests!
        req = ReservationCreate(
            outlet_id=1,
            guest_name="Corporate Summit Delegations",
            guest_phone="+91 98111 88990",
            guest_count=55,
            reservation_date="2026-11-15",
            reservation_time="20:00",
            seating_preference="INDOOR",
            special_requests="Full buyout required",
        )
        res = create_reservation(req=req, db=db)
        assert res.status == "UNDER_REVIEW"
        assert res.capacity_warning is not None
        assert "High occupancy alert" in res.capacity_warning
        assert "CAPACITY NOTICE" in res.internal_notes
    finally:
        db.close()

# 3. Test Admin Reservation Status Lifecycle & Audit Log
def test_reservation_admin_lifecycle():
    db = TestingSessionLocal()
    try:
        # List reservations
        items = list_reservations(outlet_id=1, db=db)
        assert len(items) >= 2

        target_id = items[0].id
        # Transition: -> ACCEPTED
        updated = update_reservation_status(
            res_id=target_id,
            status_update=ReservationStatusUpdate(
                status="ACCEPTED",
                internal_notes="Table #14 reserved with champagne bucket.",
            ),
            db=db,
        )
        assert updated.status == "ACCEPTED"
        assert "champagne bucket" in updated.internal_notes

        # Verify audit log
        audit = db.query(AuditLog).filter(
            AuditLog.entity_type == "RESERVATION",
            AuditLog.entity_id == target_id,
        ).order_by(AuditLog.id.desc()).first()
        assert audit is not None
        assert "ACCEPTED" in audit.details
    finally:
        db.close()

# 4. Test Reservations CSV Export
def test_reservations_csv_export():
    db = TestingSessionLocal()
    try:
        resp = export_reservations_csv(environment="DEMO", db=db)
        content = resp.body.decode("utf-8")
        assert "Reference ID" in content
        assert "Guest Name" in content
        assert "Kavita Krishnan" in content
    finally:
        db.close()

# 5. Test Event Lead Submission
def test_create_event_lead():
    db = TestingSessionLocal()
    try:
        req = LeadCreate(
            outlet_id=1,
            name="Rahul Malhotra",
            phone="+91 98102 33445",
            email="r.malhotra@techcorp.com",
            enquiry_type="CORPORATE_EVENT",
            guest_count=40,
            target_date="2026-12-10",
            budget_range="₹2,50,000 - ₹5,00,000",
            notes="Annual leadership gala with AV projector and cocktail pass-arounds.",
        )
        lead = create_lead(req=req, db=db)
        assert lead.id is not None
        assert lead.status == "NEW"
        assert lead.enquiry_type == "CORPORATE_EVENT"

        # Verify lead audit log
        audit = db.query(AuditLog).filter(
            AuditLog.entity_type == "LEAD",
            AuditLog.entity_id == lead.id,
        ).first()
        assert audit is not None
        assert "Rahul Malhotra" in audit.details
    finally:
        db.close()

# 6. Test Lead Review Workflow & Export
def test_lead_lifecycle_and_export():
    db = TestingSessionLocal()
    try:
        leads = list_leads(outlet_id=1, db=db)
        assert len(leads) >= 1
        target_lead = leads[0]

        # Update status -> PROPOSAL_SENT
        updated = update_lead_status(
            lead_id=target_lead.id,
            status_update=LeadStatusUpdate(
                status="PROPOSAL_SENT",
                notes="Customized 4-course menu proposal dispatched via email.",
            ),
            db=db,
        )
        assert updated.status == "PROPOSAL_SENT"
        assert "Customized 4-course menu proposal" in updated.notes

        # Export leads CSV
        resp = export_leads_csv(environment="DEMO", db=db)
        content = resp.body.decode("utf-8")
        assert "Reference ID" in content
        assert "Customer Name" in content
        assert "Rahul Malhotra" in content
        assert "PROPOSAL_SENT" in content
    finally:
        db.close()

if __name__ == "__main__":
    setup_module()
    try:
        print("[1/6] Testing standard reservation creation...")
        test_create_reservation_standard()
        print("  -> PASSED")

        print("[2/6] Testing reservation capacity overflow trigger...")
        test_create_reservation_capacity_overflow()
        print("  -> PASSED")

        print("[3/6] Testing admin reservation status lifecycle & audit log...")
        test_reservation_admin_lifecycle()
        print("  -> PASSED")

        print("[4/6] Testing reservations CSV export...")
        test_reservations_csv_export()
        print("  -> PASSED")

        print("[5/6] Testing event lead creation...")
        test_create_event_lead()
        print("  -> PASSED")

        print("[6/6] Testing lead review workflow & CSV export...")
        test_lead_lifecycle_and_export()
        print("  -> PASSED")

        print("\nALL 6 PHASE 5 WORKFLOW TESTS PASSED SUCCESSFULLY!")
    finally:
        teardown_module()
