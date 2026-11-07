import os
import sys

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.outlet import Outlet, MenuItem
from app.models.audit import EnvironmentSetting
from app.services.rag_service import generate_rag_chat_response

def setup_test_db():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    return db

def test_phase7_multilingual_and_outlets():
    print("\n--- BEGIN PHASE 7: MULTI-OUTLET & MULTILINGUAL CONCIERGE TESTS ---")
    db = setup_test_db()

    # 1. Seed Environment Setting (DEMO)
    env_setting = EnvironmentSetting(
        active_environment="DEMO",
        updated_by_name="System",
        switch_reason="Phase 7 Multilingual Test",
    )
    db.add(env_setting)

    # 2. Seed 3 Distinct Luxury Outlets
    outlet1 = Outlet(
        name="Amber Terrace Rooftop",
        slug="amber-terrace",
        outlet_type="Rooftop Lounge & Bar",
        cuisine_type="Modern Asian & Pan-Asian Tapas",
        location="12th Floor Sky Deck, Connaught Place, New Delhi",
        opening_time="17:00",
        closing_time="01:00",
        dress_code="Smart Evening Casual",
        seating_capacity=140,
        is_active=True,
    )
    outlet2 = Outlet(
        name="Saffron & Silk",
        slug="saffron-silk",
        outlet_type="Royal Indian Fine Dining",
        cuisine_type="Awadhi & Mughlai Heritage",
        location="Ground Atrium, Diplomatic Enclave, New Delhi",
        opening_time="12:30",
        closing_time="23:30",
        dress_code="Formal / Traditional Elegance",
        seating_capacity=95,
        is_active=True,
    )
    outlet3 = Outlet(
        name="The Velvet Cellar",
        slug="velvet-cellar",
        outlet_type="Speakeasy & Wine Salon",
        cuisine_type="Artisan Charcuterie & European Small Plates",
        location="Sub-level Vault, Lodhi Road, New Delhi",
        opening_time="18:30",
        closing_time="02:00",
        dress_code="Glamour & Cocktail Chic",
        seating_capacity=60,
        is_active=True,
    )
    db.add_all([outlet1, outlet2, outlet3])
    db.commit()

    # 3. Seed Menu Items across outlets
    dish1 = MenuItem(
        outlet_id=outlet1.id,
        environment="DEMO",
        name="Truffle Edamame Dumplings",
        price=850.0,
        description="Silken crystal skins filled with crushed edamame, shaved black truffles, and white soy reduction.",
        dietary_flags="VEG",
        is_available=True,
    )
    dish2 = MenuItem(
        outlet_id=outlet2.id,
        environment="DEMO",
        name="Royal Awadhi Dum Biryani",
        price=1250.0,
        description="Slow-cooked fragrant aged basmati rice layered with saffron, royal spices, and tender cuts sealed in purdah.",
        dietary_flags="NON_VEG",
        is_available=True,
    )
    db.add_all([dish1, dish2])
    db.commit()
    print("  [OK] Outlets and multi-outlet menu items seeded.")

    # 4. Test English Menu & Pricing Query
    res_en = generate_rag_chat_response(
        db=db,
        session_id="sess_p7_en",
        outlet=outlet1,
        user_message="What is the price of Truffle Edamame Dumplings?",
        language="EN",
    )
    print(f"  [OK] English Response generated:\n       {res_en.reply.splitlines()[0]}")
    assert "Amber Terrace Rooftop" in res_en.reply
    assert "Truffle Edamame Dumplings" in res_en.reply
    assert "850.00" in res_en.reply
    assert "[DEMO DATA" in res_en.reply

    # 5. Test Hindi / Hinglish Menu & Pricing Query (language="HI")
    res_hi = generate_rag_chat_response(
        db=db,
        session_id="sess_p7_hi_1",
        outlet=outlet1,
        user_message="Truffle Dumplings ka price kitna hai?",
        language="HI",
    )
    print(f"  [OK] Hindi Menu Response generated:\n       {res_hi.reply.splitlines()[0]}")
    assert "Amber Terrace Rooftop" in res_hi.reply
    assert "Truffle Edamame Dumplings" in res_hi.reply
    assert "850.00" in res_hi.reply
    assert "DEMO DATA" in res_hi.reply

    # 6. Test Hindi Table Reservation Query
    res_hi_res = generate_rag_chat_response(
        db=db,
        session_id="sess_p7_hi_2",
        outlet=outlet2,
        user_message="Mujhe Saffron & Silk me kal raat 4 logo ke liye table book karni hai",
        language="HI",
    )
    print(f"  [OK] Hindi Reservation Response generated:\n       {res_hi_res.reply.splitlines()[0]}")
    assert "Saffron & Silk" in res_hi_res.reply
    assert "table reservation" in res_hi_res.reply.lower() or "booking" in res_hi_res.reply.lower()

    # 7. Test Hindi Dietary Accommodations (Jain dining)
    res_hi_diet = generate_rag_chat_response(
        db=db,
        session_id="sess_p7_hi_3",
        outlet=outlet2,
        user_message="Kya aapke yahan Jain food milta hai bina pyaaz aur lehsun ka?",
        language="HI",
    )
    print(f"  [OK] Hindi Dietary Response generated:\n       {res_hi_diet.reply.splitlines()[0]}")
    assert "Jain" in res_hi_diet.reply
    assert "pyaaz" in res_hi_diet.reply.lower()

    # 8. Test Zero-Hallucination Isolation in REAL mode with Hindi
    env_setting.active_environment = "REAL"
    db.commit()

    res_real_hi = generate_rag_chat_response(
        db=db,
        session_id="sess_p7_real_hi",
        outlet=outlet3,
        user_message="Wine cellar me champagne tasting ka price kya hai?",
        language="HI",
    )
    print(f"  [OK] Real Mode Hindi Guard Response generated:\n       {res_real_hi.reply.splitlines()[0]}")
    assert "[REAL MODE — VERIFIED INFORMATION REQUIRED]" in res_real_hi.reply
    assert "verified documents" in res_real_hi.reply.lower() or "verified" in res_real_hi.reply.lower()
    assert "guestrelations@amithospitality.com" in res_real_hi.reply

    # 9. Verify Embed Widget Artifacts Exist
    widget_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/public/widget.js"))
    embed_test_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/public/embed-test.html"))
    assert os.path.exists(widget_path), f"widget.js missing at {widget_path}"
    assert os.path.exists(embed_test_path), f"embed-test.html missing at {embed_test_path}"

    with open(widget_path, "r", encoding="utf-8") as f:
        w_content = f.read()
        assert "amit-concierge-launcher" in w_content
        assert "amit-concierge-frame-container" in w_content
        assert "amithospitality.com" in w_content
    print("  [OK] Embeddable widget.js script verified.")

    print("\n--- PHASE 7: ALL TESTS PASSED SUCCESSFULLY! ---\n")

if __name__ == "__main__":
    test_phase7_multilingual_and_outlets()
