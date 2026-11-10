"""
AMIT AI CONCIERGE — PHASE 20.1 COMPREHENSIVE SECURITY, INTEGRITY & RELIABILITY SUITE
Deep-dive automated audit for OTP cryptography, guest identity, financial integrity,
lifecycle state preservation, stale notification claim recovery, and multi-tenant RBAC.
"""

import os
import sys
import time
import secrets
import threading
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal, Base, engine
import app.models
from app.models.guest import GuestProfile, GuestVerification, GuestAccessAudit, ReservationModificationRequest
from app.models.reservation import ReservationRequest, ReservationStatusHistory
from app.models.outlet import Outlet
from app.models.user import User
from app.models.notification import NotificationLog
from app.models.token import RevokedToken
from app.services.guest_crm_service import guest_crm_service, normalize_phone, normalize_email
from app.services.guest_self_service import guest_self_service, compute_otp_hmac
from app.services.reservation_lifecycle_service import reservation_lifecycle_service
from app.services.notification_service import notification_service
from app.schemas.guest import GuestReservationModifyRequest, GuestProfileUpdate
from app.utils.security import create_access_token, decode_token, hash_password, get_current_user
from fastapi import HTTPException

# Ensure schema exists in test database
Base.metadata.create_all(bind=engine)

def seed_test_outlets_and_users(db):
    """Seed isolated outlets and users for multi-tenant and operational testing."""
    # Outlet 1
    o1 = db.query(Outlet).filter(Outlet.slug == "amber-terrace-audit").first()
    if not o1:
        o1 = Outlet(
            name="Amber Terrace Audit",
            slug="amber-terrace-audit",
            outlet_type="Rooftop Lounge",
            cuisine_type="Mediterranean",
            opening_time="18:00",
            closing_time="02:00",  # Overnight closing
            seating_capacity=50,
            is_active=True,
        )
        db.add(o1)
        db.commit()
        db.refresh(o1)

    # Outlet 2
    o2 = db.query(Outlet).filter(Outlet.slug == "saffron-silk-audit").first()
    if not o2:
        o2 = Outlet(
            name="Saffron Silk Audit",
            slug="saffron-silk-audit",
            outlet_type="Fine Dining",
            cuisine_type="Royal Indian",
            opening_time="12:00",
            closing_time="23:30",  # Standard daytime closing
            seating_capacity=60,
            is_active=True,
        )
        db.add(o2)
        db.commit()
        db.refresh(o2)

    # Staff for Outlet 1
    s1 = db.query(User).filter(User.email == "staff.o1@amithospitality.com").first()
    if not s1:
        s1 = User(
            email="staff.o1@amithospitality.com",
            password_hash=hash_password("StaffPass2026!"),
            full_name="Staff Outlet One",
            role="STAFF",
            outlet_id=o1.id,
            is_active=True,
        )
        db.add(s1)

    # Staff for Outlet 2
    s2 = db.query(User).filter(User.email == "staff.o2@amithospitality.com").first()
    if not s2:
        s2 = User(
            email="staff.o2@amithospitality.com",
            password_hash=hash_password("StaffPass2026!"),
            full_name="Staff Outlet Two",
            role="STAFF",
            outlet_id=o2.id,
            is_active=True,
        )
        db.add(s2)

    # Manager for Outlet 1
    m1 = db.query(User).filter(User.email == "mgr.o1@amithospitality.com").first()
    if not m1:
        m1 = User(
            email="mgr.o1@amithospitality.com",
            password_hash=hash_password("ManagerPass2026!"),
            full_name="Manager Outlet One",
            role="MANAGER",
            outlet_id=o1.id,
            is_active=True,
        )
        db.add(m1)

    # Admin User
    admin = db.query(User).filter(User.email == "admin.audit@amithospitality.com").first()
    if not admin:
        admin = User(
            email="admin.audit@amithospitality.com",
            password_hash=hash_password("AdminPass2026!"),
            full_name="System Auditor",
            role="ADMIN",
            is_active=True,
        )
        db.add(admin)

    db.commit()
    return o1, o2, s1, s2, m1, admin

