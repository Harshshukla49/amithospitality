"""
Lord of the Drinks (LOTD) Kolkata — Authoritative Seeding Script
Enterprise Hospitality Intelligence Platform — Amit Hospitality Group

This script seeds the authoritative data for Lord of the Drinks (South City Mall, Kolkata):
1. Outlet Record (ID, name, slug, timings, seating, location, ambiance).
2. Menu Categories & Signature Menu Items (Cocktails, Dimsums, Kebabs, Mains, Desserts) for DEMO and REAL modes.
3. Grounded RAG Knowledge Documents & Vector Chunks (256-dim embeddings) for Zero-Hallucination AI Concierge.
4. Venue Policies (Cancellation, Dress Code, Age Policy, Valet).
5. Grounded Frequently Asked Questions (FAQs).

Reference: https://amithospitality.com/lordofrings.php
Operator: Amit Hospitality LLP (Amit & Vanita Bajoria)
"""

import sys
import os
import json
import logging

# Ensure backend root is on sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from sqlalchemy.orm import Session
from app.database import Base, engine, SessionLocal
from app.models.outlet import Restaurant, Outlet, MenuCategory, MenuItem
from app.models.knowledge import KnowledgeDocument, KnowledgeChunk, Policy, FAQ
from app.models.audit import AuditLog, EnvironmentSetting
from app.services.embedding_service import generate_embedding

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

LOTD_OUTLET_DATA = {
    "name": "Lord of the Drinks",
    "slug": "lord-of-the-drinks",
    "outlet_type": "Lounge, Bar & Experiential Dining",
    "cuisine_type": "Continental, Modern North Indian, Pan-Asian & Cocktails",
    "opening_time": "12:00",
    "closing_time": "00:00",
    "dress_code": "Smart Casual (Collared shirts, tailored attire; no flip-flops or athletic wear after 7 PM)",
    "seating_capacity": 220,
    "location": "4th Floor, South City Mall, 375 Prince Anwar Shah Road, Jadavpur, Kolkata - 700068",
    "description": (
        "Kolkata's tallest bar and premier experiential nightlife destination, featuring medieval European "
        "castle decor, signature Ghost Bar, neon-lit lounge, and progressive mixology by Amit Hospitality."
    ),
    "is_popular": True,
    "is_active": True,
}

LOTD_CATEGORIES = [
    {"name": "Signature Cocktails & Spirits", "display_order": 1, "description": "Crafted mixology, single malts, and signature Ghost Bar cocktails"},
    {"name": "Artisanal Dimsums & Tapas", "display_order": 2, "description": "Steamed crystal dumplings, progressive Asian small plates, and global tapas"},
    {"name": "Tandoori & Kebabs", "display_order": 3, "description": "Clay-oven smoked kebabs, regional kasundi tikkas, and Awadhi grills"},
    {"name": "Continental & Pan-Asian Mains", "display_order": 4, "description": "Wood-fired sourdough pizzas, slow-simmered curries, and wok specialties"},
    {"name": "Decadent Desserts", "display_order": 5, "description": "Artisanal confectioneries and contemporary fusion dessert creations"},
]

