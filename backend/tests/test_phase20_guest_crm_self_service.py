import sys
import os
import time
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

# Ensure utf-8 encoding on Windows console
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException

from app.database import Base
import app.database
from app.config import settings
from app.models.user import User
from app.models.outlet import Outlet
from app.models.reservation import ReservationRequest, ReservationStatusHistory
from app.models.guest import GuestProfile, GuestVerification, GuestAccessAudit, ReservationModificationRequest
from app.models.audit import EnvironmentSetting, AuditLog
from app.models.notification import NotificationLog
from app.schemas.guest import (
    GuestLookupRequest,
    GuestVerifyOtpRequest,
    GuestReservationModifyRequest,
    GuestReservationCancelRequest,
    GuestProfileUpdate,
    ReservationModificationReviewRequest,
)
from app.services.guest_crm_service import guest_crm_service
from app.services.guest_self_service import guest_self_service
from app.services.reservation_lifecycle_service import reservation_lifecycle_service
from app.services.notification_service import notification_service
from app.routers.guest import verify_guest_session_token
from app.routers.crm import (
    list_guests,
    get_guest_profile,
    update_guest_profile,
    list_modification_requests,
    review_modification_request,
)
from app.routers.reservations import create_reservation, ReservationCreate
from app.utils.security import hash_password

TEST_DB_PATH = os.path.join(backend_dir, "test_phase20_crm.db")
if os.path.exists(TEST_DB_PATH):
    try:
        os.remove(TEST_DB_PATH)
    except Exception:
        pass

