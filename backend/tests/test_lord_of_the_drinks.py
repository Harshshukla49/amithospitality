"""
Lord of the Drinks (LOTD) Kolkata — Grounded RAG & Data Integrity Test Suite
Enterprise Hospitality Intelligence Platform — Amit Hospitality Group

Verifies:
1. Lord of the Drinks outlet record, slug, location, timings, and seating capacity.
2. Menu categories and signature items (My 18th Birthday, Lavender Sour, Mustard Crusted Bhetki, etc.).
3. Grounded RAG knowledge documents and chunk embeddings (256-dim).
4. Zero-hallucination chat message handling for LOTD.
5. Venue policies and grounded FAQs.
"""

import sys
import os
import pytest

# Ensure utf-8 encoding on Windows console
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.database import SessionLocal
from app.models.outlet import Outlet, MenuCategory, MenuItem
from app.models.knowledge import KnowledgeDocument, KnowledgeChunk, Policy, FAQ
from app.routers.chat import handle_chat_message
from app.schemas.chat import ChatMessageRequest
from app.services.embedding_service import search_relevant_chunks, generate_embedding

@pytest.fixture(scope="module")
def db_session():
    db = SessionLocal()
    yield db
    db.close()

def test_lotd_outlet_record(db_session):
    """Verify Lord of the Drinks exists with authoritative attributes."""
    outlet = db_session.query(Outlet).filter(Outlet.slug == "lord-of-the-drinks").first()
    assert outlet is not None, "Lord of the Drinks outlet must exist in database"
    assert outlet.name == "Lord of the Drinks"
    assert "South City Mall" in outlet.location
    assert "Kolkata" in outlet.location
    assert outlet.opening_time == "12:00"
    assert outlet.closing_time == "00:00"
    assert outlet.seating_capacity == 220
    assert outlet.is_popular is True
    assert outlet.is_active is True

def test_lotd_categories_and_items(db_session):
    """Verify menu categories and signature menu items."""
    outlet = db_session.query(Outlet).filter(Outlet.slug == "lord-of-the-drinks").first()
    assert outlet is not None

    categories = db_session.query(MenuCategory).filter(
        MenuCategory.outlet_id == outlet.id,
        MenuCategory.environment == "DEMO"
    ).all()
    assert len(categories) >= 5, f"Expected at least 5 categories, got {len(categories)}"

    cat_names = [c.name for c in categories]
    assert "Signature Cocktails & Spirits" in cat_names
    assert "Artisanal Dimsums & Tapas" in cat_names
    assert "Continental & Pan-Asian Mains" in cat_names

    # Check signature cocktails
    my18th = db_session.query(MenuItem).filter(
        MenuItem.outlet_id == outlet.id,
        MenuItem.name == "My 18th Birthday",
        MenuItem.environment == "DEMO"
    ).first()
    assert my18th is not None
    assert my18th.price == 675.0
    assert my18th.is_signature is True
    assert "popcorn syrup" in my18th.description.lower() or "butterscotch" in my18th.description.lower()

    lavender_sour = db_session.query(MenuItem).filter(
        MenuItem.outlet_id == outlet.id,
        MenuItem.name == "Lavender Sour",
        MenuItem.environment == "DEMO"
    ).first()
    assert lavender_sour is not None
    assert lavender_sour.price == 695.0

    bhetki = db_session.query(MenuItem).filter(
        MenuItem.outlet_id == outlet.id,
        MenuItem.name == "Mustard Crusted Bhetki Tikka",
        MenuItem.environment == "DEMO"
    ).first()
    assert bhetki is not None
    assert bhetki.dietary_flags == "NON_VEG"
    assert bhetki.price == 795.0

def test_lotd_rag_knowledge_and_chunks(db_session):
    """Verify knowledge documents and chunk embeddings."""
    outlet = db_session.query(Outlet).filter(Outlet.slug == "lord-of-the-drinks").first()
    assert outlet is not None

    docs = db_session.query(KnowledgeDocument).filter(
        KnowledgeDocument.outlet_id == outlet.id,
        KnowledgeDocument.environment == "DEMO"
    ).all()
    assert len(docs) >= 2, f"Expected at least 2 knowledge docs, got {len(docs)}"

    chunks = db_session.query(KnowledgeChunk).filter(
        KnowledgeChunk.outlet_id == outlet.id,
        KnowledgeChunk.environment == "DEMO"
    ).all()
    assert len(chunks) >= 12, f"Expected at least 12 vector chunks, got {len(chunks)}"

    # Test vector search for cocktails
    cocktail_chunks = search_relevant_chunks(
        db=db_session,
        query="signature cocktails My 18th Birthday Lavender Sour",
        outlet_id=outlet.id,
        environment="DEMO",
        top_k=3
    )
    assert len(cocktail_chunks) > 0
    top_chunk = cocktail_chunks[0]
    assert "18th Birthday" in top_chunk["content"] or "Ghost Bar" in top_chunk["content"] or "cocktail" in top_chunk["content"].lower()

def test_lotd_concierge_chat(db_session):
    """Verify AI Concierge chat for Lord of the Drinks."""
    outlet = db_session.query(Outlet).filter(Outlet.slug == "lord-of-the-drinks").first()
    assert outlet is not None

    # Query 1: Cocktails inquiry
    req1 = ChatMessageRequest(
        session_id="test_sess_lotd_test",
        outlet_id=outlet.id,
        message="What are your signature cocktails and what is in My 18th Birthday?"
    )
    res1 = handle_chat_message(req1, db=db_session)
    assert res1.reply is not None
    assert len(res1.citations) > 0
    assert "Lord of the Drinks" in res1.reply
    assert "My 18th Birthday" in res1.reply or "18th Birthday" in res1.reply

    # Query 2: Location and parking inquiry
    req2 = ChatMessageRequest(
        session_id="test_sess_lotd_test",
        outlet_id=outlet.id,
        message="Where are you located in South City Mall and is parking available?"
    )
    res2 = handle_chat_message(req2, db=db_session)
    assert res2.reply is not None
    assert len(res2.citations) > 0
    assert "South City Mall" in res2.reply or "Parking" in res2.reply or "valet" in res2.reply.lower()

def test_lotd_policies_and_faqs(db_session):
    """Verify venue policies and FAQs."""
    outlet = db_session.query(Outlet).filter(Outlet.slug == "lord-of-the-drinks").first()
    assert outlet is not None

    policies = db_session.query(Policy).filter(
        Policy.outlet_id == outlet.id,
        Policy.environment == "DEMO"
    ).all()
    assert len(policies) >= 4

    pol_types = [p.policy_type for p in policies]
    assert "CANCELLATION" in pol_types
    assert "DRESS_CODE" in pol_types
    assert "AGE_RESTRICTION" in pol_types

    faqs = db_session.query(FAQ).filter(
        FAQ.outlet_id == outlet.id,
        FAQ.environment == "DEMO"
    ).all()
    assert len(faqs) >= 7
    questions = [f.question for f in faqs]
    assert any("opening hours" in q.lower() for q in questions)
    assert any("dress code" in q.lower() for q in questions)
