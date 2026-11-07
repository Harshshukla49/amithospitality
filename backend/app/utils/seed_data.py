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
                full_name="Vikram Sharma",
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

        # 4. Seed Restaurant & Outlets
        restaurant = db.query(Restaurant).first()
        if not restaurant:
            restaurant = Restaurant(
                name="Amit Hospitality Group",
                slug="amit-hospitality",
                description="Prestigious portfolio of destination dining venues and cocktail lounges.",
                address="14 MG Road & Amit Heritage Plaza",
                city="New Delhi",
                phone="+91 11 4050 9900",
                email="concierge@amithospitality.com",
            )
            db.add(restaurant)
            db.commit()
            db.refresh(restaurant)

        outlets_data = [
            {
                "id": 1,
                "name": "Amber Terrace Rooftop",
                "slug": "amber-terrace",
                "outlet_type": "Rooftop Lounge & Fine Dining",
                "cuisine_type": "Modern Pan-Asian & Global Small Plates",
                "opening_time": "17:30",
                "closing_time": "01:30",
                "dress_code": "Smart Casual (Collared shirts, tailored trousers/dresses)",
                "seating_capacity": 120,
                "location": "14th Floor, Skyline Tower, MG Road",
                "description": "Elevated al fresco dining with panoramic city skyline views, bespoke mixology, and progressive Asian gastronomy.",
                "is_popular": True,
            },
            {
                "id": 2,
                "name": "Saffron & Silk",
                "slug": "saffron-and-silk",
                "outlet_type": "Fine Dining Restaurant",
                "cuisine_type": "Contemporary Royal Indian & Awadhi",
                "opening_time": "12:30",
                "closing_time": "23:30",
                "dress_code": "Formal / Elegant Evening Attire",
                "seating_capacity": 85,
                "location": "Lobby Level, Amit Heritage Plaza",
                "description": "An ode to imperial Indian banquets featuring slow-cooked dum preparations and rare spices.",
                "is_popular": True,
            },
            {
                "id": 3,
                "name": "The Velvet Cellar",
                "slug": "the-velvet-cellar",
                "outlet_type": "Speakeasy & Cocktail Lounge",
                "cuisine_type": "Artisanal Tapas & Charcuterie",
                "opening_time": "18:00",
                "closing_time": "02:00",
                "dress_code": "Chic Lounge Wear",
                "seating_capacity": 60,
                "location": "Sub-level 1, Amit Heritage Plaza",
                "description": "An intimate subterranean sanctuary dedicated to rare single malts, botanical infusions, and live jazz.",
                "is_popular": False,
            },
        ]

        for od in outlets_data:
            existing = db.query(Outlet).filter(Outlet.id == od["id"]).first()
            if not existing:
                outlet = Outlet(
                    id=od["id"],
                    restaurant_id=restaurant.id,
                    name=od["name"],
                    slug=od["slug"],
                    outlet_type=od["outlet_type"],
                    cuisine_type=od["cuisine_type"],
                    opening_time=od["opening_time"],
                    closing_time=od["closing_time"],
                    dress_code=od["dress_code"],
                    seating_capacity=od["seating_capacity"],
                    location=od["location"],
                    description=od["description"],
                    is_popular=od["is_popular"],
                )
                db.add(outlet)
        db.commit()

        # 5. Seed DEMO Menu Items
        menu_items_data = [
            # Amber Terrace (Outlet 1)
            {
                "outlet_id": 1,
                "name": "Truffle Edamame & Wild Mushroom Dumplings",
                "description": "Steamed crystal dumplings infused with black truffle oil and aged chili ponzu.",
                "price": 695.0,
                "dietary_flags": "VEGAN,VEG",
                "is_signature": True,
            },
            {
                "outlet_id": 1,
                "name": "Glazed Chilean Sea Bass Skewers",
                "description": "Miso-mirin marinated sea bass grilled over binchotan charcoal with pickled ginger blossom.",
                "price": 1250.0,
                "dietary_flags": "NON_VEG,GLUTEN_FREE",
                "is_signature": True,
            },
            {
                "outlet_id": 1,
                "name": "Robata Smoked King Oyster Mushrooms",
                "description": "Sweet soy tare glaze, crispy garlic chips, sesame nori powder, and steamed jasmine rice.",
                "price": 850.0,
                "dietary_flags": "VEG,VEGAN",
                "is_signature": False,
            },
            {
                "outlet_id": 1,
                "name": "The Amber Horizon Cocktail",
                "description": "Smoked Japanese whisky, yuzu liqueur, saffron-infused honey, and gold leaf ice cube.",
                "price": 895.0,
                "dietary_flags": "VEG",
                "is_signature": True,
            },
            # Saffron & Silk (Outlet 2)
            {
                "outlet_id": 2,
                "name": "Subz Nadru Ki Shammi",
                "description": "Pan-seared Kashmiri lotus stem patties stuffed with smoked plum and toasted pine nuts.",
                "price": 650.0,
                "dietary_flags": "VEG,JAIN,GLUTEN_FREE",
                "is_signature": True,
            },
            {
                "outlet_id": 2,
                "name": "Galouti Kebab Royale",
                "description": "Mouth-melting smoked lamb patties flavored with 24 Awadhi spices, served on saffron sheermal.",
                "price": 950.0,
                "dietary_flags": "NON_VEG",
                "is_signature": True,
            },
            {
                "outlet_id": 2,
                "name": "Dal Saffron & Silk (36-Hour Simmered)",
                "description": "Slow-cooked black lentils simmered overnight over glowing embers with cultured butter.",
                "price": 595.0,
                "dietary_flags": "VEG,GLUTEN_FREE",
                "is_signature": True,
            },
            {
                "outlet_id": 2,
                "name": "Nalli Nihari Khas",
                "description": "Braised lamb shanks in an aromatic spiced stock reduction scented with rose petals.",
                "price": 1150.0,
                "dietary_flags": "NON_VEG",
                "is_signature": True,
            },
            # The Velvet Cellar (Outlet 3)
            {
                "outlet_id": 3,
                "name": "Artisanal Truffle Burrata Bowl",
                "description": "Heirloom tomatoes, basil emulsion, aged balsamic glaze, and grilled sourdough wafers.",
                "price": 795.0,
                "dietary_flags": "VEG",
                "is_signature": True,
            },
            {
                "outlet_id": 3,
                "name": "Old Fashioned 1928 Cocktail",
                "description": "Small-batch bourbon, demerara sugar syrup, aromatic bitters, and hickory wood smoke.",
                "price": 925.0,
                "dietary_flags": "VEG",
                "is_signature": True,
            },
        ]

        for mi in menu_items_data:
            existing_mi = (
                db.query(MenuItem)
                .filter(MenuItem.name == mi["name"], MenuItem.environment == "DEMO")
                .first()
            )
            if not existing_mi:
                item = MenuItem(
                    outlet_id=mi["outlet_id"],
                    environment="DEMO",
                    name=mi["name"],
                    description=mi["description"],
                    price=mi["price"],
                    currency="INR",
                    dietary_flags=mi["dietary_flags"],
                    is_available=True,
                    is_signature=mi["is_signature"],
                )
                db.add(item)
        db.commit()

        # 6. Seed Sample DEMO Knowledge Documents
        sample_docs = [
            {
                "title": "Amber Terrace Operating Timings & Valet Guide (Sample)",
                "file_name": "amber_terrace_policies_sample.pdf",
                "file_type": "PDF",
                "outlet_id": 1,
                "category": "TIMING",
                "chunk_count": 8,
            },
            {
                "title": "Saffron & Silk Royal Banquet & Menu Roster (Sample)",
                "file_name": "saffron_silk_menu_sample.xlsx",
                "file_type": "XLSX",
                "outlet_id": 2,
                "category": "MENU",
                "chunk_count": 16,
            },
            {
                "title": "The Velvet Cellar Dress Code & Weekend Policies (Sample)",
                "file_name": "velvet_cellar_policy_sample.docx",
                "file_type": "DOCX",
                "outlet_id": 3,
                "category": "POLICY",
                "chunk_count": 6,
            },
        ]

        for sd in sample_docs:
            existing_doc = (
                db.query(KnowledgeDocument)
                .filter(KnowledgeDocument.file_name == sd["file_name"], KnowledgeDocument.environment == "DEMO")
                .first()
            )
            if not existing_doc:
                kdoc = KnowledgeDocument(
                    environment="DEMO",
                    outlet_id=sd["outlet_id"],
                    title=sd["title"],
                    file_name=sd["file_name"],
                    file_type=sd["file_type"],
                    category=sd["category"],
                    verification_status="UNVERIFIED",
                    chunk_count=sd["chunk_count"],
                    is_active=True,
                )
                db.add(kdoc)
        db.commit()

        # 7. Seed Sample DEMO Reservations
        if db.query(ReservationRequest).count() == 0:
            db.add(
                ReservationRequest(
                    environment="DEMO",
                    outlet_id=1,
                    outlet_name="Amber Terrace Rooftop",
                    guest_name="Vikramaditya Singhania",
                    guest_phone="+91 98201 44521",
                    guest_email="v.singhania@apexcapital.in",
                    guest_count=4,
                    reservation_date="2026-11-08",
                    reservation_time="20:30",
                    seating_preference="ROOFTOP",
                    special_requests="Wedding anniversary celebration. Corner skyline table requested.",
                    status="ACCEPTED",
                    internal_notes="Complimentary champagne toast approved by F&B Manager.",
                )
            )
            db.add(
                ReservationRequest(
                    environment="DEMO",
                    outlet_id=2,
                    outlet_name="Saffron & Silk",
                    guest_name="Ananya Deshmukh",
                    guest_phone="+91 98112 33419",
                    guest_email="ananya.d@designstudio.com",
                    guest_count=6,
                    reservation_date="2026-11-09",
                    reservation_time="19:45",
                    seating_preference="PRIVATE",
                    special_requests="Two guests require strictly Jain meals.",
                    status="PENDING",
                    internal_notes="Awaiting confirmation of private dining room.",
                )
            )
            db.commit()

        # 8. Seed Sample DEMO Leads
        if db.query(Lead).count() == 0:
            db.add(
                Lead(
                    environment="DEMO",
                    outlet_id=1,
                    outlet_name="Amber Terrace Rooftop",
                    name="Rajesh Mehta",
                    phone="+91 98220 11990",
                    email="rajesh@mehtaluxury.com",
                    enquiry_type="CORPORATE_EVENT",
                    guest_count=45,
                    target_date="2026-12-15",
                    budget_range="₹3,50,000 - ₹5,00,000",
                    status="QUALIFIED",
                    notes="Annual leadership dinner. Customized 5-course tasting menu.",
                )
            )
            db.commit()

        # 9. Seed Initial Audit Log
        if db.query(AuditLog).count() == 0:
            db.add(
                AuditLog(
                    user_name="Vikram Sharma",
                    user_role="SUPER_ADMIN",
                    action="SYSTEM_BOOTSTRAP",
                    entity_type="SYSTEM",
                    environment="DEMO",
                    details="Initialized database with DEMO data environment and Super Admin credentials.",
                )
            )
            db.commit()

        # 10. Seed AI Configuration
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

        print("[OK] Database seeded successfully with initial Super Admin and DEMO environment records.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
