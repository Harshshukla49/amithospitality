from sqlalchemy.orm import Session
from app.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.outlet import Restaurant, Outlet, MenuCategory, MenuItem
from app.models.knowledge import KnowledgeDocument, KnowledgeChunk, Policy, FAQ
from app.models.reservation import ReservationRequest
from app.models.lead import Lead
from app.models.audit import EnvironmentSetting, AuditLog
from app.models.ai_config import AIConfiguration
from app.utils.security import hash_password
from app.utils.seed_all_brands import seed_all_brands
import json

def seed_database():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # 1. Seed Initial Super Admin
        admin = db.query(User).filter(User.email == "admin@amithospitality.com").first()
        if not admin:
            admin = User(
                email="admin@amithospitality.com",
                password_hash=hash_password("AmitConcierge2026!Secure"),
                full_name="Amit Bajoria",
                role="SUPER_ADMIN",
                is_active=True,
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)

        # 2. Seed Staff and Manager accounts
        manager = db.query(User).filter(User.email == "manager@amithospitality.com").first()
        if not manager:
            manager = User(
                email="manager@amithospitality.com",
                password_hash=hash_password("Manager2026!"),
                full_name="Arjun Kapoor",
                role="MANAGER",
                is_active=True,
            )
            db.add(manager)

        staff = db.query(User).filter(User.email == "staff@amithospitality.com").first()
        if not staff:
            staff = User(
                email="staff@amithospitality.com",
                password_hash=hash_password("Staff2026!"),
                full_name="Priya Nair",
                role="STAFF",
                is_active=True,
            )
            db.add(staff)
        db.commit()

        # 3. Seed Environment Setting
        env_setting = db.query(EnvironmentSetting).first()
        if not env_setting:
            env_setting = EnvironmentSetting(
                active_environment="DEMO",
                updated_by_name="System Initializer",
                switch_reason="Initial platform bootstrap in DEMO mode.",
            )
            db.add(env_setting)
            db.commit()

        # 4. Seed Corporate Restaurant (Amit Hospitality LLP)
        restaurant = db.query(Restaurant).first()
        if not restaurant:
            restaurant = Restaurant(
                name="Amit Hospitality LLP",
                slug="amit-hospitality",
                description="Kolkata's premier hospitality group curating world-class culinary, nightlife, and boutique retail destinations.",
                address="401 Kamalalaya Centre, 156A Lenin Sarani",
                city="Kolkata",
                phone="+91 94323 35967",
                email="vanita@amithospitality.com",
            )
            db.add(restaurant)
            db.commit()
            db.refresh(restaurant)
        else:
            restaurant.name = "Amit Hospitality LLP"
            restaurant.slug = "amit-hospitality"
            restaurant.description = "Kolkata's premier hospitality group curating world-class culinary, nightlife, and boutique retail destinations."
            restaurant.address = "401 Kamalalaya Centre, 156A Lenin Sarani"
            restaurant.city = "Kolkata"
            restaurant.phone = "+91 94323 35967"
            restaurant.email = "vanita@amithospitality.com"
            db.commit()

        # 5. Authoritatively seed all 4 authentic brands (LOTD, Veneto, Warehouse Cafe, Deliite)
        seed_all_brands(db)

        # 6. Seed Sample DEMO Reservations
        if db.query(ReservationRequest).count() == 0:
            db.add(
                ReservationRequest(
                    environment="DEMO",
                    outlet_id=8,
                    outlet_name="Lord of the Drinks",
                    guest_name="Vikramaditya Singhania",
                    guest_phone="+91 98201 44521",
                    guest_email="v.singhania@apexcapital.in",
                    guest_count=4,
                    reservation_date="2026-11-20",
                    reservation_time="20:30",
                    seating_preference="INDOOR",
                    special_requests="Wedding anniversary celebration. Preferred table near Ghost Bar.",
                    status="ACCEPTED",
                    internal_notes="Complimentary dessert platter approved by GM.",
                )
            )
            db.add(
                ReservationRequest(
                    environment="DEMO",
                    outlet_id=9,
                    outlet_name="Veneto Kitchen and Bar",
                    guest_name="Ananya Deshmukh",
                    guest_phone="+91 98112 33419",
                    guest_email="ananya.d@designstudio.com",
                    guest_count=6,
                    reservation_date="2026-11-21",
                    reservation_time="19:45",
                    seating_preference="INDOOR",
                    special_requests="Two guests require vegetarian wood-fired pizza and truffle pasta.",
                    status="PENDING",
                    internal_notes="Awaiting confirmation of central booth availability.",
                )
            )
            db.commit()

        # 7. Seed Sample DEMO Leads
        if db.query(Lead).count() == 0:
            db.add(
                Lead(
                    environment="DEMO",
                    outlet_id=8,
                    outlet_name="Lord of the Drinks",
                    name="Rajesh Mehta",
                    phone="+91 98220 11990",
                    email="rajesh@mehtaluxury.com",
                    enquiry_type="CORPORATE_EVENT",
                    guest_count=45,
                    target_date="2026-12-15",
                    budget_range="₹3,50,000 - ₹5,00,000",
                    status="QUALIFIED",
                    notes="Annual leadership dinner. Customized cocktail menu and AV setup.",
                )
            )
            db.commit()

        # 8. Seed Initial Audit Log
        if db.query(AuditLog).count() == 0:
            db.add(
                AuditLog(
                    user_name="Amit Bajoria",
                    user_role="SUPER_ADMIN",
                    action="SYSTEM_BOOTSTRAP",
                    entity_type="SYSTEM",
                    environment="DEMO",
                    details="Initialized database with authentic Amit Hospitality LLP brands and verified Kolkata destinations.",
                )
            )
            db.commit()

        # 9. Seed AI Configuration
        if db.query(AIConfiguration).count() == 0:
            db.add(
                AIConfiguration(
                    environment="DEMO",
                    model_name="gemini-1.5-flash",
                    temperature=0.2,
                    top_k_retrievals=4,
                    system_prompt="You are Amit Hospitality's luxury AI Concierge. Answer questions using only retrieved active environment knowledge.",
                )
            )
            db.commit()

        print("[OK] Database seeded successfully with authentic Amit Hospitality LLP brands.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