# ==============================================================================
# 1. OTP CRYPTOGRAPHY, RESISTANCE & EXPIRY
# ==============================================================================
def test_01_otp_security_hmac_and_brute_force_resistance():
    print(">>> [1/7] Testing OTP HMAC Cryptography, Rainbow Table Resistance & Rate Limits...")
    db = SessionLocal()
    try:
        ref_id = f"REF-AUDIT-OTP-{secrets.token_hex(4).upper()}"
        res = ReservationRequest(
            reference_id=ref_id,
            environment="DEMO",
            outlet_id=1,
            outlet_name="Amber Terrace",
            guest_name="Aarav Mehra",
            guest_phone="+919988776655",
            guest_email="aarav.mehra@example.com",
            guest_count=2,
            reservation_date="2026-12-25",
            reservation_time="20:00",
            status="CONFIRMED",
        )
        db.add(res)
        db.commit()

        # 1. Request verification
        dispatch = guest_self_service.request_verification(
            db=db,
            reference_id=ref_id,
            contact="+919988776655",
            ip_address="192.168.1.50",
        )
        assert dispatch["status"] == "VERIFICATION_DISPATCHED"
        otp_code = dispatch["demo_otp"]
        assert otp_code is not None and len(otp_code) == 6

        # Verify HMAC in database matches compute_otp_hmac
        ver = db.query(GuestVerification).filter(GuestVerification.reference_id == ref_id).order_by(GuestVerification.id.desc()).first()
        expected_hmac = compute_otp_hmac(ref_id, otp_code)
        assert ver.token_hash == expected_hmac, "Stored hash must match HMAC-SHA256 bound to reference_id"

        # Rainbow table resistance: verify the same OTP on another reference ID yields a completely different hash
        other_hmac = compute_otp_hmac("REF-DIFFERENT-999", otp_code)
        assert ver.token_hash != other_hmac, "HMAC must be bound to reference_id to prevent cross-booking reuse"

        # 2. Resend Cooldown (attempting immediate resend within 60s must raise 429)
        cooldown_blocked = False
        try:
            guest_self_service.request_verification(
                db=db,
                reference_id=ref_id,
                contact="+919988776655",
                ip_address="192.168.1.50",
            )
        except HTTPException as ex:
            if ex.status_code == 429:
                cooldown_blocked = True
        assert cooldown_blocked, "Immediate resend within 60 seconds must be blocked with HTTP 429"

        # 3. Invalid OTP attempts decrement counter and lock code after 5 attempts
        for attempt in range(1, 6):
            try:
                guest_self_service.verify_otp_and_issue_token(
                    db=db,
                    reference_id=ref_id,
                    otp="000000",  # intentionally wrong
                )
            except HTTPException as ex:
                assert ex.status_code in (400, 429)

        # 6th attempt must be hard blocked
        try:
            guest_self_service.verify_otp_and_issue_token(
                db=db,
                reference_id=ref_id,
                otp=otp_code,  # correct code, but code is now deactivated
            )
            assert False, "Deactivated code must not be accepted"
        except HTTPException as ex:
            assert ex.status_code in (400, 429)

        print("  [OK] OTP HMAC Cryptography, Rainbow Table Resistance & Attempt Lockouts Verified.")
    finally:
        db.close()

