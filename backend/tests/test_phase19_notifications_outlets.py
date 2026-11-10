import sys
import os
import time
from datetime import datetime, timedelta

# Ensure utf-8 encoding on Windows console
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException, BackgroundTasks

from app.database import Base
import app.database
from app.config import settings
from app.models.user import User
from app.models.outlet import Outlet, MenuItem
from app.models.reservation import ReservationRequest
from app.models.lead import Lead
from app.models.audit import EnvironmentSetting, AuditLog
from app.models.notification import NotificationLog
from app.schemas.outlet import OutletUpdate, MenuItemCreate, MenuItemUpdate
from app.schemas.reservation import ReservationCreate, ReservationStatusUpdate
from app.schemas.lead import LeadCreate
from app.routers.outlets import update_outlet, list_outlets, get_outlet, get_menus
from app.routers.reservations import create_reservation, update_reservation_status
from app.routers.leads import create_lead
from app.routers.notifications import list_notification_logs
from app.services.notification_service import notification_service
from app.utils.security import create_access_token, hash_password, require_roles

TEST_DB_PATH = os.path.join(backend_dir, "test_phase19_notifications.db")
if os.path.exists(TEST_DB_PATH):
    try:
        os.remove(TEST_DB_PATH)
    except Exception:
        pass