LOTD_MENU_ITEMS = [
    # Cocktails & Spirits
    {
        "category_name": "Signature Cocktails & Spirits",
        "name": "My 18th Birthday",
        "description": "Signature LOTD concoction with premium vodka, rich butterscotch liqueur, salted caramel, popcorn syrup, and fresh pineapple juice.",
        "price": 675.0,
        "currency": "INR",
        "dietary_flags": "VEG",
        "is_signature": True,
        "display_order": 1,
    },
    {
        "category_name": "Signature Cocktails & Spirits",
        "name": "Lavender Sour",
        "description": "Botanical dry gin, organic lavender blossom tincture, butterfly pea flower tea, fresh lime, and vegan aquafaba foam.",
        "price": 695.0,
        "currency": "INR",
        "dietary_flags": "VEG",
        "is_signature": True,
        "display_order": 2,
    },
    {
        "category_name": "Signature Cocktails & Spirits",
        "name": "Smoked Rosemary Negroni",
        "description": "Campari, sweet vermouth, London dry gin, infused with torched wild rosemary smoke in a vintage glass bell.",
        "price": 725.0,
        "currency": "INR",
        "dietary_flags": "VEG",
        "is_signature": True,
        "display_order": 3,
    },
    {
        "category_name": "Signature Cocktails & Spirits",
        "name": "Kolkata Spiced Mule",
        "description": "Triple-distilled vodka, regional Gondhoraj lime reduction, spicy house-brewed ginger beer, and fresh garden mint.",
        "price": 645.0,
        "currency": "INR",
        "dietary_flags": "VEG",
        "is_signature": True,
        "display_order": 4,
    },
    # Artisanal Dimsums & Tapas
    {
        "category_name": "Artisanal Dimsums & Tapas",
        "name": "Mustard Crusted Bhetki Tikka",
        "description": "Fresh Bengal bhetki fillets marinated in stone-ground Kasundi mustard and yellow chili, clay-oven roasted to perfection.",
        "price": 795.0,
        "currency": "INR",
        "dietary_flags": "NON_VEG",
        "is_signature": True,
        "display_order": 5,
    },
    {
        "category_name": "Artisanal Dimsums & Tapas",
        "name": "Truffle & Edamame Crystal Dimsums",
        "description": "Hand-rolled translucent dumplings filled with crushed edamame, water chestnuts, and fragrant white truffle essence.",
        "price": 595.0,
        "currency": "INR",
        "dietary_flags": "VEGAN,VEG",
        "is_signature": True,
        "display_order": 6,
    },
    {
        "category_name": "Artisanal Dimsums & Tapas",
        "name": "Ghost Bar Crispy Calamari",
        "description": "Tender golden calamari rings tossed with charred scallions, crushed black pepper, and citrus sriracha aioli.",
        "price": 685.0,
        "currency": "INR",
        "dietary_flags": "NON_VEG",
        "is_signature": False,
        "display_order": 7,
    },
    {
        "category_name": "Artisanal Dimsums & Tapas",
        "name": "Ghost Bar Nachos Grande",
        "description": "Crisp artisanal corn tortillas layered with molten cheddar queso, refried pinto beans, jalapenos, and fresh guacamole.",
        "price": 495.0,
        "currency": "INR",
        "dietary_flags": "VEG",
        "is_signature": False,
        "display_order": 8,
    },
    # Tandoori & Kebabs
    {
        "category_name": "Tandoori & Kebabs",
        "name": "Paneer Khas Tikka",
        "description": "Tender cottage cheese stuffed with sun-dried tomato tapenade, hung curd marinade, and smoked paprika.",
        "price": 545.0,
        "currency": "INR",
        "dietary_flags": "VEG,JAIN",
        "is_signature": False,
        "display_order": 9,
    },
    {
        "category_name": "Tandoori & Kebabs",
        "name": "Bhatti Murgh Kebab",
        "description": "Succulent chicken thighs char-grilled with crushed roasted spices, malt vinegar, and smoked ginger.",
        "price": 695.0,
        "currency": "INR",
        "dietary_flags": "NON_VEG",
        "is_signature": False,
        "display_order": 10,
    },
    {
        "category_name": "Tandoori & Kebabs",
        "name": "Gilafi Lamb Seekh Kebab",
        "description": "Minced prime lamb skewers coated with bell peppers, mint, and royal Awadhi spices.",
        "price": 775.0,
        "currency": "INR",
        "dietary_flags": "NON_VEG",
        "is_signature": True,
        "display_order": 11,
    },
    # Continental & Pan-Asian Mains
    {
        "category_name": "Continental & Pan-Asian Mains",
        "name": "Slow-Cooked Dal Makhani with Truffle Butter",
        "description": "Black lentils slow-cooked for 24 hours over glowing coals, finished with hand-churned truffle butter and cream.",
        "price": 525.0,
        "currency": "INR",
        "dietary_flags": "VEG",
        "is_signature": True,
        "display_order": 12,
    },
    {
        "category_name": "Continental & Pan-Asian Mains",
        "name": "Kolkata Spiced Lamb Rogan Josh",
        "description": "Slow-braised lamb shanks simmered in caramelized onions, saffron, and Kashmiri spices, served with saffron butter naan.",
        "price": 825.0,
        "currency": "INR",
        "dietary_flags": "NON_VEG",
        "is_signature": True,
        "display_order": 13,
    },
    {
        "category_name": "Continental & Pan-Asian Mains",
        "name": "Wild Mushroom & Truffle Oil Wood-Fired Pizza",
        "description": "Hand-stretched Neapolitan crust topped with roasted porcini, shiitake, fior di latte mozzarella, and white truffle oil.",
        "price": 695.0,
        "currency": "INR",
        "dietary_flags": "VEG",
        "is_signature": False,
        "display_order": 14,
    },
    {
        "category_name": "Continental & Pan-Asian Mains",
        "name": "Pan-Seared Norwegian Salmon",
        "description": "Crispy skin Atlantic salmon over creamy saffron risotto, charred asparagus, and lemon dill velouté.",
        "price": 1195.0,
        "currency": "INR",
        "dietary_flags": "NON_VEG",
        "is_signature": True,
        "display_order": 15,
    },
    {
        "category_name": "Continental & Pan-Asian Mains",
        "name": "Wok-Tossed Hakka Chili Chicken",
        "description": "Classic Kolkata-style wok-charred chicken with green chilies, dark soy, spring onion, and crispy garlic.",
        "price": 625.0,
        "currency": "INR",
        "dietary_flags": "NON_VEG",
        "is_signature": False,
        "display_order": 16,
    },
    # Decadent Desserts
    {
        "category_name": "Decadent Desserts",
        "name": "Classic Dark Chocolate Sphere",
        "description": "Belgian dark chocolate dome with hazelnut praline mousse, poured over with steaming salted caramel ganache.",
        "price": 475.0,
        "currency": "INR",
        "dietary_flags": "VEG",
        "is_signature": True,
        "display_order": 17,
    },
    {
        "category_name": "Decadent Desserts",
        "name": "Baked Gulab Jamun Cheesecake",
        "description": "Signature fusion dessert featuring warm baby gulab jamuns baked inside saffron-cardamom cream cheese on speculoos crust.",
        "price": 425.0,
        "currency": "INR",
        "dietary_flags": "VEG",
        "is_signature": False,
        "display_order": 18,
    },
]