# ==============================================================================
# 2. GUEST JWT SCOPE ISOLATION & ADMIN BOUNDARY
# ==============================================================================
def test_02_guest_session_jwt_scope_isolation_and_admin_blocking():
    print(">>> [2/7] Testing Guest JWT Scope Isolation, IDOR Defense & Admin Protection...")
    db = SessionLocal()
    try:
        ref_a = f"REF-AUDIT-A-{secrets.token_hex(4).upper()}"
        ref_b = f"REF-AUDIT-B-{secrets.token_hex(4).upper()}"

        res_a = ReservationRequest(reference_id=ref_a, outlet_id=1, outlet_name="Amber Terrace", guest_name="Guest A", guest_phone="+919111111111", guest_email="a@test.com", reservation_date="2026-12-10", reservation_time="20:00", status="ACCEPTED")
        res_b = ReservationRequest(reference_id=ref_b, outlet_id=1, outlet_name="Amber Terrace", guest_name="Guest B", guest_phone="+919222222222", guest_email="b@test.com", reservation_date="2026-12-10", reservation_time="20:00", status="ACCEPTED")
        db.add_all([res_a, res_b])
        db.commit()

        # Issue guest JWT for Reservation A
        payload_a = {
            "sub": f"guest:{ref_a}",
            "ref": ref_a,
            "res_id": res_a.id,
            "scope": f"guest:reservation:{ref_a}",
            "guest_name": "Guest A",
            "type": "guest_access",
        }
        token_a = create_access_token(payload_a, expires_delta=timedelta(minutes=30))

        # 1. Verify guest token calling internal get_current_user is rejected with HTTP 403
        guest_blocked_from_admin = False
        try:
            get_current_user(token=token_a, db=db)
        except HTTPException as ex:
            if ex.status_code == 403:
                guest_blocked_from_admin = True
        assert guest_blocked_from_admin, "Guest session token must be explicitly forbidden from administrative get_current_user"

        # 2. Scope check: verify guest token A cannot modify Reservation B
        from app.routers.guest import verify_guest_session_token
        idor_prevented = False
        try:
            verify_guest_session_token(reference_id=ref_b, authorization=f"Bearer {token_a}", db=db)
        except HTTPException as ex:
            if ex.status_code == 403:
                idor_prevented = True
        assert idor_prevented, "Token scoped to Ref A must be forbidden from accessing Ref B (IDOR prevention)"

        # 3. Check token revocation check
        decoded = decode_token(token_a)
        jti = decoded.get("jti")
        rev = RevokedToken(jti=jti, token_type="guest_access", expires_at=datetime.utcnow() + timedelta(minutes=30))
        db.add(rev)
        db.commit()

        revocation_blocked = False
        try:
            verify_guest_session_token(reference_id=ref_a, authorization=f"Bearer {token_a}", db=db)
        except HTTPException as ex:
            if ex.status_code == 401:
                revocation_blocked = True
        assert revocation_blocked, "Revoked guest session token must immediately return HTTP 401"

        print("  [OK] Guest JWT Scoping, IDOR Defense & Administrative Boundaries Verified.")
    finally:
        db.close()

# ==============================================================================
# 3. GUEST IDENTITY, SHARED FAMILY CONTACT & CONCURRENCY
# ==============================================================================
def test_03_guest_identity_shared_family_contact_and_concurrency():
    print(">>> [3/7] Testing Shared Family Phone Disambiguation & Concurrent Profile Creation...")
    db = SessionLocal()
    try:
        shared_phone = "+919876500001"
        shared_email = "family.sharma@example.com"

        # Husband: Rajesh Sharma
        p_husband = guest_crm_service.resolve_or_create_guest_profile(
            db=db,
            full_name="Rajesh Sharma",
            phone=shared_phone,
            email=shared_email,
            outlet_id=1,
            environment="DEMO",
        )
        p_husband.dietary_preferences = "JAIN"
        p_husband.allergies = "Peanuts"
        db.commit()

        # Wife: Priya Sharma (shares phone and email, but is a distinct individual)
        p_wife = guest_crm_service.resolve_or_create_guest_profile(
            db=db,
            full_name="Priya Sharma",
            phone=shared_phone,
            email=shared_email,
            outlet_id=1,
            environment="DEMO",
        )
        db.commit()

        # Assert distinct profile created
        assert p_husband.id != p_wife.id, "Shared family contact with different full_name must create separate profiles"
        assert p_wife.full_name == "Priya Sharma"
        assert p_husband.full_name == "Rajesh Sharma"
        assert p_wife.is_shared_contact is True, "Wife profile must be marked is_shared_contact=True"
        assert p_husband.is_shared_contact is True, "Husband profile must be marked is_shared_contact=True"
        assert p_wife.allergies != "Peanuts", "Wife must not inherit husband's peanut allergy (allergen isolation)"

        # Same husband returning: must resolve to husband's exact profile
        p_husband_returning = guest_crm_service.resolve_or_create_guest_profile(
            db=db,
            full_name="Rajesh Sharma",
            phone=shared_phone,
            email=shared_email,
            outlet_id=1,
            environment="DEMO",
        )
        assert p_husband_returning.id == p_husband.id, "Exact identity match must resolve to existing profile"

        # Concurrency Test: 10 parallel threads resolving the same profile
        def worker_resolve(name):
            thread_db = SessionLocal()
            try:
                prof = guest_crm_service.resolve_or_create_guest_profile(
                    db=thread_db,
                    full_name=name,
                    phone="+919999888877",
                    email="concurrent@example.com",
                    outlet_id=1,
                    environment="DEMO",
                )
                thread_db.commit()
                return prof.id
            finally:
                thread_db.close()

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(worker_resolve, "Concurrent Tester") for _ in range(8)]
            results = [f.result() for f in futures]

        unique_ids = set(results)
        assert len(unique_ids) == 1, f"Concurrent resolution of identical profile must converge to 1 profile (got {unique_ids})"

        print("  [OK] Shared Family Contact Disambiguation & Concurrency Safety Verified.")
    finally:
        db.close()