engine = create_engine(f"sqlite:///{TEST_DB_PATH}", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Monkeypatch SessionLocal in app.database to ensure background tasks write to the test DB
app.database.SessionLocal = TestingSessionLocal
app.database.engine = engine

def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        # 1. Environment Setting
        env_setting = EnvironmentSetting(
            active_environment="DEMO",
            updated_by_name="System",
            switch_reason="Phase 19 Foundation Stabilization",
        )
        db.add(env_setting)

        # 2. Outlets
        outlet1 = Outlet(
            id=1,
            name="Amber Terrace Rooftop",
            slug="amber-terrace",
            outlet_type="Rooftop Lounge",
            cuisine_type="Pan-Asian & Cocktails",
            opening_time="18:00",
            closing_time="01:00",
            seating_capacity=80,
            description="Open-air rooftop overlooking the skyline",
            location="Level 12, Tower A, Amit Horizon, Mumbai",
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
            seating_capacity=60,
            description="Opulent fine dining with heritage royal recipes",
            location="Ground Floor, Grand Atrium, Amit Horizon, Mumbai",
            is_active=True,
        )
        db.add_all([outlet1, outlet2])
        db.commit()

        # 3. Users with various roles
        superadmin = User(
            id=1,
            email="superadmin@amithospitality.com",
            password_hash=hash_password("SuperSecure123!"),
            full_name="Rajesh Sharma",
            role="SUPER_ADMIN",
            is_active=True,
            outlet_id=None,
        )
        manager1 = User(
            id=2,
            email="manager1@amithospitality.com",
            password_hash=hash_password("ManagerSecure123!"),
            full_name="Vikram Sethi",
            role="MANAGER",
            is_active=True,
            outlet_id=1,  # Assigned to Amber Terrace
        )
        manager2 = User(
            id=3,
            email="manager2@amithospitality.com",
            password_hash=hash_password("ManagerSecure123!"),
            full_name="Pooja Batra",
            role="MANAGER",
            is_active=True,
            outlet_id=2,  # Assigned to Saffron & Silk
        )
        staff1 = User(
            id=4,
            email="staff1@amithospitality.com",
            password_hash=hash_password("StaffSecure123!"),
            full_name="Amit Kumar",
            role="STAFF",
            is_active=True,
            outlet_id=1,
        )
        db.add_all([superadmin, manager1, manager2, staff1])
        db.commit()

        # 4. Sample Menu Items
        dish1 = MenuItem(
            id=1,
            outlet_id=1,
            environment="DEMO",
            name="Crispy Truffle Lotus Stem",
            description="Honey-chilli glaze with shaved black truffle",
            price=850.0,
            currency="INR",
            dietary_flags="VEG",
            is_available=True,
        )
        db.add(dish1)
        db.commit()
    finally:
        db.close()

def teardown_db():
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass

def run_background(bg: BackgroundTasks):
    """Helper to execute queued FastAPI BackgroundTasks synchronously."""
    if bg and hasattr(bg, "tasks"):
        for task in bg.tasks:
            task.func(*task.args, **task.kwargs)

def run_phase19_suite():
    print("=" * 80)
    print("   PHASE 19: FOUNDATION STABILIZATION & LIVE DATA INTEGRATION")
    print("   Live Outlets API, RBAC Protection, Background Notifications & Audit Trail")
    print("=" * 80)

    setup_db()
    db = TestingSessionLocal()

    try:
        superadmin = db.query(User).filter(User.email == "superadmin@amithospitality.com").first()
        manager1 = db.query(User).filter(User.email == "manager1@amithospitality.com").first()
        manager2 = db.query(User).filter(User.email == "manager2@amithospitality.com").first()
        staff1 = db.query(User).filter(User.email == "staff1@amithospitality.com").first()

        # ----------------------------------------------------------------------
        # 1. LIVE OUTLETS API PERSISTENCE & RBAC
        # ----------------------------------------------------------------------
        print("\n>>> 1. Testing Live Outlets API: PUT /api/v1/outlets/{id} & Multi-Outlet RBAC...")

        # 1A. SuperAdmin updates Outlet 1 details
        update_in = OutletUpdate(
            seating_capacity=100,
            opening_time="17:30",
            closing_time="02:00",
            location="Level 12 & Terrace, Tower A, Amit Horizon, Mumbai",
            dress_code="Glamorous Evening",
        )
        updated = update_outlet(outlet_id=1, outlet_in=update_in, current_user=superadmin, db=db)
        assert updated.seating_capacity == 100, "Seating capacity should be updated to 100"
        assert updated.opening_time == "17:30"
        assert updated.closing_time == "02:00"
        assert updated.dress_code == "Glamorous Evening"

        # Verify DB persistence directly
        db.expire_all()
        persisted_outlet = db.query(Outlet).filter(Outlet.id == 1).first()
        assert persisted_outlet.seating_capacity == 100
        assert persisted_outlet.dress_code == "Glamorous Evening"

        # Verify AuditLog created
        audit_entry = db.query(AuditLog).filter(
            AuditLog.entity_type == "OUTLET",
            AuditLog.entity_id == 1,
            AuditLog.action == "OUTLET_UPDATED",
        ).first()
        assert audit_entry is not None, "AuditLog entry for OUTLET_UPDATED must exist"
        assert "Rajesh Sharma" in audit_entry.user_name
        print("    [PASS] SuperAdmin successfully updated Outlet 1 and generated AuditLog.")

        # 1B. Manager 1 updates their assigned Outlet (Outlet 1)
        mgr_update = OutletUpdate(closing_time="01:30")
        updated_mgr = update_outlet(outlet_id=1, outlet_in=mgr_update, current_user=manager1, db=db)
        assert updated_mgr.closing_time == "01:30"
        print("    [PASS] Assigned Manager 1 successfully updated Outlet 1.")

        # 1C. Cross-Outlet Tampering: Manager 1 tries to update Outlet 2 (Assigned to Manager 2)
        try:
            update_outlet(
                outlet_id=2,
                outlet_in=OutletUpdate(seating_capacity=40),
                current_user=manager1,
                db=db,
            )
            assert False, "Manager 1 must be rejected from modifying Outlet 2 (HTTP 403 expected)"
        except HTTPException as e:
            assert e.status_code == 403, f"Expected 403, got {e.status_code}"
            assert "Cross-outlet tampering forbidden" in e.detail
            print(f"    [PASS] Cross-outlet tampering blocked with HTTP 403: {e.detail}")

        # 1D. Unauthorized role check: Staff role attempting update
        try:
            auth_checker = require_roles("SUPER_ADMIN", "ADMIN", "MANAGER")
            auth_checker(current_user=staff1)
            assert False, "Staff role must be rejected by require_roles (HTTP 403 expected)"
        except HTTPException as e:
            assert e.status_code == 403
            print("    [PASS] Staff role prohibited from updating outlet (HTTP 403).")

        # 1E. 404 for non-existent outlet
        try:
            update_outlet(
                outlet_id=9999,
                outlet_in=OutletUpdate(seating_capacity=50),
                current_user=superadmin,
                db=db,
            )
            assert False, "Non-existent outlet must return HTTP 404"
        except HTTPException as e:
            assert e.status_code == 404
            assert "Outlet not found" in e.detail
            print("    [PASS] Non-existent outlet returns HTTP 404 correctly.")

        # ----------------------------------------------------------------------
        # 2. RESERVATION LIFECYCLE NOTIFICATION SYSTEM & IDEMPOTENCY
        # ----------------------------------------------------------------------
        print("\n>>> 2. Testing Reservation Notifications & Idempotency Audit Trail...")

        bg = BackgroundTasks()
        res_create = ReservationCreate(
            outlet_id=1,
            guest_name="Karan Malhotra",
            guest_email="karan.malhotra@example.com",
            guest_phone="+919876500001",
            reservation_date="2026-12-10",
            reservation_time="20:00",
            guest_count=4,
            special_requests="Corner table with skyline view",
            environment="DEMO",
        )

        res_obj = create_reservation(req=res_create, background_tasks=bg, db=db)
        assert res_obj.id is not None
        assert res_obj.status == "NEW"
        print(f"    [INFO] Created reservation ID: {res_obj.id}, Reference: {res_obj.reference_id}")

        # Run the queued background tasks
        assert len(bg.tasks) > 0, "Background tasks must have been queued for notification"
        run_background(bg)

        # Check that NotificationLog rows were inserted
        db.expire_all()
        notif_logs = db.query(NotificationLog).filter(
            NotificationLog.entity_type == "RESERVATION",
            NotificationLog.entity_id == res_obj.id,
        ).all()

        assert len(notif_logs) >= 2, f"Expected at least 2 notification logs (Email + SMS), got {len(notif_logs)}"
        email_log = next((l for l in notif_logs if l.channel == "EMAIL"), None)
        sms_log = next((l for l in notif_logs if l.channel == "SMS"), None)

        assert email_log is not None, "Email notification log must exist"
        assert email_log.recipient == "karan.malhotra@example.com"
        assert email_log.status in ("SIMULATED", "SENT")
        assert email_log.event_type == "RESERVATION_NEW"
        assert email_log.idempotency_key is not None

        assert sms_log is not None, "SMS notification log must exist"
        assert sms_log.recipient == "+919876500001"
        assert sms_log.status in ("SIMULATED", "SENT")
        assert sms_log.event_type == "RESERVATION_NEW"
        print(f"    [PASS] Reservation creation dispatched {len(notif_logs)} notification logs with status '{email_log.status}'.")

        # 2B. Test Notification Idempotency (prevent duplicate dispatch for same state)
        initial_log_count = db.query(NotificationLog).count()
        # Trigger same lifecycle notification directly
        notification_service.notify_reservation_lifecycle(
            reservation_id=res_obj.id,
            reference_id=res_obj.reference_id,
            guest_name=res_obj.guest_name,
            guest_email=res_obj.guest_email,
            guest_phone=res_obj.guest_phone,
            outlet_name=res_obj.outlet_name,
            date_str=res_obj.reservation_date,
            time_str=res_obj.reservation_time,
            guest_count=res_obj.guest_count,
            status="NEW",
            environment="DEMO",
        )
        new_log_count = db.query(NotificationLog).count()
        assert new_log_count == initial_log_count, "Idempotent notification dispatch must NOT insert duplicate logs"
        print("    [PASS] Idempotency successfully prevented duplicate notification logs for the same state.")

        # 2C. Reservation Status Update: ACCEPTED
        bg_update = BackgroundTasks()
        updated_res = update_reservation_status(
            res_id=res_obj.id,
            status_update=ReservationStatusUpdate(status="ACCEPTED", special_requests="Confirmed table #14"),
            background_tasks=bg_update,
            current_user=superadmin,
            db=db,
        )
        assert updated_res.status == "ACCEPTED"
        run_background(bg_update)

        db.expire_all()
        accepted_logs = db.query(NotificationLog).filter(
            NotificationLog.entity_type == "RESERVATION",
            NotificationLog.entity_id == res_obj.id,
            NotificationLog.event_type == "RESERVATION_ACCEPTED",
        ).all()
        assert len(accepted_logs) >= 2, "Confirmation notification logs must be recorded for ACCEPTED status"
        print(f"    [PASS] Status update to ACCEPTED dispatched confirmation notifications.")

        # 2D. Reservation Status Update: CANCELLED
        bg_cancel = BackgroundTasks()
        cancelled_res = update_reservation_status(
            res_id=res_obj.id,
            status_update=ReservationStatusUpdate(status="CANCELLED"),
            background_tasks=bg_cancel,
            current_user=superadmin,
            db=db,
        )
        assert cancelled_res.status == "CANCELLED"
        run_background(bg_cancel)

        db.expire_all()
        cancelled_logs = db.query(NotificationLog).filter(
            NotificationLog.entity_type == "RESERVATION",
            NotificationLog.entity_id == res_obj.id,
            NotificationLog.event_type == "RESERVATION_CANCELLED",
        ).all()
        assert len(cancelled_logs) >= 2, "Cancellation notification logs must be recorded for CANCELLED status"
        print(f"    [PASS] Status update to CANCELLED dispatched cancellation notifications.")

        # ----------------------------------------------------------------------
        # 3. LEAD LIFECYCLE NOTIFICATION SYSTEM
        # ----------------------------------------------------------------------
        print("\n>>> 3. Testing Lead Creation Notification & Acknowledgement...")

        bg_lead = BackgroundTasks()
        lead_create = LeadCreate(
            outlet_id=1,
            name="Sneha Kapoor",
            email="sneha.kapoor@example.com",
            phone="+919876543299",
            enquiry_type="PRIVATE_DINING",
            target_date="2026-12-25",
            guest_count=20,
            notes="Annual executive team dinner",
            environment="DEMO",
        )
        lead_obj = create_lead(req=lead_create, background_tasks=bg_lead, db=db)
        assert lead_obj.id is not None
        run_background(bg_lead)

        db.expire_all()
        lead_logs = db.query(NotificationLog).filter(
            NotificationLog.entity_type == "LEAD",
            NotificationLog.entity_id == lead_obj.id,
        ).all()
        assert len(lead_logs) >= 1, "Lead acknowledgement notification log must exist"
        assert lead_logs[0].recipient == "sneha.kapoor@example.com"
        assert lead_logs[0].event_type == "LEAD_CREATED"
        print(f"    [PASS] Lead inquiry acknowledged via notification service with status '{lead_logs[0].status}'.")

        # ----------------------------------------------------------------------
        # 4. NOTIFICATION AUDIT LOGS ENDPOINT & RBAC
        # ----------------------------------------------------------------------
        print("\n>>> 4. Testing Notification Logs Endpoint: GET /api/v1/notifications/logs...")

        # 4A. SuperAdmin fetches all notification logs
        all_logs = list_notification_logs(limit=50, entity_type=None, current_user=superadmin, db=db)
        assert len(all_logs) >= 5, f"Expected at least 5 logs, got {len(all_logs)}"
        assert "entity_type" in all_logs[0]
        assert "channel" in all_logs[0]
        assert "status" in all_logs[0]

        # 4B. Filter by entity_type="RESERVATION"
        res_logs_api = list_notification_logs(limit=50, entity_type="RESERVATION", current_user=manager1, db=db)
        assert all(l["entity_type"] == "RESERVATION" for l in res_logs_api)

        # 4C. Filter by entity_type="LEAD"
        lead_logs_api = list_notification_logs(limit=50, entity_type="LEAD", current_user=superadmin, db=db)
        assert all(l["entity_type"] == "LEAD" for l in lead_logs_api)

        # 4D. Staff role can also view notification logs
        staff_logs = list_notification_logs(limit=10, entity_type=None, current_user=staff1, db=db)
        assert isinstance(staff_logs, list)

        print(f"    [PASS] Notification logs API verified with filtering, pagination and RBAC.")

        print("\n" + "=" * 80)
        print("   ALL PHASE 19 BACKEND TESTS PASSED SUCCESSFULLY! (100%)")
        print("=" * 80)

    finally:
        db.close()
        teardown_db()

if __name__ == "__main__":
    run_phase19_suite()