LOTD_KNOWLEDGE_DOCS = [
    {
        "title": "Lord of the Drinks Kolkata — Venue Operations, Entry & Reservation Guide",
        "file_name": "lotd_kolkata_venue_guide.pdf",
        "file_type": "PDF",
        "category": "POLICY",
        "chunks": [
            (
                "Operating Hours & Access: Lord of the Drinks (LOTD) Kolkata is located on the 4th Floor of "
                "South City Mall, 375 Prince Anwar Shah Road, Jadavpur, Kolkata - 700068. The venue operates "
                "seven days a week from 12:00 PM (Noon) to 12:00 AM (Midnight). Express high-speed elevators "
                "from the South City Mall main atrium provide direct access to the 4th floor entrance."
            ),
            (
                "Age Policy & Government ID Verification: Lord of the Drinks welcomes guests of all ages and "
                "families for lunch and dining until 7:00 PM. From 7:00 PM onwards, entry to the main lounge, "
                "high-top seating, and bar area is strictly restricted to guests aged 21 years and above. All "
                "guests entering after 7:00 PM must present valid original government-issued photo identification "
                "(Aadhaar, Passport, or Driver's License) at the security reception."
            ),
            (
                "Dress Code Standards: The establishment strictly enforces a Smart Casual dress code. Gentlemen "
                "are requested to wear collared shirts, tailored polos, full trousers or smart chinos, and closed "
                "footwear. Flip-flops, bathroom slippers, tracksuits, athletic gym shorts, and sleeveless tank tops "
                "or undershirts are strictly prohibited during evening operational hours after 7:00 PM."
            ),
            (
                "Valet Parking & South City Mall Amenities: Guests visiting Lord of the Drinks enjoy dedicated valet "
                "parking drop-off at the South City Mall main entrance porch. In addition, the South City Mall "
                "multi-level basement car parking offers covered parking for over 1,500 vehicles with direct elevator "
                "connectivity to the 4th floor venue."
            ),
            (
                "Table Reservation, Holding & Cancellation Policy: Table reservations are held for a maximum grace "
                "period of 15 minutes past the scheduled booking time before being released to walk-in waiting guests. "
                "For weekend evening bookings (Friday through Sunday) and parties of 6 or more, advance reservation "
                "through the AI Concierge or guest relations desk is highly advised. Cancellation or rescheduling is "
                "permitted up to 2 hours prior to the reservation time without penalty."
            ),
            (
                "Private Events, Cabanas & Corporate Gatherings: Lord of the Drinks Kolkata features exclusive VIP "
                "cabanas, a dedicated Ghost Bar section, and semi-private lounge areas suitable for hosting corporate "
                "mixers, birthday celebrations, and cocktail receptions for 15 to 150 guests. Custom banquet menus, "
                "dedicated bar service, and multimedia presentation screens are available upon request through Amit "
                "Hospitality Guest Relations (concierge@amithospitality.com / +91 11 4050 9900)."
            ),
        ],
    },
    {
        "title": "Lord of the Drinks Kolkata — Culinary Gastronomy, Mixology & Dietary Profile",
        "file_name": "lotd_kolkata_culinary_guide.pdf",
        "file_type": "PDF",
        "category": "MENU",
        "chunks": [
            (
                "Culinary Concept & Hospitality Group: Operated under Amit Hospitality LLP by Amit & Vanita Bajoria "
                "(Registered Office: 401 Kamalalaya Centre, 156A Lenin Sarani, Kolkata - 700013), Lord of the Drinks "
                "Kolkata brings world-class experiential dining to the City of Joy. The kitchen blends Continental "
                "classics, Asian wok gastronomy, Mediterranean tapas, and refined North Indian recipes."
            ),
            (
                "Signature Cocktails & Kolkata's Tallest Bar: LOTD Kolkata boasts the city's tallest bar installation "
                "and the famous Ghost Bar. Celebrity mixologist cocktails include 'My 18th Birthday' (premium vodka, "
                "butterscotch, popcorn syrup, salted caramel, and pineapple juice), 'Lavender Sour' (botanical gin with "
                "lavender blossom infusion and butterfly pea flower), 'Smoked Rosemary Negroni', and the local favorite "
                "'Kolkata Spiced Mule' showcasing native Gondhoraj citrus."
            ),
            (
                "Signature Appetizers & Small Plates: Acclaimed dishes include the Kasundi Mustard Crusted Bhetki "
                "Tikka (using fresh Kolkata river/coastal bhetki), Truffle & Edamame Crystal Dimsums, Ghost Bar "
                "Crispy Calamari, Paneer Khas Tikka stuffed with sundried tomatoes, and Loaded Ghost Bar Nachos Grande."
            ),
            (
                "Signature Main Courses & Pizzas: Standout dinner selections feature the 24-hour slow-cooked Dal "
                "Makhani with truffle butter, rich Kashmiri Lamb Rogan Josh with saffron naan, Wood-Fired Wild Mushroom "
                "& Truffle Oil Pizza on sourdough crust, and Pan-Seared Norwegian Salmon with saffron risotto."
            ),
            (
                "Dietary Accommodations & Pure Jain Dining: Lord of the Drinks operates strict kitchen segregation "
                "protocols for vegetarian and non-vegetarian preparation. A dedicated Jain menu—prepared strictly "
                "without onions, garlic, potatoes, or underground root vegetables—is readily available. Guests with "
                "gluten sensitivities, nut allergies, or vegan dietary preferences can request tailored dish adjustments "
                "with the floor captain or through the AI Concierge."
            ),
            (
                "Average Pricing & Payment Acceptance: The average dining and beverage spend is approximately ₹1,800 "
                "to ₹2,500 for two guests. All major credit cards, debit cards, UPI payments, and contactless mobile "
                "wallets are accepted. All bills are subject to applicable government GST and discretionary service charge."
            ),
        ],
    },
]