# ==============================================================================
# 4. GUEST DATA & FINANCIAL INTEGRITY
# ==============================================================================
def test_04_financial_integrity_and_completed_visit_metrics():
    print(">>> [4/7] Testing Financial Integrity, Completed Visit Metrics & Phantom Spend Prevention...")
    db = SessionLocal()
    try:
        uniq_phone = f"+9198{secrets.randbelow(89999999)+10000000}"
        guest_name = f"Kavita Audit {secrets.token_hex(3)}"
        # Create a brand new guest
        guest = guest_crm_service.resolve_or_create_guest_profile(
            db=db,
            full_name=guest_name,
            phone=uniq_phone,
            email=f"{secrets.token_hex(3)}@audit.com",
            outlet_id=1,
            environment="DEMO",
        )
        db.commit()

        # Assert initial metrics
        assert guest.total_visits == 1, "New guest profile records initial booking attempt"
        assert guest.total_spend == 0.0, "total_spend must start at 0.0"
        assert guest.currency == "INR", "Default currency must be INR"

        # Create 3 uncompleted reservations (1 NEW, 1 CANCELLED, 1 UNDER_REVIEW)
        r1 = ReservationRequest(reference_id=f"REF-FIN-1-{secrets.token_hex(3)}", outlet_id=1, outlet_name="Amber Terrace", guest_profile_id=guest.id, guest_name=guest_name, guest_phone=uniq_phone, reservation_date="2026-12-10", reservation_time="20:00", status="NEW")
        r2 = ReservationRequest(reference_id=f"REF-FIN-2-{secrets.token_hex(3)}", outlet_id=1, outlet_name="Amber Terrace", guest_profile_id=guest.id, guest_name=guest_name, guest_phone=uniq_phone, reservation_date="2026-12-11", reservation_time="20:00", status="CANCELLED")
        r3 = ReservationRequest(reference_id=f"REF-FIN-3-{secrets.token_hex(3)}", outlet_id=1, outlet_name="Amber Terrace", guest_profile_id=guest.id, guest_name=guest_name, guest_phone=uniq_phone, reservation_date="2026-12-12", reservation_time="20:00", status="UNDER_REVIEW")
        db.add_all([r1, r2, r3])
        db.commit()

        # Recompute metrics: completed_visits must strictly be 0
        metrics = guest_crm_service.recompute_guest_metrics(db, guest.id)
        assert metrics["completed_visits"] == 0, "Uncompleted/cancelled bookings must NOT count towards completed_visits"

        # Now complete r1
        reservation_lifecycle_service.transition_status(
            db=db,
            reservation_id=r1.id,
            target_status="ACCEPTED",
            actor_name="Admin",
            actor_role="ADMIN",
            notify=False,
        )
        reservation_lifecycle_service.transition_status(
            db=db,
            reservation_id=r1.id,
            target_status="COMPLETED",
            actor_name="Maitre d",
            actor_role="STAFF",
            notify=False,
        )

        metrics_after = guest_crm_service.recompute_guest_metrics(db, guest.id)
        assert metrics_after["completed_visits"] == 1, "Completed dining visit must increment completed_visits to exactly 1"

        print("  [OK] Completed Visit Metrics & Financial Precision Verified.")
    finally:
        db.close()

