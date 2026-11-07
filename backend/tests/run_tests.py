import asyncio
import httpx
import os
import sys
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import Base, get_db
from app.main import app
from app.models.user import User
from app.models.audit import EnvironmentSetting
from app.models.outlet import Outlet, MenuItem
from app.models.knowledge import KnowledgeDocument
from app.utils.security import hash_password, create_access_token

TEST_DB_FILE = "./test_run.db"
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_FILE}"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

def init_test_data():
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except Exception:
            pass

    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()

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

    demo_doc = KnowledgeDocument(
        environment="DEMO",
        outlet_id=1,
        title="Sample Menu PDF",
        file_name="sample.pdf",
        file_type="PDF",
        verification_status="UNVERIFIED",
    )
    real_doc = KnowledgeDocument(
        environment="REAL",
        outlet_id=1,
        title="Verified Operating Policies",
        file_name="verified_policies.pdf",
        file_type="PDF",
        verification_status="VERIFIED",
    )
    db.add(demo_doc)
    db.add(real_doc)

    db.commit()
    db.close()

async def run_all_tests():
    init_test_data()
    transport = httpx.ASGITransport(app=app)
    passed = 0
    failed = 0

    admin_token = create_access_token({"sub": "admin@amithospitality.com", "role": "SUPER_ADMIN"})
    staff_token = create_access_token({"sub": "staff@amithospitality.com", "role": "STAFF"})

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        print("\n================ AMIT AI CONCIERGE TEST SUITE ================")

        # Test 1: Login Success
        try:
            res = await client.post(
                "/api/v1/auth/login",
                json={"email": "admin@amithospitality.com", "password": "AmitConcierge2026!Secure"},
            )
            assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
            data = res.json()
            assert data["role"] == "SUPER_ADMIN"
            assert "access_token" in data
            print(" [PASS] test_login_success (JWT generated, role: SUPER_ADMIN)")
            passed += 1
        except Exception as e:
            print(f" [FAIL] test_login_success: {e}")
            failed += 1

        # Test 2: Login Invalid Password
        try:
            res = await client.post(
                "/api/v1/auth/login",
                json={"email": "admin@amithospitality.com", "password": "WrongPassword!"},
            )
            assert res.status_code == 401, f"Expected 401, got {res.status_code}"
            print(" [PASS] test_login_invalid_password (Properly rejected with 401)")
            passed += 1
        except Exception as e:
            print(f" [FAIL] test_login_invalid_password: {e}")
            failed += 1

        # Test 3: Get Current User Profile
        try:
            res = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
            assert res.status_code == 200
            assert res.json()["email"] == "admin@amithospitality.com"
            print(" [PASS] test_get_current_user_me (Authenticated user profile returned)")
            passed += 1
        except Exception as e:
            print(f" [FAIL] test_get_current_user_me: {e}")
            failed += 1

        # Test 4: RBAC Enforcement
        try:
            staff_res = await client.get("/api/v1/auth/users", headers={"Authorization": f"Bearer {staff_token}"})
            assert staff_res.status_code == 403, "Staff should be forbidden from listing all users"

            admin_res = await client.get("/api/v1/auth/users", headers={"Authorization": f"Bearer {admin_token}"})
            assert admin_res.status_code == 200
            assert len(admin_res.json()) >= 2
            print(" [PASS] test_rbac_user_management (Staff forbidden 403, Super Admin allowed 200)")
            passed += 1
        except Exception as e:
            print(f" [FAIL] test_rbac_user_management: {e}")
            failed += 1

        # Test 5: Default Active Environment is DEMO
        try:
            res = await client.get("/api/v1/environment/active")
            assert res.status_code == 200
            data = res.json()
            assert data["environment"] == "DEMO"
            assert data["is_demo"] is True
            print(" [PASS] test_active_environment_default (System initializes in DEMO mode)")
            passed += 1
        except Exception as e:
            print(f" [FAIL] test_active_environment_default: {e}")
            failed += 1

        # Test 6: Zero Knowledge Contamination in DEMO Mode
        try:
            res = await client.get("/api/v1/menus?outlet_id=1&environment=DEMO")
            assert res.status_code == 200
            items = res.json()
            assert any("Demo" in i["name"] for i in items), "Demo items must be returned"
            assert not any("Real Verified" in i["name"] for i in items), "REAL items must NOT leak into DEMO query"
            print(" [PASS] test_menu_environment_isolation_demo (Zero leakage: DEMO queries only return DEMO items)")
            passed += 1
        except Exception as e:
            print(f" [FAIL] test_menu_environment_isolation_demo: {e}")
            failed += 1

        # Test 7: Environment Switch RBAC & State Transition
        try:
            staff_switch = await client.post(
                "/api/v1/environment/switch",
                headers={"Authorization": f"Bearer {staff_token}"},
                json={"target_environment": "REAL", "reason": "Unauthorized", "confirm_acknowledgment": True},
            )
            assert staff_switch.status_code == 403, "Staff cannot switch environment"

            admin_switch = await client.post(
                "/api/v1/environment/switch",
                headers={"Authorization": f"Bearer {admin_token}"},
                json={"target_environment": "REAL", "reason": "Authorized switch to verified mode", "confirm_acknowledgment": True},
            )
            assert admin_switch.status_code == 200
            assert admin_switch.json()["active_environment"] == "REAL"

            check_env = await client.get("/api/v1/environment/active")
            assert check_env.json()["environment"] == "REAL"
            assert check_env.json()["is_demo"] is False

            # Verify REAL mode only returns verified items
            real_menus = await client.get("/api/v1/menus?outlet_id=1&environment=REAL")
            real_items = real_menus.json()
            assert any("Real Verified" in i["name"] for i in real_items)
            assert not any("Demo" in i["name"] for i in real_items)

            # Revert back to DEMO
            await client.post(
                "/api/v1/environment/switch",
                headers={"Authorization": f"Bearer {admin_token}"},
                json={"target_environment": "DEMO", "reason": "Revert to demo for tests", "confirm_acknowledgment": True},
            )
            print(" [PASS] test_environment_switch_rbac (Staff blocked 403, Admin switched, isolation verified)")
            passed += 1
        except Exception as e:
            print(f" [FAIL] test_environment_switch_rbac: {e}")
            failed += 1

        # Test 8: Reservation Request Submission
        try:
            res = await client.post(
                "/api/v1/reservations",
                json={
                    "outlet_id": 1,
                    "guest_name": "Rohan Mehra",
                    "guest_phone": "+91 98200 11223",
                    "guest_email": "rohan@example.com",
                    "guest_count": 4,
                    "reservation_date": "2026-11-12",
                    "reservation_time": "20:00",
                    "seating_preference": "ROOFTOP",
                    "special_requests": "Anniversary celebration",
                },
            )
            assert res.status_code == 200
            data = res.json()
            assert data["guest_name"] == "Rohan Mehra"
            assert data["status"] == "NEW"
            assert data["environment"] == "DEMO"
            print(" [PASS] test_create_reservation_request (Guest request logged as NEW)")
            passed += 1
        except Exception as e:
            print(f" [FAIL] test_create_reservation_request: {e}")
            failed += 1

        # Test 9: Staff Update Reservation Status & Notes
        try:
            create_res = await client.post(
                "/api/v1/reservations",
                json={
                    "outlet_id": 1,
                    "guest_name": "Meera Kapoor",
                    "guest_phone": "+91 98111 22334",
                    "guest_count": 2,
                    "reservation_date": "2026-11-15",
                    "reservation_time": "19:30",
                    "seating_preference": "INDOOR",
                },
            )
            res_id = create_res.json()["id"]

            patch_res = await client.patch(
                f"/api/v1/reservations/{res_id}/status",
                headers={"Authorization": f"Bearer {staff_token}"},
                json={"status": "ACCEPTED", "internal_notes": "Table 14 allocated by Hostess Priya"},
            )
            assert patch_res.status_code == 200
            data = patch_res.json()
            assert data["status"] == "ACCEPTED"
            assert "Table 14" in data["internal_notes"]
            print(" [PASS] test_staff_update_reservation_status (Maître d' allocation status updated)")
            passed += 1
        except Exception as e:
            print(f" [FAIL] test_staff_update_reservation_status: {e}")
            failed += 1

        # Test 10: Export Reservations CSV
        try:
            res = await client.get("/api/v1/reservations/export", headers={"Authorization": f"Bearer {admin_token}"})
            assert res.status_code == 200
            assert "text/csv" in res.headers["content-type"]
            assert "Guest Name" in res.text
            print(" [PASS] test_export_reservations_csv (CSV exported with correct headers)")
            passed += 1
        except Exception as e:
            print(f" [FAIL] test_export_reservations_csv: {e}")
            failed += 1

        print("==============================================================")
        print(f"TOTAL: {passed + failed} | PASSED: {passed} | FAILED: {failed}")
        if failed == 0:
            print(" ALL TESTS PASSED! PHASE 2 ACCEPTANCE CRITERIA VERIFIED.")
        print("==============================================================\n")

    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except Exception:
            pass

    return failed == 0

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