LOTD_POLICIES = [
    {
        "policy_type": "CANCELLATION",
        "title": "Reservation Cancellation & Rescheduling",
        "description": "Reservations may be cancelled or modified up to 2 hours prior to the reserved time without penalty. Table holds expire 15 minutes after the booked time.",
    },
    {
        "policy_type": "DRESS_CODE",
        "title": "Smart Casual Evening Dress Code",
        "description": "Smart Casual attire is enforced. Gentlemen are requested to wear collared shirts and closed shoes. Flip-flops, slippers, and sleeveless shirts are prohibited after 7 PM.",
    },
    {
        "policy_type": "AGE_RESTRICTION",
        "title": "Evening Age Policy (21+)",
        "description": "Guests of all ages are welcome for lunch dining until 7:00 PM. After 7:00 PM, entry is strictly 21+ with original government-issued photo identification.",
    },
    {
        "policy_type": "VALET",
        "title": "Valet & Mall Parking Facility",
        "description": "Valet parking is available at South City Mall main porch. Covered multi-level parking for 1,500+ cars is accessible via mall basement levels.",
    },
]

LOTD_FAQS = [
    {
        "category": "TIMING",
        "question": "What are the opening hours of Lord of the Drinks Kolkata?",
        "answer": "Lord of the Drinks at South City Mall, Kolkata is open daily from 12:00 PM (Noon) to 12:00 AM (Midnight) for lunch, sundowners, and evening dining.",
    },
    {
        "category": "LOCATION",
        "question": "Where is Lord of the Drinks located in Kolkata?",
        "answer": "Lord of the Drinks is located on the 4th Floor of South City Mall, 375 Prince Anwar Shah Road, Jadavpur, Kolkata - 700068. Express elevators in the mall atrium lead directly to the 4th floor entrance.",
    },
    {
        "category": "POLICY",
        "question": "What is the dress code and age policy at Lord of the Drinks Kolkata?",
        "answer": "Lord of the Drinks welcomes guests of all ages for lunch until 7:00 PM. From 7:00 PM onwards, entry to the lounge and bar is strictly 21+ with valid government photo ID. The dress code is Smart Casual (collared shirts, elegant attire, closed shoes for men; flip-flops and athletic wear are prohibited).",
    },
    {
        "category": "MENU",
        "question": "What are the signature cocktails and dishes at Lord of the Drinks Kolkata?",
        "answer": "Signature cocktails include 'My 18th Birthday' (popcorn syrup, butterscotch, vodka) and 'Lavender Sour'. Acclaimed dishes include Mustard Crusted Bhetki Tikka, Truffle Edamame Dimsums, 24-Hour Dal Makhani with Truffle Butter, and Wild Mushroom Truffle Pizza.",
    },
    {
        "category": "PARKING",
        "question": "Is parking available at Lord of the Drinks South City Mall?",
        "answer": "Yes, guests can utilize the South City Mall multi-level covered parking (1,500+ spaces) or convenient valet parking drop-off at the mall's main entrance porch.",
    },
    {
        "category": "DIETARY",
        "question": "Are vegetarian and Jain options available at Lord of the Drinks?",
        "answer": "Yes, Lord of the Drinks offers extensive vegetarian options and a dedicated Jain menu prepared without onion, garlic, or root vegetables with isolated kitchen preparation.",
    },
    {
        "category": "RESERVATIONS",
        "question": "How can I book a table or private event at LOTD Kolkata?",
        "answer": "You can reserve directly through our AI Concierge on this portal or contact Amit Hospitality Guest Relations at concierge@amithospitality.com / +91 11 4050 9900.",
    },
]