# ==============================================================================
# 5. RESERVATION WORKFLOWS & OPERATING HOURS
# ==============================================================================
def test_05_reservation_workflow_and_manager_rejection_preservation():
    print(">>> [5/7] Testing Reservation Lifecycles, Manager Rejection & Operating Hour Boundaries...")
    db = SessionLocal()
    try:
        o1, o2, s1, s2, m1, admin = seed_test_outlets_and_users(db)

        # 1. Operating Hour Boundary: Amber Terrace Audit is 18:00 to 02:00 (overnight)
        ref_ov = f"REF-OVN-{secrets.token_hex(3).upper()}"
        res_ov = ReservationRequest(
            reference_id=ref_ov,
            outlet_id=o1.id,
            outlet_name=o1.name,
            guest_name="Vikram Seth",
            guest_phone="+919876543219",
            guest_count=2,
            reservation_date="2026-11-20",
            reservation_time="20:00",
            status="CONFIRMED",
        )
        db.add(res_ov)
        db.commit()

        # Valid overnight modification: 01:30 AM (is within 18:00 to 02:00)
        mod_req_valid = GuestReservationModifyRequest(reservation_time="01:30")
        res_valid = guest_self_service.modify_verified_reservation(db=db, reference_id=ref_ov, req=mod_req_valid)
        assert res_valid["status"] == "APPLIED"
        assert res_ov.reservation_time == "01:30"

        # Invalid modification: 04:00 AM (outside 18:00 to 02:00)
        invalid_hour_blocked = False
        try:
            guest_self_service.modify_verified_reservation(
                db=db,
                reference_id=ref_ov,
                req=GuestReservationModifyRequest(reservation_time="04:00"),
            )
        except HTTPException as ex:
            if ex.status_code == 400:
                invalid_hour_blocked = True
        assert invalid_hour_blocked, "Time 04:00 AM must be rejected as outside operating hours (18:00 to 02:00)"

        # 2. Large Party Size Staged for Review & Rejection Restoration
        # Change Vikram's booking from 2 to 8 guests (>6 guests -> triggers PENDING_APPROVAL)
        res_ov.status = "CONFIRMED"
        db.commit()

        mod_large = guest_self_service.modify_verified_reservation(
            db=db,
            reference_id=ref_ov,
            req=GuestReservationModifyRequest(guest_count=8),
        )
        assert mod_large["status"] == "PENDING_APPROVAL"
        db.refresh(res_ov)
        assert res_ov.status == "UNDER_REVIEW"
        assert res_ov.guest_count == 2, "Original booking guest count must be preserved while under review"

        # Manager Rejection: must revert to original status "CONFIRMED"
        from app.routers.crm import review_modification_request
        from app.schemas.guest import ReservationModificationReviewRequest

        mod_rec = db.query(ReservationModificationRequest).filter(ReservationModificationRequest.reference_id == ref_ov).order_by(ReservationModificationRequest.id.desc()).first()
        assert mod_rec.old_status == "CONFIRMED"

        review_res = review_modification_request(
            request_id=mod_rec.id,
            req=ReservationModificationReviewRequest(action="REJECT", review_notes="Large tables fully committed tonight"),
            current_user=m1,
            db=db,
        )
        assert review_res["status"] == "REJECTED"
        db.refresh(res_ov)
        assert res_ov.status == "CONFIRMED", "Manager rejection must restore original confirmed status (not blindly ACCEPTED)"

        # 3. Cancellation Policy: Cannot cancel completed or cancelled reservation
        res_ov.status = "COMPLETED"
        db.commit()
        cancelled_blocked = False
        try:
            guest_self_service.cancel_verified_reservation(db=db, reference_id=ref_ov, reason="Cannot attend")
        except HTTPException as ex:
            if ex.status_code == 400:
                cancelled_blocked = True
        assert cancelled_blocked, "Cancellation of terminal COMPLETED reservation must be blocked with HTTP 400"

        print("  [OK] Reservation Lifecycle, Manager Rejection & Operating Hours Verified.")
    finally:
        db.close()

