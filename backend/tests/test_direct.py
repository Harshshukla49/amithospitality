import os
import sys

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure backend directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException

from app.database import Base
from app.models.user import User
from app.models.audit import EnvironmentSetting
from app.models.outlet import Outlet, MenuItem
from app.models.knowledge import KnowledgeDocument
from app.utils.security import hash_password, create_access_token, decode_token, require_roles
from app.schemas.auth import LoginRequest
from app.schemas.knowledge import EnvironmentSwitchRequest
from app.schemas.reservation import ReservationCreate, ReservationStatusUpdate
from app.schemas.chat import ChatMessageRequest
from app.routers.auth import login, get_me
from app.routers.environment import get_active_environment, switch_environment
from app.routers.outlets import get_menus, create_menu_item
from app.routers.reservations import create_reservation, update_reservation_status, export_reservations_csv
from app.routers.chat import handle_chat_message

TEST_DB_FILE = "./test_direct.db"
if os.path.exists(TEST_DB_FILE):
    try:
        os.remove(TEST_DB_FILE)
    except Exception:
        pass

engine = create_engine(f"sqlite:///{TEST_DB_FILE}", connect_args={"check_same_thread": False})
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def run():
    Base.metadata.create_all(bind=engine)
    db = Session()
    passed = 0
    failed = 0

    print("\n================ AMIT AI CONCIERGE FAST TEST SUITE ================")

    try:
        # Seed test records
        admin = User(
            email="admin@amithospitality.com",
            password_hash=hash_password("AmitConcierge2026!Secure", rounds=4),
            full_name="Vikram Sharma",
            role="SUPER_ADMIN",
            is_active=True,
        )
        staff = User(
            email="staff@amithospitality.com",
            password_hash=hash_password("Staff2026!", rounds=4),
            full_name="Priya Nair",
            role="STAFF",
            is_active=True,
        )
        db.add(admin)
        db.add(staff)

        env = EnvironmentSetting(active_environment="DEMO", updated_by_name="Test")
        db.add(env)

        outlet = Outlet(
            id=1,
            name="Amber Terrace Rooftop",
            slug="amber-terrace",
            outlet_type="Rooftop Lounge",
            cuisine_type="Pan-Asian",
            opening_time="17:30",
            closing_time="01:30",
            dress_code="Smart Casual",
            is_active=True,
        )
        db.add(outlet)

        demo_item = MenuItem(
            outlet_id=1,
            environment="DEMO",
            name="Truffle Dumplings (Demo)",
            price=695.0,
            is_available=True,
        )
        real_item = MenuItem(
            outlet_id=1,
            environment="REAL",
            name="Truffle Dumplings (Real Verified)",
            price=850.0,
            is_available=True,
        )
        db.add(demo_item)
        db.add(real_item)
        db.commit()

        # TEST 1: Auth - Successful Login with Valid Password
        try:
            token_resp = login(LoginRequest(email="admin@amithospitality.com", password="AmitConcierge2026!Secure"), db=db)
            assert token_resp.access_token is not None
            assert token_resp.role == "SUPER_ADMIN"
            payload = decode_token(token_resp.access_token)
            assert payload["sub"] == "admin@amithospitality.com"
            print(" [PASS] 1. test_login_success: JWT created with SUPER_ADMIN role claim")
            passed += 1
        except Exception as e:
            print(f" [FAIL] 1. test_login_success: {e}")
            failed += 1

        # TEST 2: Auth - Invalid Password Rejection (HTTP 401)
        try:
            rejected = False
            try:
                login(LoginRequest(email="admin@amithospitality.com", password="BadPassword!"), db=db)
            except HTTPException as he:
                if he.status_code == 401:
                    rejected = True
            assert rejected, "Invalid password must raise HTTPException 401"
            print(" [PASS] 2. test_login_invalid_password: Bad credentials properly rejected with 401")
            passed += 1
        except Exception as e:
            print(f" [FAIL] 2. test_login_invalid_password: {e}")
            failed += 1

        # TEST 3: RBAC Role-Checker Dependency
        try:
            checker = require_roles("SUPER_ADMIN", "ADMIN")
            # Admin user passes
            assert checker(current_user=admin).role == "SUPER_ADMIN"
            # Staff user is rejected with 403
            staff_rejected = False
            try:
                checker(current_user=staff)
            except HTTPException as he:
                if he.status_code == 403:
                    staff_rejected = True
            assert staff_rejected, "Staff role must be rejected with 403 Forbidden"
            print(" [PASS] 3. test_rbac_enforcement: Role guard properly forbids unauthorized staff (403)")
            passed += 1
        except Exception as e:
            print(f" [FAIL] 3. test_rbac_enforcement: {e}")
            failed += 1

        # TEST 4: Environment Isolation - Default Mode
        try:
            active_info = get_active_environment(db=db)
            assert active_info["environment"] == "DEMO"
            assert active_info["is_demo"] is True
            print(" [PASS] 4. test_active_environment_default: Initial environment is confirmed DEMO")
            passed += 1
        except Exception as e:
            print(f" [FAIL] 4. test_active_environment_default: {e}")
            failed += 1

        # TEST 5: Zero-Contamination Menu Isolation (DEMO query only returns DEMO items)
        try:
            demo_menus = get_menus(outlet_id=1, environment="DEMO", db=db)
            assert any("Demo" in m.name for m in demo_menus)
            assert not any("Real Verified" in m.name for m in demo_menus), "REAL items must NOT leak into DEMO"
            print(" [PASS] 5. test_zero_contamination_demo: Zero leakage confirmed in DEMO queries")
            passed += 1
        except Exception as e:
            print(f" [FAIL] 5. test_zero_contamination_demo: {e}")
            failed += 1

        # TEST 6: Environment Switch & Audit Logging
        try:
            switch_req = EnvironmentSwitchRequest(
                target_environment="REAL",
                reason="Verification transition test",
                confirm_acknowledgment=True,
            )
            switch_res = switch_environment(switch_req, current_user=admin, db=db)
            assert switch_res["active_environment"] == "REAL"
            assert switch_res["previous_environment"] == "DEMO"

            # Check that environment updated in DB
            updated_info = get_active_environment(db=db)
            assert updated_info["environment"] == "REAL"

            # Verify REAL mode query only returns verified items
            real_menus = get_menus(outlet_id=1, environment="REAL", db=db)
            assert any("Real Verified" in m.name for m in real_menus)
            assert not any("Demo" in m.name for m in real_menus), "DEMO items must NOT leak into REAL mode"

            # Revert to DEMO
            switch_environment(
                EnvironmentSwitchRequest(target_environment="DEMO", reason="Reverting", confirm_acknowledgment=True),
                current_user=admin,
                db=db,
            )
            print(" [PASS] 6. test_environment_switch_isolation: Switch to REAL mode works; strict isolation verified")
            passed += 1
        except Exception as e:
            print(f" [FAIL] 6. test_environment_switch_isolation: {e}")
            failed += 1

        # TEST 7: Customer Reservation Creation Workflow
        try:
            booking_req = ReservationCreate(
                outlet_id=1,
                guest_name="Rohan Mehra",
                guest_phone="+91 98200 11223",
                guest_email="rohan@example.com",
                guest_count=4,
                reservation_date="2026-11-12",
                reservation_time="20:00",
                seating_preference="ROOFTOP",
                special_requests="Anniversary dinner",
            )
            res = create_reservation(booking_req, db=db)
            assert res.id is not None
            assert res.status == "NEW"
            assert res.environment == "DEMO"
            assert res.guest_count == 4
            print(f" [PASS] 7. test_create_reservation: Reservation #{res.id} created with status 'NEW'")
            passed += 1
        except Exception as e:
            print(f" [FAIL] 7. test_create_reservation: {e}")
            failed += 1

        # TEST 8: Staff Reservation Status Update & Notes
        try:
            res_id = res.id
            patch_req = ReservationStatusUpdate(status="ACCEPTED", internal_notes="Table 14 allocated by Hostess Priya")
            updated_res = update_reservation_status(res_id, patch_req, current_user=staff, db=db)
            assert updated_res.status == "ACCEPTED"
            assert "Table 14" in updated_res.internal_notes
            print(" [PASS] 8. test_staff_update_reservation: Status updated to 'ACCEPTED' with maître d' notes")
            passed += 1
        except Exception as e:
            print(f" [FAIL] 8. test_staff_update_reservation: {e}")
            failed += 1

        # TEST 9: Grounded Chat Assistant in DEMO Mode
        try:
            chat_req = ChatMessageRequest(
                session_id="session_test_101",
                outlet_id=1,
                message="What is the price of the Truffle Dumplings?",
                language="EN",
            )
            chat_res = handle_chat_message(chat_req, db=db)
            assert "₹695" in chat_res.reply, f"Response should quote dish price: {chat_res.reply}"
            assert chat_res.is_demo is True
            assert chat_res.environment == "DEMO"
            print(" [PASS] 9. test_chat_grounded_response: AI correctly quotes active menu price ₹695 with citations")
            passed += 1
        except Exception as e:
            print(f" [FAIL] 9. test_chat_grounded_response: {e}")
            failed += 1

        # TEST 10: Reservations CSV Export
        try:
            csv_resp = export_reservations_csv(environment="DEMO", current_user=admin, db=db)
            csv_text = csv_resp.body.decode("utf-8")
            assert "Guest Name" in csv_text
            assert "Rohan Mehra" in csv_text
            print(" [PASS] 10. test_export_reservations_csv: Export generated with compliant CSV headers")
            passed += 1
        except Exception as e:
            print(f" [FAIL] 10. test_export_reservations_csv: {e}")
            failed += 1

    finally:
        db.close()
        if os.path.exists(TEST_DB_FILE):
            try:
                os.remove(TEST_DB_FILE)
            except Exception:
                pass

    print("==============================================================")
    print(f"RESULTS: {passed} PASSED | {failed} FAILED (TOTAL {passed + failed})")
    if failed == 0:
        print(" ALL 10 PHASE 2 ACCEPTANCE CRITERIA TESTS PASSED!")
    print("==============================================================\n")
    return failed == 0

if __name__ == "__main__":
    success = run()
    sys.exit(0 if success else 1)