def seed_lord_of_the_drinks(db: Session = None):
    own_session = False
    if db is None:
        db = SessionLocal()
        own_session = True

    try:
        # 1. Ensure Restaurant exists
        restaurant = db.query(Restaurant).first()
        if not restaurant:
            restaurant = Restaurant(
                name="Amit Hospitality Group",
                slug="amit-hospitality",
                description="Prestigious portfolio of destination dining venues and cocktail lounges.",
                address="401 Kamalalaya Centre, 156A Lenin Sarani",
                city="Kolkata",
                phone="+91 11 4050 9900",
                email="concierge@amithospitality.com",
            )
            db.add(restaurant)
            db.commit()
            db.refresh(restaurant)

        # 2. Seed or Update Outlet
        outlet = db.query(Outlet).filter(Outlet.slug == LOTD_OUTLET_DATA["slug"]).first()
        if not outlet:
            outlet = Outlet(
                restaurant_id=restaurant.id,
                **LOTD_OUTLET_DATA,
            )
            db.add(outlet)
            db.commit()
            db.refresh(outlet)
            logger.info(f"Created new Outlet: '{outlet.name}' (ID: {outlet.id}, Slug: {outlet.slug})")
        else:
            for key, val in LOTD_OUTLET_DATA.items():
                setattr(outlet, key, val)
            outlet.restaurant_id = restaurant.id
            db.commit()
            db.refresh(outlet)
            logger.info(f"Updated existing Outlet: '{outlet.name}' (ID: {outlet.id}, Slug: {outlet.slug})")

        # 3. Seed Menu Categories for DEMO and REAL environments
        categories_by_name = {}
        for env in ["DEMO", "REAL"]:
            for cat_data in LOTD_CATEGORIES:
                cat = (
                    db.query(MenuCategory)
                    .filter(
                        MenuCategory.outlet_id == outlet.id,
                        MenuCategory.environment == env,
                        MenuCategory.name == cat_data["name"],
                    )
                    .first()
                )
                if not cat:
                    cat = MenuCategory(
                        outlet_id=outlet.id,
                        environment=env,
                        name=cat_data["name"],
                        display_order=cat_data["display_order"],
                        description=cat_data["description"],
                        is_active=True,
                    )
                    db.add(cat)
                    db.commit()
                    db.refresh(cat)
                categories_by_name[(env, cat_data["name"])] = cat.id

        logger.info(f"Seeded {len(LOTD_CATEGORIES)} Menu Categories for DEMO and REAL modes.")

        # 4. Seed Menu Items for DEMO and REAL environments
        seeded_items_count = 0
        for env in ["DEMO", "REAL"]:
            for item_data in LOTD_MENU_ITEMS:
                existing_item = (
                    db.query(MenuItem)
                    .filter(
                        MenuItem.outlet_id == outlet.id,
                        MenuItem.environment == env,
                        MenuItem.name == item_data["name"],
                    )
                    .first()
                )
                cat_id = categories_by_name.get((env, item_data["category_name"]))

                if not existing_item:
                    new_item = MenuItem(
                        outlet_id=outlet.id,
                        category_id=cat_id,
                        environment=env,
                        name=item_data["name"],
                        description=item_data["description"],
                        price=item_data["price"],
                        currency=item_data["currency"],
                        dietary_flags=item_data["dietary_flags"],
                        is_available=True,
                        is_signature=item_data["is_signature"],
                        display_order=item_data["display_order"],
                    )
                    db.add(new_item)
                    seeded_items_count += 1
                else:
                    existing_item.category_id = cat_id
                    existing_item.description = item_data["description"]
                    existing_item.price = item_data["price"]
                    existing_item.dietary_flags = item_data["dietary_flags"]
                    existing_item.is_signature = item_data["is_signature"]
                    existing_item.display_order = item_data["display_order"]
                    existing_item.is_available = True
        db.commit()
        logger.info(f"Seeded/Updated {len(LOTD_MENU_ITEMS)} Menu Items across DEMO and REAL modes.")

        # 5. Seed RAG Knowledge Documents & Vector Chunks
        for env in ["DEMO", "REAL"]:
            for doc_data in LOTD_KNOWLEDGE_DOCS:
                kdoc = (
                    db.query(KnowledgeDocument)
                    .filter(
                        KnowledgeDocument.outlet_id == outlet.id,
                        KnowledgeDocument.environment == env,
                        KnowledgeDocument.file_name == doc_data["file_name"],
                    )
                    .first()
                )
                if not kdoc:
                    kdoc = KnowledgeDocument(
                        environment=env,
                        outlet_id=outlet.id,
                        title=doc_data["title"],
                        file_name=doc_data["file_name"],
                        file_type=doc_data["file_type"],
                        category=doc_data["category"],
                        verification_status="VERIFIED",
                        verified_by="Amit Hospitality Knowledge Engineering",
                        chunk_count=len(doc_data["chunks"]),
                        is_active=True,
                    )
                    db.add(kdoc)
                    db.commit()
                    db.refresh(kdoc)
                else:
                    kdoc.title = doc_data["title"]
                    kdoc.verification_status = "VERIFIED"
                    kdoc.chunk_count = len(doc_data["chunks"])
                    kdoc.is_active = True
                    db.commit()

                # Check and seed chunks
                existing_chunks = db.query(KnowledgeChunk).filter(KnowledgeChunk.document_id == kdoc.id).all()
                if not existing_chunks or len(existing_chunks) != len(doc_data["chunks"]):
                    # Clear out outdated chunks if mismatched
                    if existing_chunks:
                        for ec in existing_chunks:
                            db.delete(ec)
                        db.commit()

                    for c_idx, chunk_text in enumerate(doc_data["chunks"]):
                        vec = generate_embedding(chunk_text)
                        meta = {
                            "title": doc_data["title"],
                            "outlet_id": outlet.id,
                            "outlet_name": outlet.name,
                            "environment": env,
                            "category": doc_data["category"],
                            "chunk_index": c_idx,
                        }
                        chunk = KnowledgeChunk(
                            document_id=kdoc.id,
                            environment=env,
                            outlet_id=outlet.id,
                            chunk_index=c_idx,
                            content=chunk_text,
                            metadata_json=json.dumps(meta),
                            embedding_json=json.dumps(vec),
                            is_active=True,
                        )
                        db.add(chunk)
                    db.commit()

        logger.info("Seeded RAG Knowledge Documents & Chunks with 256-dim embeddings for DEMO and REAL modes.")

        # 6. Seed Policies
        for env in ["DEMO", "REAL"]:
            for pol_data in LOTD_POLICIES:
                existing_pol = (
                    db.query(Policy)
                    .filter(
                        Policy.outlet_id == outlet.id,
                        Policy.environment == env,
                        Policy.policy_type == pol_data["policy_type"],
                    )
                    .first()
                )
                if not existing_pol:
                    pol = Policy(
                        outlet_id=outlet.id,
                        environment=env,
                        policy_type=pol_data["policy_type"],
                        title=pol_data["title"],
                        description=pol_data["description"],
                        is_active=True,
                    )
                    db.add(pol)
                else:
                    existing_pol.title = pol_data["title"]
                    existing_pol.description = pol_data["description"]
                    existing_pol.is_active = True
        db.commit()
        logger.info(f"Seeded {len(LOTD_POLICIES)} Policies for DEMO and REAL modes.")

        # 7. Seed Grounded FAQs
        for env in ["DEMO", "REAL"]:
            for faq_data in LOTD_FAQS:
                existing_faq = (
                    db.query(FAQ)
                    .filter(
                        FAQ.outlet_id == outlet.id,
                        FAQ.environment == env,
                        FAQ.question == faq_data["question"],
                    )
                    .first()
                )
                if not existing_faq:
                    faq = FAQ(
                        outlet_id=outlet.id,
                        environment=env,
                        category=faq_data["category"],
                        question=faq_data["question"],
                        answer=faq_data["answer"],
                        is_active=True,
                    )
                    db.add(faq)
                else:
                    existing_faq.answer = faq_data["answer"]
                    existing_faq.category = faq_data["category"]
                    existing_faq.is_active = True
        db.commit()
        logger.info(f"Seeded {len(LOTD_FAQS)} FAQs for DEMO and REAL modes.")

        # 8. Record Audit Log
        audit = AuditLog(
            user_name="System Knowledge Engineer",
            user_role="SUPER_ADMIN",
            action="OUTLET_SEEDED",
            entity_type="OUTLET",
            entity_id=outlet.id,
            environment="DEMO",
            details=f"Authoritative seed executed for '{outlet.name}' (Kolkata). Loaded categories, menus, RAG documents, and FAQs.",
        )
        db.add(audit)
        db.commit()

        logger.info("=" * 60)
        logger.info(f"[SUCCESS] Lord of the Drinks seeded successfully! Outlet ID: {outlet.id}")
        logger.info("=" * 60)
        return outlet.id

    except Exception as e:
        db.rollback()
        logger.error(f"[ERROR] Failed to seed Lord of the Drinks: {e}", exc_info=True)
        raise
    finally:
        if own_session:
            db.close()

if __name__ == "__main__":
    seed_lord_of_the_drinks()