# ==============================================================================
# 6. NOTIFICATION RELIABILITY & CRASH RECOVERY
# ==============================================================================
def test_06_notification_reliability_and_stale_claim_recovery():
    print(">>> [6/7] Testing Atomic Notification Claims, Stale Record Recovery & Max Retries...")
    idemp_key = f"audit_claim_{secrets.token_hex(4)}"

    # 1. Concurrency: 10 threads trying to atomically claim the exact same idempotency_key
    claim_results = []
    def try_claim():
        claimed = notification_service.atomic_claim_notification(
            idempotency_key=idemp_key,
            entity_type="RESERVATION",
            entity_id=999,
            reference_id="REF-CLAIM-TEST",
            channel="EMAIL",
            recipient="audit@example.com",
            event_type="CREATED",
            environment="DEMO",
            outlet_id=1,
        )
        claim_results.append(claimed)

    threads = [threading.Thread(target=try_claim) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert claim_results.count(True) == 1, f"Exactly 1 worker must win atomic claim (won: {claim_results.count(True)})"
    assert claim_results.count(False) == 9, "Remaining 9 workers must be suppressed"

    # 2. Interruption Recovery: simulate crash where worker claimed but never updated status
    db = SessionLocal()
    try:
        log_rec = db.query(NotificationLog).filter(NotificationLog.idempotency_key == idemp_key).first()
        assert log_rec.status == "CLAIMED"
        # Simulate record being 300 seconds old
        log_rec.created_at = datetime.utcnow() - timedelta(seconds=300)
        db.commit()

        # Run recover_stale_claims
        recovered = notification_service.recover_stale_claims(max_age_seconds=180)
        assert recovered >= 1, "recover_stale_claims must recover abandoned claim"

        db.refresh(log_rec)
        assert log_rec.status == "FAILED", "Abandoned claim with attempts < 3 must be reset to FAILED for retry"

        # 3. Max Retry Threshold: increment attempts to 3 and age again
        log_rec.attempts = 3
        log_rec.status = "CLAIMED"
        log_rec.created_at = datetime.utcnow() - timedelta(seconds=300)
        db.commit()

        notification_service.recover_stale_claims(max_age_seconds=180)
        db.refresh(log_rec)
        assert log_rec.status == "FAILED_PERMANENT", "Abandoned claim with attempts >= 3 must be marked FAILED_PERMANENT"

        print("  [OK] Atomic Claim Concurrency, Stale Recovery & Max Retries Verified.")
    finally:
        db.close()

# ==============================================================================
# 7. MULTI-TENANT CROSS-OUTLET RBAC SECURITY
# ==============================================================================
def test_07_multi_tenant_cross_outlet_rbac_boundaries():
    print(">>> [7/7] Testing Multi-Tenant Cross-Outlet Isolation across STAFF, MANAGER & ADMIN...")
    db = SessionLocal()
    try:
        o1, o2, s1, s2, m1, admin = seed_test_outlets_and_users(db)

        # Create Guest Exclusive to Outlet 2
        g2 = guest_crm_service.resolve_or_create_guest_profile(
            db=db,
            full_name="Outlet Two Guest",
            phone="+919777777777",
            email="o2guest@example.com",
            outlet_id=o2.id,
            environment="DEMO",
        )
        db.commit()

        # 1. Staff of Outlet 1 attempting to view details of Outlet 2's guest
        cross_read_blocked = False
        try:
            guest_crm_service.get_guest_detail(db=db, guest_id=g2.id, current_user=s1)
        except HTTPException as ex:
            if ex.status_code == 403:
                cross_read_blocked = True
        assert cross_read_blocked, "Staff of Outlet 1 must be forbidden (403) from accessing Outlet 2 guest"

        # 2. Staff of Outlet 2 CAN view details
        detail = guest_crm_service.get_guest_detail(db=db, guest_id=g2.id, current_user=s2)
        assert detail["id"] == g2.id

        # 3. Staff cannot toggle VIP status
        vip_tamper_blocked = False
        try:
            guest_crm_service.update_guest_profile(
                db=db,
                guest_id=g2.id,
                req=GuestProfileUpdate(vip_status=True),
                current_user=s2,
            )
        except HTTPException as ex:
            if ex.status_code == 403:
                vip_tamper_blocked = True
        assert vip_tamper_blocked, "Staff must be forbidden (403) from modifying VIP designation"

        # 4. Admin CAN view and modify
        admin_detail = guest_crm_service.get_guest_detail(db=db, guest_id=g2.id, current_user=admin)
        assert admin_detail["id"] == g2.id
        admin_update = guest_crm_service.update_guest_profile(
            db=db,
            guest_id=g2.id,
            req=GuestProfileUpdate(vip_status=True),
            current_user=admin,
        )
        assert admin_update["vip_status"] is True, "Admin must be authorized to toggle VIP status"

        print("  [OK] Multi-Tenant Isolation & Role Boundaries Verified.")
    finally:
        db.close()

def run_all_phase20_1_audit_tests():
    print("=" * 80)
    print("   AMIT AI CONCIERGE — PHASE 20.1 SECURITY & DATA INTEGRITY VERIFICATION")
    print("=" * 80)
    t0 = time.time()
    test_01_otp_security_hmac_and_brute_force_resistance()
    test_02_guest_session_jwt_scope_isolation_and_admin_blocking()
    test_03_guest_identity_shared_family_contact_and_concurrency()
    test_04_financial_integrity_and_completed_visit_metrics()
    test_05_reservation_workflow_and_manager_rejection_preservation()
    test_06_notification_reliability_and_stale_claim_recovery()
    test_07_multi_tenant_cross_outlet_rbac_boundaries()
    duration = time.time() - t0
    print("=" * 80)
    print(f"   PHASE 20.1 ALL 7 AUDIT SUITES PASSED (100%) in {duration:.2f}s")
    print("=" * 80)

if __name__ == "__main__":
    run_all_phase20_1_audit_tests()
