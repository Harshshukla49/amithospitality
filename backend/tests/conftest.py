import pytest
import pytest_asyncio
import httpx
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models.user import User
from app.models.audit import EnvironmentSetting
from app.models.outlet import Restaurant, Outlet, MenuItem
from app.models.knowledge import KnowledgeDocument
from app.utils.security import hash_password, create_access_token

TEST_DB_FILE = "./test_concierge.db"
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_FILE}"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except Exception:
            pass

    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    admin = User(
        email="admin@amithospitality.com",
        password_hash=hash_password("AmitConcierge2026!Secure"),
        full_name="Vikram Sharma",
        role="SUPER_ADMIN",
        is_active=True,
    )
    staff = User(
        email="staff@amithospitality.com",
        password_hash=hash_password("Staff2026!"),
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

    yield

    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except Exception:
            pass

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixture
async def client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def admin_token():
    return create_access_token({"sub": "admin@amithospitality.com", "role": "SUPER_ADMIN"})

@pytest.fixture
def staff_token():
    return create_access_token({"sub": "staff@amithospitality.com", "role": "STAFF"})