engine = create_engine(f"sqlite:///{TEST_DB_PATH}", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app.database.SessionLocal = TestingSessionLocal
app.database.engine = engine

def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        # Environment
        env = EnvironmentSetting(
            active_environment="DEMO",
            updated_by_name="Lead Auditor",
            switch_reason="Phase 20 CRM & Self-Service Test Suite",
        )
        db.add(env)

        # Outlets
        outlet1 = Outlet(
            id=1,
            name="Amber Terrace Rooftop",
            slug="amber-terrace",
            outlet_type="Rooftop Lounge",
            cuisine_type="Pan-Asian & Cocktails",
            opening_time="18:00",
            closing_time="01:00",
            seating_capacity=80,
            location="Level 12, Tower A, Mumbai",
            is_active=True,
        )
        outlet2 = Outlet(
            id=2,
            name="Saffron & Silk",
            slug="saffron-silk",
            outlet_type="Fine Dining",
            cuisine_type="Awadhi & Royal Indian",
            opening_time="12:30",
            closing_time="23:30",
            seating_capacity=50,
            location="Ground Floor, Grand Atrium, Mumbai",
            is_active=True,
        )
        db.add_all([outlet1, outlet2])
        db.commit()

        # Users
        superadmin = User(
            id=1,
            email="superadmin@amithospitality.com",
            password_hash=hash_password("SuperSecure123!"),
            full_name="Corporate Director",
            role="SUPER_ADMIN",
            is_active=True,
        )
        manager1 = User(
            id=2,
            email="manager1@amithospitality.com",
            password_hash=hash_password("ManagerSecure123!"),
            full_name="Vikram Sethi",
            role="MANAGER",
            outlet_id=1,
            is_active=True,
        )
        manager2 = User(
            id=3,
            email="manager2@amithospitality.com",
            password_hash=hash_password("ManagerSecure123!"),
            full_name="Pooja Batra",
            role="MANAGER",
            outlet_id=2,
            is_active=True,
        )
        staff1 = User(
            id=4,
            email="staff1@amithospitality.com",
            password_hash=hash_password("StaffSecure123!"),
            full_name="Amit Kumar",
            role="STAFF",
            outlet_id=1,
            is_active=True,
        )
        db.add_all([superadmin, manager1, manager2, staff1])
        db.commit()
    finally:
        db.close()

def teardown_db():
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass

def run_phase20_suite():
    print("=" * 80)
    print("   AMIT AI CONCIERGE: PHASE 20 CRM & SECURE SELF-SERVICE TEST SUITE")
    print("=" * 80)

    setup_db()
    db = TestingSessionLocal()

    try:
        superadmin = db.query(User).filter(User.email == "superadmin@amithospitality.com").first()
        manager1 = db.query(User).filter(User.email == "manager1@amithospitality.com").first()
        manager2 = db.query(User).filter(User.email == "manager2@amithospitality.com").first()
        staff1 = db.query(User).filter(User.email == "staff1@amithospitality.com").first()

        # ----------------------------------------------------------------------
        # 1. UNIFIED GUEST CRM: IDENTITY MATCHING & DEDUPLICATION
        # ----------------------------------------------------------------------
        print("\n>>> 1. Testing Unified Guest Profile Resolution & Deduplication...")

        # Guest 1: First booking
        g1 = guest_crm_service.resolve_or_create_guest_profile(
            db=db,
            full_name="Aarav Mehra",
            phone="+91 98765 43210",
            email="aarav.mehra@example.com",
            outlet_id=1,
            environment="DEMO",
        )
        db.commit()
        assert g1.id is not None
        assert g1.guest_uuid.startswith("GST-")
        assert g1.phone_normalized == "+919876543210"
        assert g1.email_normalized == "aarav.mehra@example.com"
        assert g1.total_visits == 1
        print(f"    [PASS] Created initial guest profile: #{g1.id} ({g1.guest_uuid}) for {g1.full_name}.")

        # Guest 1: Second booking with slight phone formatting variance
        g1_repeat = guest_crm_service.resolve_or_create_guest_profile(
            db=db,
            full_name="Aarav Mehra",
            phone="+91-98765-43210",
            email="aarav.mehra@example.com",
            outlet_id=1,
            environment="DEMO",
        )
        db.commit()
        assert g1_repeat.id == g1.id, "Repeat phone number must resolve to existing profile"
        assert g1_repeat.total_visits == 2, f"Expected 2 visits, got {g1_repeat.total_visits}"
        print(f"    [PASS] Deduplicated repeat guest by normalized phone: Total visits incremented to {g1_repeat.total_visits}.")

        # Guest 2: Different person with same first name, different contact
        g2 = guest_crm_service.resolve_or_create_guest_profile(
            db=db,
            full_name="Aarav Mehra",
            phone="+91 99999 11111",
            email="other.aarav@example.com",
            outlet_id=2,
            environment="DEMO",
        )
        db.commit()
        assert g2.id != g1.id, "Must NOT merge distinct guests solely on name similarity"
        print(f"    [PASS] Correctly distinguished separate guest #{g2.id} with similar name but different contact.")

        # ----------------------------------------------------------------------
        # 2. RESERVATION CREATION WITH GUEST CRM LINKAGE
        # ----------------------------------------------------------------------
        print("\n>>> 2. Testing Reservation Creation with Automatic Guest Profile Linkage...")

        res_in = ReservationCreate(
            outlet_id=1,
            guest_name="Rohan Singhania",
            guest_email="rohan.s@example.com",
            guest_phone="+919811122233",
            reservation_date="2026-12-20",
            reservation_time="20:00",
            guest_count=4,
            seating_preference="ROOFTOP",
            special_requests="Window table for anniversary celebration",
            environment="DEMO",
        )
        created_res = create_reservation(req=res_in, db=db)
        assert created_res.id is not None
        assert created_res.guest_profile_id is not None, "Reservation must be linked to a GuestProfile"
        
        linked_profile = db.query(GuestProfile).filter(GuestProfile.id == created_res.guest_profile_id).first()
        assert linked_profile is not None
        assert linked_profile.full_name == "Rohan Singhania"
        assert linked_profile.phone_normalized == "+919811122233"
        print(f"    [PASS] Reservation {created_res.reference_id} automatically linked to GuestProfile #{linked_profile.id}.")

        # ----------------------------------------------------------------------
        # 3. SECURE GUEST BOOKING LOOKUP & 2FA OTP VERIFICATION
        # ----------------------------------------------------------------------
        print("\n>>> 3. Testing Secure Booking Lookup & Expiring OTP Verification...")

        ref_id = created_res.reference_id

        # 3A. Invalid reference ID lookup
        try:
            guest_self_service.request_verification(db, reference_id="REF-INVALID-12345", contact="+919811122233")
            assert False, "Non-existent reference must return HTTP 404"
        except HTTPException as e:
            assert e.status_code == 404
            print(f"    [PASS] Non-existent booking reference rejected with HTTP 404.")

        # 3B. Contact mismatch (valid reference, wrong phone)
        try:
            guest_self_service.request_verification(db, reference_id=ref_id, contact="+919999999999")
            assert False, "Contact mismatch must return HTTP 404 to prevent enumeration"
        except HTTPException as e:
            assert e.status_code == 404
            print(f"    [PASS] Contact mismatch safely rejected without disclosing booking details.")

        # 3C. Valid lookup request (returns simulated OTP in DEMO mode)
        lookup_res = guest_self_service.request_verification(
            db,
            reference_id=ref_id,
            contact="+919811122233",
            ip_address="127.0.0.1",
            user_agent="Mozilla/5.0 LuxuryClient/1.0",
        )
        assert lookup_res["status"] == "VERIFICATION_DISPATCHED"
        assert lookup_res["target_type"] == "PHONE"
        assert lookup_res["demo_otp"] is not None
        otp = lookup_res["demo_otp"]
        print(f"    [PASS] OTP dispatched to masked target {lookup_res['target_masked']} (Code: {otp}).")

        # 3D. Verify with wrong OTP code
        try:
            guest_self_service.verify_otp_and_issue_token(db, reference_id=ref_id, otp="000000")
            assert False, "Invalid OTP must be rejected"
        except HTTPException as e:
            assert e.status_code == 400
            assert "Invalid verification code" in e.detail
            print(f"    [PASS] Invalid OTP rejected with HTTP 400.")

        # 3E. Verify with correct OTP
        auth_session = guest_self_service.verify_otp_and_issue_token(db, reference_id=ref_id, otp=otp)
        assert "access_token" in auth_session
        assert auth_session["reservation"]["reference_id"] == ref_id
        guest_token = auth_session["access_token"]
        print(f"    [PASS] OTP verified successfully; issued signed guest JWT (expires in {auth_session['expires_in_seconds']}s).")

        # 3F. Replay defense: verify OTP code cannot be re-used
        try:
            guest_self_service.verify_otp_and_issue_token(db, reference_id=ref_id, otp=otp)
            assert False, "Consumed OTP must be rejected"
        except HTTPException as e:
            assert e.status_code == 400
            print(f"    [PASS] Consumed OTP replay rejected.")

        # 3G. Token scope enforcement: token for ref_id cannot access another reservation
        valid_auth_header = f"Bearer {guest_token}"
        # Valid access
        payload = verify_guest_session_token(reference_id=ref_id, authorization=valid_auth_header)
        assert payload["ref"] == ref_id
        # Cross-reservation access attempt
        try:
            verify_guest_session_token(reference_id="REF-OTHER-99999", authorization=valid_auth_header)
            assert False, "Guest token scoped to ref_id must not access different reference"
        except HTTPException as e:
            assert e.status_code == 403
            print(f"    [PASS] Cross-booking token access strictly forbidden with HTTP 403.")

        # ----------------------------------------------------------------------
        # 4. SELF-SERVICE MODIFICATION & CONCURRENCY / CAPACITY VALIDATION
        # ----------------------------------------------------------------------
        print("\n>>> 4. Testing Self-Service Reservation Modification & Capacity Validation...")

        # 4A. Normal modification (within standard capacity & auto-apply)
        mod_req = GuestReservationModifyRequest(
            reservation_time="20:30",
            guest_count=4,
            special_requests="Corner table with champagne on arrival",
        )
        mod_res = guest_self_service.modify_verified_reservation(db=db, reference_id=ref_id, req=mod_req)
        assert mod_res["status"] == "APPLIED"
        assert mod_res["reservation"]["reservation_time"] == "20:30"
        assert mod_res["reservation"]["status"] == "MODIFIED"
        print("    [PASS] Self-service modification applied automatically (Status -> MODIFIED).")

        # 4B. Large party modification (> 6 guests): Must stage for Manager Approval
        large_mod = GuestReservationModifyRequest(guest_count=12)
        large_res = guest_self_service.modify_verified_reservation(db=db, reference_id=ref_id, req=large_mod)
        assert large_res["status"] == "PENDING_APPROVAL"
        assert "manager review" in large_res["message"].lower()

        # Verify staged in reservation_modification_requests table
        staged_mod = db.query(ReservationModificationRequest).filter(
            ReservationModificationRequest.reference_id == ref_id,
            ReservationModificationRequest.status == "PENDING_APPROVAL",
        ).first()
        assert staged_mod is not None
        assert staged_mod.new_guest_count == 12
        print("    [PASS] Large party modification safely flagged as PENDING_APPROVAL for Manager review.")

        # 4C. Manager reviews and approves the modification
        review_in = ReservationModificationReviewRequest(action="APPROVE", review_notes="Table #8 reallocated for VIP anniversary party")
        review_res = review_modification_request(request_id=staged_mod.id, req=review_in, current_user=manager1, db=db)
        assert review_res["status"] == "APPLIED"

        db.expire_all()
        updated_res_obj = db.query(ReservationRequest).filter(ReservationRequest.reference_id == ref_id).first()
        assert updated_res_obj.guest_count == 12
        print("    [PASS] Outlet Manager approved staged modification; capacity and covers updated to 12.")

        # ----------------------------------------------------------------------
        # 5. RESERVATION LIFECYCLE STATE MACHINE VALIDATION
        # ----------------------------------------------------------------------
        print("\n>>> 5. Testing Reservation Lifecycle State Machine Transitions...")

        # 5A. Valid transition: MODIFIED -> ACCEPTED
        res_accept = reservation_lifecycle_service.transition_status(
            db=db,
            reservation_id=created_res.id,
            target_status="ACCEPTED",
            actor_name="Vikram Sethi",
            actor_role="MANAGER",
            notes="Confirmed table availability",
        )
        assert res_accept.status == "ACCEPTED"
        print("    [PASS] Valid transition MODIFIED -> ACCEPTED permitted.")

        # 5B. Valid transition: ACCEPTED -> COMPLETED
        res_done = reservation_lifecycle_service.transition_status(
            db=db,
            reservation_id=created_res.id,
            target_status="COMPLETED",
            actor_name="Front Desk Hostess",
            actor_role="STAFF",
            notes="Guest party seated and bill settled",
        )
        assert res_done.status == "COMPLETED"
        print("    [PASS] Valid transition ACCEPTED -> COMPLETED permitted.")

        # 5C. Invalid transition from terminal state: COMPLETED -> CANCELLED (Must be blocked)
        try:
            reservation_lifecycle_service.transition_status(
                db=db,
                reservation_id=created_res.id,
                target_status="CANCELLED",
                actor_name="Guest (Self-Service)",
                actor_role="GUEST",
            )
            assert False, "Transitioning from terminal state COMPLETED must be blocked"
        except HTTPException as e:
            assert e.status_code == 400
            assert "Invalid reservation lifecycle transition" in e.detail
            print(f"    [PASS] Blocked illegal transition from terminal COMPLETED state with HTTP 400.")

        # ----------------------------------------------------------------------
        # 6. SELF-SERVICE CANCELLATION WORKFLOW
        # ----------------------------------------------------------------------
        print("\n>>> 6. Testing Self-Service Booking Cancellation Workflow...")

        # Create a fresh booking for cancellation test
        fresh_res_in = ReservationCreate(
            outlet_id=1,
            guest_name="Deepak Chopra",
            guest_email="deepak.c@example.com",
            guest_phone="+919822233344",
            reservation_date="2026-12-25",
            reservation_time="19:00",
            guest_count=2,
            environment="DEMO",
        )
        cancel_target = create_reservation(req=fresh_res_in, db=db)
        
        cancel_res = guest_self_service.cancel_verified_reservation(
            db=db,
            reference_id=cancel_target.reference_id,
            reason="Change of travel plans to Bangalore",
        )
        assert cancel_res["status"] == "CANCELLED"
        assert cancel_res["reservation"]["status"] == "CANCELLED"

        # Verify repeated cancellation fails
        try:
            guest_self_service.cancel_verified_reservation(
                db=db,
                reference_id=cancel_target.reference_id,
                reason="Cancelling again",
            )
            assert False, "Repeated cancellation must be blocked"
        except HTTPException as e:
            assert e.status_code == 400
            print("    [PASS] Repeated cancellation of already cancelled booking blocked.")

        # ----------------------------------------------------------------------
        # 7. ADMIN GUEST CRM: RBAC, SEARCH & TENANT ISOLATION
        # ----------------------------------------------------------------------
        print("\n>>> 7. Testing Admin Guest CRM: RBAC & Multi-Outlet Isolation...")

        # 7A. SuperAdmin lists all guests
        all_guests_data = list_guests(current_user=superadmin, db=db)
        assert all_guests_data["total"] >= 2
        print(f"    [PASS] SuperAdmin successfully listed all {all_guests_data['total']} CRM guest profiles.")

        # 7B. Outlet isolation: Manager 1 vs Manager 2
        m1_guests = list_guests(current_user=manager1, db=db)
        m2_guests = list_guests(current_user=manager2, db=db)

        # Manager 1 sees guests associated with Outlet 1
        m1_ids = [g["id"] for g in m1_guests["guests"]]
        assert g1.id in m1_ids, "Manager 1 must see Guest 1 (Amber Terrace)"
        
        # Cross-outlet inspection
        try:
            get_guest_profile(guest_id=g2.id, current_user=manager1, db=db)
            assert False, "Manager 1 must be blocked from inspecting Guest 2 associated exclusively with Outlet 2"
        except HTTPException as e:
            assert e.status_code == 403
            assert "Cross-outlet access forbidden" in e.detail
            print("    [PASS] Manager 1 blocked from cross-outlet guest inspection with HTTP 403.")

        # 7C. Update guest preferences and dietary flags
        pref_update = GuestProfileUpdate(
            dietary_preferences="VEGAN",
            allergies="Peanuts, Tree Nuts",
            special_occasions="Birthday: Dec 25",
            vip_status=True,
            staff_notes="Prefers quiet corner table away from speakers.",
        )
        updated_profile = update_guest_profile(guest_id=g1.id, req=pref_update, current_user=manager1, db=db)
        assert updated_profile["dietary_preferences"] == "VEGAN"
        assert updated_profile["vip_status"] is True
        assert updated_profile["allergies"] == "Peanuts, Tree Nuts"
        print("    [PASS] Manager updated guest preferences and designated VIP status.")

        # 7D. Staff role cannot toggle VIP status
        staff_vip_attempt = GuestProfileUpdate(vip_status=False)
        try:
            update_guest_profile(guest_id=g1.id, req=staff_vip_attempt, current_user=staff1, db=db)
            assert False, "Staff role must be prohibited from changing VIP designation"
        except HTTPException as e:
            assert e.status_code == 403
            assert "Staff role is not authorized" in e.detail
            print("    [PASS] Staff role prohibited from toggling VIP status with HTTP 403.")

        # ----------------------------------------------------------------------
        # 8. NOTIFICATION CONCURRENCY & ATOMIC CLAIM
        # ----------------------------------------------------------------------
        print("\n>>> 8. Testing Database-Backed Atomic Notification Claim Concurrency...")

        test_key = f"concurrent_test_key_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        def claim_worker(worker_id: int):
            return notification_service.atomic_claim_notification(
                idempotency_key=test_key,
                entity_type="RESERVATION",
                entity_id=1,
                reference_id="REF-CONCURRENT-001",
                channel="EMAIL",
                recipient="concurrent@example.com",
                event_type="RESERVATION_NEW",
                environment="DEMO",
                outlet_id=1,
            )

        # 10 workers concurrently compete to claim the exact same idempotency_key
        with ThreadPoolExecutor(max_workers=10) as executor:
            claim_results = list(executor.map(claim_worker, range(10)))

        success_count = sum(1 for res in claim_results if res is True)
        suppressed_count = sum(1 for res in claim_results if res is False)

        assert success_count == 1, f"Exactly 1 worker must acquire atomic claim, got {success_count}"
        assert suppressed_count == 9, f"Exactly 9 workers must be suppressed, got {suppressed_count}"
        print(f"    [PASS] Atomic DB claim resolved: Exactly 1 worker won claim, 9 concurrent duplicate requests safely suppressed.")

        print("\n" + "=" * 80)
        print("   ALL PHASE 20 BACKEND TESTS PASSED SUCCESSFULLY! (100%)")
        print("=" * 80)

    finally:
        db.close()
        teardown_db()

if __name__ == "__main__":
    run_phase20_suite()
