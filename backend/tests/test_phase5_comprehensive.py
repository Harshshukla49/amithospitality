import sys
import os
import io
import csv
import pytest
from pydantic import ValidationError

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
from app.models.outlet import Outlet, MenuItem
from app.models.reservation import ReservationRequest, ReservationStatusHistory
from app.models.lead import Lead, LeadStatusHistory
from app.models.audit import EnvironmentSetting, AuditLog
from app.routers.reservations import (
    create_reservation,
    list_reservations,
    get_reservation_detail,
    update_reservation_status,
    get_reservation_history,
    export_reservations_csv,
)
from app.routers.leads import (
    create_lead,
    list_leads,
    get_lead_detail,
    update_lead_status,
    get_lead_history,
    export_leads_csv,
)
from app.schemas.reservation import ReservationCreate, ReservationStatusUpdate
from app.schemas.lead import LeadCreate, LeadStatusUpdate
from app.services.intent_service import detect_intent
from app.services.rag_service import build_deterministic_concierge_response

TEST_DB_PATH = os.path.join(backend_dir, "test_phase5_comprehensive.db")
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
            password_hash="argon2id_hash_sample",
            full_name="Vikram Sharma",
            role="SUPER_ADMIN",
            is_active=True,
        )
        staff = User(
            id=2,
            email="host@amithospitality.com",
            password_hash="argon2id_hash_sample",
            full_name="Priya Hostess",
            role="STAFF",
            is_active=True,
        )
        db.add(admin)
        db.add(staff)

        outlet = Outlet(
            id=1,
            name="Amber Terrace Rooftop",
            slug="amber-terrace",
            outlet_type="Rooftop Lounge",
            cuisine_type="Modern Pan-Asian",
            opening_time="17:30",
            closing_time="01:30",
            dress_code="Smart Casual",
            seating_capacity=40,
            location="14th Floor, Skyline Tower",
            description="Luxury panoramic dining",
        )
        db.add(outlet)

        setting = EnvironmentSetting(
            active_environment="DEMO",
            updated_by_name="Setup",
            switch_reason="Phase 5 Test Suite Initialization",
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

# ==============================================================================
# 1. RESERVATION CREATION & REFERENCE ID GENERATION
# ==============================================================================
def test_reservation_creation_success():
    db = TestingSessionLocal()
    try:
        req = ReservationCreate(
            outlet_id=1,
            guest_name="Aarav Singhania",
            guest_phone="+91 98201 55667",
            guest_email="aarav@singhania.com",
            guest_count=4,
            reservation_date="2026-11-20",
            reservation_time="20:30",
            seating_preference="ROOFTOP",
            special_requests="Anniversary dinner. Window table requested.",
        )
        res = create_reservation(req=req, db=db)
        assert res.id is not None
        assert res.reference_id is not None
        assert res.reference_id.startswith("REF-RES-")
        assert res.status == "NEW"
        assert res.guest_name == "Aarav Singhania"
        assert res.outlet_name == "Amber Terrace Rooftop"

        # Verify initial history record
        hist = db.query(ReservationStatusHistory).filter(
            ReservationStatusHistory.reservation_id == res.id
        ).all()
        assert len(hist) == 1
        assert hist[0].new_status == "NEW"
        assert hist[0].previous_status is None
    finally:
        db.close()

# ==============================================================================
# 2. RESERVATION VALIDATION (FAILED SCENARIOS)
# ==============================================================================
def test_reservation_validation_failures():
    # Test phone too short (< 7 digits)
    with pytest.raises(ValidationError):
        ReservationCreate(
            outlet_id=1,
            guest_name="Raj",
            guest_phone="12345",  # Too short
            guest_count=2,
            reservation_date="2026-11-20",
            reservation_time="20:00",
            seating_preference="INDOOR",
        )

    # Test empty guest name
    with pytest.raises(ValidationError):
        ReservationCreate(
            outlet_id=1,
            guest_name="   ",  # Blank
            guest_phone="+91 98220 11223",
            guest_count=2,
            reservation_date="2026-11-20",
            reservation_time="20:00",
            seating_preference="INDOOR",
        )

    # Test invalid date format
    with pytest.raises(ValidationError):
        ReservationCreate(
            outlet_id=1,
            guest_name="Valid Name",
            guest_phone="+91 98220 11223",
            guest_count=2,
            reservation_date="20-11-2026",  # Not YYYY-MM-DD
            reservation_time="20:00",
            seating_preference="INDOOR",
        )

# ==============================================================================
# 3. RESERVATION CAPACITY CHECK
# ==============================================================================
def test_reservation_capacity_warning():
    db = TestingSessionLocal()
    try:
        # Outlet capacity is 40. Request 45 covers!
        req = ReservationCreate(
            outlet_id=1,
            guest_name="Large Corporate Delegation",
            guest_phone="+91 98111 22334",
            guest_count=45,
            reservation_date="2026-11-20",
            reservation_time="20:30",
            seating_preference="INDOOR",
            special_requests="Need full floor space",
        )
        res = create_reservation(req=req, db=db)
        assert res.status == "UNDER_REVIEW"
        assert res.capacity_warning is not None
        assert "High occupancy alert" in res.capacity_warning
    finally:
        db.close()

# ==============================================================================
# 4. RESERVATION STATUS WORKFLOW & HISTORY TIMELINE
# ==============================================================================
def test_reservation_status_workflow_and_history():
    db = TestingSessionLocal()
    try:
        # Create a reservation
        req = ReservationCreate(
            outlet_id=1,
            guest_name="Maya Sen",
            guest_phone="+91 98765 43210",
            guest_count=2,
            reservation_date="2026-11-22",
            reservation_time="19:30",
            seating_preference="ROOFTOP",
        )
        res = create_reservation(req=req, db=db)
        res_id = res.id

        # Transition 1: NEW -> UNDER_REVIEW
        up1 = update_reservation_status(
            res_id=res_id,
            status_update=ReservationStatusUpdate(
                status="UNDER_REVIEW",
                internal_notes="Checking terrace table availability with kitchen.",
                assigned_staff_name="Vikramaditya (Host)",
            ),
            db=db,
        )
        assert up1.status == "UNDER_REVIEW"
        assert up1.assigned_staff_name == "Vikramaditya (Host)"

        # Transition 2: UNDER_REVIEW -> ACCEPTED
        up2 = update_reservation_status(
            res_id=res_id,
            status_update=ReservationStatusUpdate(
                status="ACCEPTED",
                internal_notes="Terrace table 12 allocated. Anniversary note added.",
            ),
            db=db,
        )
        assert up2.status == "ACCEPTED"

        # Transition 3: ACCEPTED -> COMPLETED
        up3 = update_reservation_status(
            res_id=res_id,
            status_update=ReservationStatusUpdate(
                status="COMPLETED",
                internal_notes="Guest departed. Exceptional dining experience delivered.",
            ),
            db=db,
        )
        assert up3.status == "COMPLETED"

        # Verify complete status history
        history = get_reservation_history(res_id=res_id, db=db)
        assert len(history) == 4  # Initial + 3 transitions
        history_statuses = [h.new_status for h in history]
        assert "NEW" in history_statuses
        assert "UNDER_REVIEW" in history_statuses
        assert "ACCEPTED" in history_statuses
        assert "COMPLETED" in history_statuses
    finally:
        db.close()

# ==============================================================================
# 5. LEAD CREATION (CHATBOT SOURCE & MANUAL STAFF ENTRY)
# ==============================================================================
def test_lead_creation_chatbot_and_manual():
    db = TestingSessionLocal()
    try:
        # Chatbot lead
        req1 = LeadCreate(
            outlet_id=1,
            name="Rohit Mehra",
            phone="+91 98100 22334",
            email="rohit@innovate.io",
            enquiry_type="CORPORATE_EVENT",
            guest_count=30,
            target_date="2026-12-10",
            budget_range="₹2,00,000 - ₹4,00,000",
            notes="Quarterly executive dinner with live jazz quartet.",
            source="AI_CONCIERGE_WEB",
        )
        lead1 = create_lead(req=req1, db=db)
        assert lead1.id is not None
        assert lead1.reference_id is not None
        assert lead1.reference_id.startswith("REF-LEAD-")
        assert lead1.source == "AI_CONCIERGE_WEB"
        assert lead1.status == "NEW"

        # Manual Staff Entry lead
        req2 = LeadCreate(
            outlet_id=1,
            name="Ananya & Kunal Roy",
            phone="+91 99200 44556",
            email="ananya.roy@gmail.com",
            enquiry_type="WEDDING_EVENT",
            guest_count=70,
            target_date="2027-01-15",
            budget_range="₹5,00,000 - ₹8,00,000",
            notes="Walk-in inquiry for rooftop cocktail reception.",
            assigned_staff_name="Shalini Roy",
            source="STAFF_MANUAL_ENTRY",
        )
        lead2 = create_lead(req=req2, db=db)
        assert lead2.id is not None
        assert lead2.reference_id.startswith("REF-LEAD-")
        assert lead2.source == "STAFF_MANUAL_ENTRY"
        assert lead2.assigned_staff_name == "Shalini Roy"
    finally:
        db.close()

# ==============================================================================
# 6. LEAD STATUS UPDATES, ASSIGNMENT & HISTORY
# ==============================================================================
def test_lead_status_workflow_and_assignment():
    db = TestingSessionLocal()
    try:
        req = LeadCreate(
            outlet_id=1,
            name="Deepak Chawla",
            phone="+91 98300 77889",
            email="deepak@chawlagroup.com",
            enquiry_type="PRIVATE_PARTY",
            guest_count=20,
            target_date="2026-11-28",
            budget_range="₹1,50,000 - ₹3,00,000",
        )
        lead = create_lead(req=req, db=db)
        lead_id = lead.id

        # Update 1: CONTACTED with assignment
        up1 = update_lead_status(
            lead_id=lead_id,
            status_update=LeadStatusUpdate(
                status="CONTACTED",
                notes="Called client; shared 4-course bespoke menu.",
                assigned_staff_name="Arjun Banquets Manager",
            ),
            db=db,
        )
        assert up1.status == "CONTACTED"
        assert up1.assigned_staff_name == "Arjun Banquets Manager"

        # Update 2: QUALIFIED
        up2 = update_lead_status(
            lead_id=lead_id,
            status_update=LeadStatusUpdate(
                status="QUALIFIED",
                notes="Budget verified; venue walkthrough scheduled.",
            ),
            db=db,
        )
        assert up2.status == "QUALIFIED"

        # Update 3: FOLLOW_UP_REQUIRED
        up3 = update_lead_status(
            lead_id=lead_id,
            status_update=LeadStatusUpdate(
                status="FOLLOW_UP_REQUIRED",
                notes="Awaiting client board confirmation on beverage package.",
            ),
            db=db,
        )
        assert up3.status == "FOLLOW_UP_REQUIRED"

        # Update 4: CONVERTED
        up4 = update_lead_status(
            lead_id=lead_id,
            status_update=LeadStatusUpdate(
                status="CONVERTED",
                notes="Advance deposit received; buyout agreement signed.",
            ),
            db=db,
        )
        assert up4.status == "CONVERTED"

        # Verify history
        history = get_lead_history(lead_id=lead_id, db=db)
        assert len(history) == 5  # Initial + 4 transitions
        statuses = [h.new_status for h in history]
        assert "NEW" in statuses
        assert "CONTACTED" in statuses
        assert "QUALIFIED" in statuses
        assert "FOLLOW_UP_REQUIRED" in statuses
        assert "CONVERTED" in statuses
    finally:
        db.close()

# ==============================================================================
# 7. DEMO / REAL ENVIRONMENT ISOLATION
# ==============================================================================
def test_demo_real_isolation():
    db = TestingSessionLocal()
    try:
        # Create DEMO reservation
        db.query(EnvironmentSetting).filter(EnvironmentSetting.id == 1).update(
            {"active_environment": "DEMO"}
        )
        db.commit()

        demo_res = create_reservation(
            req=ReservationCreate(
                outlet_id=1,
                guest_name="Demo Guest",
                guest_phone="+91 99999 11111",
                guest_count=2,
                reservation_date="2026-11-25",
                reservation_time="20:00",
                seating_preference="ROOFTOP",
            ),
            db=db,
        )
        assert demo_res.environment == "DEMO"

        # Switch to REAL environment
        db.query(EnvironmentSetting).filter(EnvironmentSetting.id == 1).update(
            {"active_environment": "REAL"}
        )
        db.commit()

        # Query in REAL environment - demo reservation must NOT appear!
        real_reservations = list_reservations(outlet_id=1, db=db)
        real_ids = [r.id for r in real_reservations]
        assert demo_res.id not in real_ids

        # Create REAL reservation
        real_res = create_reservation(
            req=ReservationCreate(
                outlet_id=1,
                guest_name="Verified Company VIP",
                guest_phone="+91 98888 22222",
                guest_count=2,
                reservation_date="2026-11-25",
                reservation_time="20:00",
                seating_preference="ROOFTOP",
            ),
            db=db,
        )
        assert real_res.environment == "REAL"

        # Re-query REAL environment - only REAL reservation is present
        real_reservations_now = list_reservations(outlet_id=1, db=db)
        assert any(r.id == real_res.id for r in real_reservations_now)
        assert not any(r.id == demo_res.id for r in real_reservations_now)

        # Switch back to DEMO
        db.query(EnvironmentSetting).filter(EnvironmentSetting.id == 1).update(
            {"active_environment": "DEMO"}
        )
        db.commit()
    finally:
        db.close()

# ==============================================================================
# 8. CHATBOT RESERVATION & LEAD INTENT AND ZERO-HALLUCINATION WORKFLOW
# ==============================================================================
def test_chatbot_reservation_and_lead_intent():
    db = TestingSessionLocal()
    try:
        # Test 1: "I want to book a table" -> RESERVATION_REQUEST
        intent_booking = detect_intent("I want to book a table for 4 guests tonight at 8pm")
        assert intent_booking["intent"] == "RESERVATION_REQUEST"
        assert intent_booking["entities"].get("guest_count") == 4

        # Test 2: Hindi booking query
        intent_hi_booking = detect_intent("Mujhe aaj raat table chahiye 2 logo ke liye")
        assert intent_hi_booking["intent"] == "RESERVATION_REQUEST"

        # Test 3: "I want to organize a party" -> EVENT_INQUIRY
        intent_party = detect_intent("I want to organize a private birthday party for 25 people")
        assert intent_party["intent"] == "EVENT_INQUIRY"

        # Test 4: "I want to arrange a corporate event" -> EVENT_INQUIRY
        intent_corp = detect_intent("I want to arrange a corporate event for our executive board")
        assert intent_corp["intent"] == "EVENT_INQUIRY"

        # Test 5: "I want someone to contact me" -> HUMAN_HANDOVER
        intent_call = detect_intent("I want someone to contact me regarding venue buyouts")
        assert intent_call["intent"] == "HUMAN_HANDOVER"

        # Test response generation does NOT invent fake confirmation
        outlet = db.query(Outlet).filter(Outlet.id == 1).first()
        res = build_deterministic_concierge_response(
            intent="RESERVATION_REQUEST",
            outlet=outlet,
            environment="DEMO",
            chunks=[],
            menu_items=[],
            entities={"guest_count": 4},
            query="I want to book a table for 4",
            language="EN",
        )
        reply = res["reply"]
        # Must clearly state that it is a request awaiting maître d' review, not an automated table confirmation
        assert "Reference ID" in reply or "REF-RES" in reply or "request" in reply.lower()
        assert "not an automated table confirmation" in reply or "awaiting" in reply.lower()
    finally:
        db.close()

# ==============================================================================
# 9. CSV EXPORTS (RECORDS & HEADERS)
# ==============================================================================
def test_csv_exports():
    db = TestingSessionLocal()
    try:
        # Export reservations CSV
        res_resp = export_reservations_csv(environment="DEMO", db=db)
        res_text = res_resp.body.decode("utf-8")
        assert "Reference ID" in res_text
        assert "Guest Name" in res_text
        assert "Aarav Singhania" in res_text

        # Export leads CSV
        lead_resp = export_leads_csv(environment="DEMO", db=db)
        lead_text = lead_resp.body.decode("utf-8")
        assert "Reference ID" in lead_text
        assert "Enquiry Type" in lead_text
        assert "Rohit Mehra" in lead_text
    finally:
        db.close()

if __name__ == "__main__":
    setup_module()
    try:
        print("[1/9] Testing reservation creation and reference ID generation...")
        test_reservation_creation_success()
        print("  [OK] Reservation creation & reference IDs verified.")

        print("[2/9] Testing reservation Pydantic validation failures...")
        test_reservation_validation_failures()
        print("  [OK] Validation constraints verified.")

        print("[3/9] Testing reservation capacity check...")
        test_reservation_capacity_warning()
        print("  [OK] Capacity overflow warnings verified.")

        print("[4/9] Testing reservation status workflow and history...")
        test_reservation_status_workflow_and_history()
        print("  [OK] Reservation status transitions & history verified.")

        print("[5/9] Testing lead creation (chatbot and manual)...")
        test_lead_creation_chatbot_and_manual()
        print("  [OK] Lead creation verified.")

        print("[6/9] Testing lead status updates, assignment & history...")
        test_lead_status_workflow_and_assignment()
        print("  [OK] Lead assignment and history verified.")

        print("[7/9] Testing DEMO / REAL environment isolation...")
        test_demo_real_isolation()
        print("  [OK] Dual-environment isolation verified.")

        print("[8/9] Testing chatbot intent and zero-hallucination workflow...")
        test_chatbot_reservation_and_lead_intent()
        print("  [OK] Chatbot intent parsing & reservation guardrails verified.")

        print("[9/9] Testing CSV export headers and data integrity...")
        test_csv_exports()
        print("  [OK] CSV exports verified.")

        print("\n=======================================================")
        print("ALL PHASE 5 COMPREHENSIVE TESTS PASSED SUCCESSFULLY!")
        print("=======================================================")
    finally:
        teardown_module()
