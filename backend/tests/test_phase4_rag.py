import sys
import os
import io
import json
import pytest

# Ensure utf-8 encoding on Windows console
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from app.database import Base
from app.models.user import User
from app.models.outlet import Outlet, MenuItem
from app.models.knowledge import KnowledgeDocument, KnowledgeChunk
from app.models.conversation import Conversation, Message
from app.models.audit import EnvironmentSetting, AuditLog
from app.services.intent_service import detect_intent
from app.services.rag_service import generate_rag_chat_response
from app.services.embedding_service import generate_embedding
from app.routers.chat import handle_chat_message, get_chat_history
from app.routers.environment import switch_environment
from app.schemas.chat import ChatMessageRequest
from app.schemas.knowledge import EnvironmentSwitchRequest

TEST_DB_PATH = os.path.join(backend_dir, "test_phase4.db")
if os.path.exists(TEST_DB_PATH):
    try:
        os.remove(TEST_DB_PATH)
    except Exception:
        pass

engine = create_engine(f"sqlite:///{TEST_DB_PATH}", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def setup_module():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        # 1. Admin
        admin = User(
            id=1,
            email="admin@amithospitality.com",
            password_hash="testhash",
            full_name="Vikram Sharma",
            role="SUPER_ADMIN",
            is_active=True,
        )
        db.add(admin)

        # 2. Outlets
        outlet1 = Outlet(
            id=1,
            name="Amber Terrace Rooftop",
            slug="amber-terrace",
            outlet_type="Rooftop Lounge",
            cuisine_type="Modern Pan-Asian",
            opening_time="17:30",
            closing_time="01:30",
            dress_code="Smart Casual (No flip-flops or sleeveless jerseys)",
            seating_capacity=120,
            location="14th Floor, Skyline Tower, MG Road",
            description="Luxury rooftop lounge with skyline views.",
        )
        outlet2 = Outlet(
            id=2,
            name="Saffron & Silk",
            slug="saffron-and-silk",
            outlet_type="Fine Dining Restaurant",
            cuisine_type="Royal Awadhi & Dum Gastronomy",
            opening_time="12:30",
            closing_time="23:45",
            dress_code="Formal / Elegant Casual",
            seating_capacity=85,
            location="Amit Heritage Plaza, Ground Level",
            description="Heritage Awadhi dining.",
        )
        db.add_all([outlet1, outlet2])

        # 3. Environment: initial DEMO
        env = EnvironmentSetting(
            active_environment="DEMO",
            updated_by_name="Tester",
            switch_reason="Test setup",
        )
        db.add(env)

        # 4. DEMO Menu items
        m1 = MenuItem(
            id=1,
            outlet_id=1,
            environment="DEMO",
            name="Truffle Edamame Dumplings",
            description="Steamed parcels infused with white truffle essence.",
            price=695.0,
            currency="INR",
            dietary_flags="VEG",
            is_available=True,
            is_signature=True,
        )
        m2 = MenuItem(
            id=2,
            outlet_id=1,
            environment="DEMO",
            name="Glazed Chilean Sea Bass",
            description="Slow-roasted sea bass with aged mirin and ginger reduction.",
            price=1250.0,
            currency="INR",
            dietary_flags="NON_VEG",
            is_available=True,
            is_signature=True,
        )
        db.add_all([m1, m2])

        # 5. DEMO Knowledge Document & Chunks
        doc_demo = KnowledgeDocument(
            id=1,
            environment="DEMO",
            outlet_id=1,
            title="Amber Terrace Operating Guidelines (Sample)",
            file_name="amber_terrace_sample.pdf",
            file_type="PDF",
            category="TIMING",
            verification_status="UNVERIFIED",
            chunk_count=2,
            is_active=True,
        )
        db.add(doc_demo)
        db.commit()

        c1 = KnowledgeChunk(
            document_id=doc_demo.id,
            environment="DEMO",
            outlet_id=1,
            chunk_index=0,
            content="Operating hours for Amber Terrace: Monday to Sunday 17:30 to 01:30. Complimentary valet parking is provided at Skyline Tower entrance.",
            embedding_json=json.dumps(generate_embedding("Operating hours for Amber Terrace 17:30 to 01:30 valet parking")),
            is_active=True,
        )
        c2 = KnowledgeChunk(
            document_id=doc_demo.id,
            environment="DEMO",
            outlet_id=1,
            chunk_index=1,
            content="Dress code strictly observed: Smart Casual. Gentlemen are requested to wear tailored trousers and collared shirts. Flip-flops and athletic sportswear are strictly prohibited.",
            embedding_json=json.dumps(generate_embedding("Dress code strictly observed Smart Casual trousers collared shirts flip-flops prohibited")),
            is_active=True,
        )
        db.add_all([c1, c2])

        # 6. REAL Knowledge Document & Chunks (Verified Corporate Asset)
        doc_real = KnowledgeDocument(
            id=2,
            environment="REAL",
            outlet_id=1,
            title="Official Amit Hospitality ESG & Corporate Sustainability Policy",
            file_name="amit_esg_policy_verified.pdf",
            file_type="PDF",
            category="POLICY",
            verification_status="VERIFIED",
            verified_by="Super Admin",
            verified_at=datetime.utcnow(),
            chunk_count=1,
            is_active=True,
        )
        db.add(doc_real)
        db.commit()

        c_real = KnowledgeChunk(
            document_id=doc_real.id,
            environment="REAL",
            outlet_id=1,
            chunk_index=0,
            content="Amit Hospitality Group verified corporate charter: All culinary outlets must source 100% organic farm produce within 200 km radius and achieve zero single-use plastic waste across banquets by Q4 2026.",
            embedding_json=json.dumps(generate_embedding("Amit Hospitality verified corporate charter organic farm produce zero single-use plastic waste")),
            is_active=True,
        )
        db.add(c_real)
        db.commit()
    finally:
        db.close()

def teardown_module():
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass

# 1. Test Intent Detection & Entity Extraction
def test_intent_detection():
    # Menu inquiry
    r1 = detect_intent("Show me the signature menu and chef specials")
    assert r1["intent"] == "MENU_INQUIRY"

    # Pricing inquiry
    r2 = detect_intent("What is the price of the Chilean Sea Bass?")
    assert r2["intent"] == "PRICING_INQUIRY"

    # Timing & Location
    r3 = detect_intent("What time do you open and do you have valet parking?")
    assert r3["intent"] == "TIMING_LOCATION"

    # Reservation with guest count entity
    r4 = detect_intent("I would like to book a table for 6 guests tonight at 8pm")
    assert r4["intent"] == "RESERVATION_REQUEST"
    assert r4["entities"].get("guest_count") == 6

    # Dietary inquiry with Jain entity
    r5 = detect_intent("Do you have Jain food prepared without onion and garlic?")
    assert r5["intent"] == "DIETARY_INQUIRY"
    assert "JAIN" in r5["entities"].get("dietary", [])

    # Human handover
    r6 = detect_intent("I want to speak with a human manager immediately")
    assert r6["intent"] == "HUMAN_HANDOVER"

# 2. Test DEMO Mode Menu & Pricing Retrieval
def test_demo_mode_chat_generation():
    db = TestingSessionLocal()
    try:
        # Chat inquiry about Sea Bass price
        req = ChatMessageRequest(
            session_id="test_session_demo_1",
            outlet_id=1,
            message="What is the price of the Glazed Chilean Sea Bass?",
            language="EN",
        )
        res = handle_chat_message(req=req, db=db)
        
        assert res.environment == "DEMO"
        assert res.is_demo is True
        assert "1,250" in res.reply
        assert "Glazed Chilean Sea Bass" in res.reply
        assert "[DEMO DATA" in res.reply
        assert len(res.suggested_actions) > 0
    finally:
        db.close()

# 3. Test DEMO Mode Policy & Timings Retrieval
def test_demo_mode_policy_retrieval():
    db = TestingSessionLocal()
    try:
        req = ChatMessageRequest(
            session_id="test_session_demo_2",
            outlet_id=1,
            message="What are your opening hours and do you have valet?",
            language="EN",
        )
        res = handle_chat_message(req=req, db=db)
        assert "17:30" in res.reply
        assert "valet" in res.reply.lower()
        assert len(res.citations) > 0
        assert res.citations[0].document_title == "Amber Terrace Operating Guidelines (Sample)"
    finally:
        db.close()

# 4. Test REAL Mode Zero-Hallucination Fallback
def test_real_mode_strict_fallback():
    db = TestingSessionLocal()
    admin = db.query(User).filter(User.id == 1).first()
    try:
        # Switch to REAL mode
        switch_environment(
            req=EnvironmentSwitchRequest(
                target_environment="REAL",
                reason="Testing strict real-mode zero hallucination guarantee",
                confirm_acknowledgment=True,
            ),
            current_user=admin,
            db=db,
        )

        # Ask for dish price in REAL mode (no verified menu uploaded yet)
        req = ChatMessageRequest(
            session_id="test_session_real_1",
            outlet_id=1,
            message="What is the price of Truffle Dumplings?",
            language="EN",
        )
        res = handle_chat_message(req=req, db=db)

        # MUST strictly trigger verified information fallback
        assert res.environment == "REAL"
        assert res.is_demo is False
        assert "VERIFIED INFORMATION REQUIRED" in res.reply
        assert "695" not in res.reply  # Demo price must NEVER appear!
        assert "guestrelations@amithospitality.com" in res.reply
        assert len(res.citations) == 0
    finally:
        # Switch back to DEMO
        switch_environment(
            req=EnvironmentSwitchRequest(
                target_environment="DEMO",
                reason="Reset to DEMO",
                confirm_acknowledgment=True,
            ),
            current_user=admin,
            db=db,
        )
        db.close()

# 5. Test REAL Mode Grounding with Verified Document
def test_real_mode_verified_grounding():
    db = TestingSessionLocal()
    admin = db.query(User).filter(User.id == 1).first()
    try:
        switch_environment(
            req=EnvironmentSwitchRequest(
                target_environment="REAL",
                reason="Testing real verified grounding",
                confirm_acknowledgment=True,
            ),
            current_user=admin,
            db=db,
        )

        # Ask about verified ESG / sustainability policy
        req = ChatMessageRequest(
            session_id="test_session_real_2",
            outlet_id=1,
            message="Tell me about your organic farm produce and single-use plastic policy",
            language="EN",
        )
        res = handle_chat_message(req=req, db=db)

        assert res.environment == "REAL"
        assert "organic farm produce" in res.reply
        assert "plastic" in res.reply
        assert len(res.citations) > 0
        assert "Official Amit Hospitality ESG" in res.citations[0].document_title
    finally:
        switch_environment(
            req=EnvironmentSwitchRequest(
                target_environment="DEMO",
                reason="Reset to DEMO",
                confirm_acknowledgment=True,
            ),
            current_user=admin,
            db=db,
        )
        db.close()

# 6. Test Conversation History Persistence
def test_conversation_history_persistence():
    db = TestingSessionLocal()
    try:
        session_id = "test_session_history_turn"
        # Turn 1
        handle_chat_message(
            req=ChatMessageRequest(
                session_id=session_id,
                outlet_id=1,
                message="Hello, do you have outdoor seating?",
                language="EN",
            ),
            db=db,
        )
        # Turn 2
        handle_chat_message(
            req=ChatMessageRequest(
                session_id=session_id,
                outlet_id=1,
                message="What are your timings?",
                language="EN",
            ),
            db=db,
        )

        # Fetch history
        hist = get_chat_history(session_id=session_id, db=db)
        assert len(hist["messages"]) == 4  # 2 user messages + 2 assistant messages
        assert hist["messages"][0]["sender"] == "USER"
        assert hist["messages"][1]["sender"] == "ASSISTANT"
        assert hist["messages"][2]["sender"] == "USER"
        assert hist["messages"][3]["sender"] == "ASSISTANT"
    finally:
        db.close()

if __name__ == "__main__":
    setup_module()
    try:
        print("[1/6] Testing intent detection & entity extraction...")
        test_intent_detection()
        print("  -> PASSED")

        print("[2/6] Testing DEMO mode menu & pricing RAG...")
        test_demo_mode_chat_generation()
        print("  -> PASSED")

        print("[3/6] Testing DEMO mode policy & timings retrieval...")
        test_demo_mode_policy_retrieval()
        print("  -> PASSED")

        print("[4/6] Testing REAL mode zero-hallucination fallback...")
        test_real_mode_strict_fallback()
        print("  -> PASSED")

        print("[5/6] Testing REAL mode verified grounding...")
        test_real_mode_verified_grounding()
        print("  -> PASSED")

        print("[6/6] Testing conversation history persistence...")
        test_conversation_history_persistence()
        print("  -> PASSED")

        print("\nALL 6 PHASE 4 RAG & AI CHATBOT TESTS PASSED SUCCESSFULLY!")
    finally:
        teardown_module()
