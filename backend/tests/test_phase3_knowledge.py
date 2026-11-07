import sys
import os
import io
import json
import pytest

# Ensure utf-8 encoding on Windows console
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Ensure backend directory is in python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from app.database import Base
from app.models.user import User
from app.models.outlet import Outlet, Restaurant
from app.models.knowledge import KnowledgeDocument, KnowledgeChunk
from app.models.audit import EnvironmentSetting, AuditLog
from app.services.document_service import (
    extract_document_content,
    chunk_text,
    extract_text_from_txt,
    extract_text_from_spreadsheet,
)
from app.services.embedding_service import (
    generate_embedding,
    cosine_similarity,
    keyword_overlap_score,
    search_relevant_chunks,
)
from app.routers.knowledge import (
    list_documents,
    get_document_detail,
    add_manual_knowledge,
    update_document,
    toggle_document_status,
    delete_document,
    search_knowledge,
    get_knowledge_stats,
)
from app.routers.environment import switch_environment, get_active_environment
from app.schemas.knowledge import (
    ManualKnowledgeCreate,
    DocumentUpdateRequest,
    DocumentStatusUpdateRequest,
    EnvironmentSwitchRequest,
)

# Test DB Setup
TEST_DB_PATH = os.path.join(backend_dir, "test_phase3.db")
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
        # Seed test admin
        admin = User(
            id=1,
            email="admin@amithospitality.com",
            password_hash="testhash",
            full_name="Vikram Sharma",
            role="SUPER_ADMIN",
            is_active=True,
        )
        db.add(admin)

        # Seed outlet
        outlet = Outlet(
            id=1,
            name="Amber Terrace Rooftop",
            slug="amber-terrace",
            outlet_type="Rooftop Lounge",
            cuisine_type="Pan-Asian",
            opening_time="17:30",
            closing_time="01:30",
            dress_code="Smart Casual",
            seating_capacity=100,
            location="MG Road",
            description="Luxury rooftop",
        )
        db.add(outlet)

        # Seed initial environment setting in DEMO mode
        setting = EnvironmentSetting(
            active_environment="DEMO",
            updated_by_name="System Initializer",
            switch_reason="Bootstrap",
        )
        db.add(setting)
        db.commit()
    finally:
        db.close()

def teardown_module():
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass

# 1. Test Document Extraction
def test_txt_and_csv_extraction():
    # Test TXT
    tmp_txt = os.path.join(backend_dir, "test_sample.txt")
    with open(tmp_txt, "w", encoding="utf-8") as f:
        f.write("Amber Terrace operates from 17:30 to 01:30 daily.\n\nDress code is strictly Smart Casual.")
    
    sections = extract_document_content(tmp_txt, "TXT")
    assert len(sections) >= 1
    assert "Smart Casual" in sections[0]["content"]
    os.remove(tmp_txt)

    # Test CSV
    tmp_csv = os.path.join(backend_dir, "test_sample.csv")
    with open(tmp_csv, "w", encoding="utf-8", newline="") as f:
        f.write("Dish,Category,Price\nGalouti Kebab,Awadhi Starter,850\nDal Heritage,Main Course,650\n")
    
    csv_sections = extract_document_content(tmp_csv, "CSV")
    assert len(csv_sections) >= 1
    assert "Galouti Kebab" in csv_sections[0]["content"]
    assert "850" in csv_sections[0]["content"]
    os.remove(tmp_csv)

# 2. Test Semantic Chunking with Overlap
def test_semantic_chunking():
    long_content = "Word " * 600
    sections = [{"title": "Corporate Guidelines", "page_number": 1, "content": long_content}]
    chunks = chunk_text(sections, chunk_size=200, chunk_overlap=30)
    assert len(chunks) > 1
    for c in chunks:
        assert "Corporate Guidelines" in c["content"]
        assert c["chunk_index"] is not None

# 3. Test Embedding & Cosine Similarity
def test_embedding_and_cosine():
    vec1 = generate_embedding("What is the dress code policy for rooftop lounge?")
    vec2 = generate_embedding("Dress code is smart casual with collared shirts and trousers.")
    vec3 = generate_embedding("Astrophysics and gravitational waves in deep space.")

    sim_related = cosine_similarity(vec1, vec2)
    sim_unrelated = cosine_similarity(vec1, vec3)

    assert sim_related > sim_unrelated
    assert sim_related > 0.25

# 4. Test Knowledge Manual Creation & Storage
def test_manual_knowledge_creation():
    db = TestingSessionLocal()
    admin = db.query(User).filter(User.id == 1).first()

    # Create in DEMO
    demo_doc = add_manual_knowledge(
        req=ManualKnowledgeCreate(
            title="Amber Terrace Dress Code Guidelines",
            content="Gentlemen must wear collared shirts and tailored trousers. Flip-flops and sleeveless tops are not permitted.",
            category="POLICY",
            outlet_id=1,
            environment="DEMO",
        ),
        current_user=admin,
        db=db,
    )
    assert demo_doc.id is not None
    assert demo_doc.environment == "DEMO"
    assert demo_doc.verification_status == "UNVERIFIED"

    # Create in REAL
    real_doc = add_manual_knowledge(
        req=ManualKnowledgeCreate(
            title="Official Amit Hospitality Corporate ESG Policy 2026",
            content="Amit Hospitality commits to 100% locally sourced organic farm produce and zero plastic landfill waste by Q4 2026.",
            category="POLICY",
            outlet_id=1,
            environment="REAL",
        ),
        current_user=admin,
        db=db,
    )
    assert real_doc.id is not None
    assert real_doc.environment == "REAL"
    assert real_doc.verification_status == "VERIFIED"
    assert real_doc.verified_by == admin.full_name
    db.close()

# 5. Test Strict Dual Environment Isolation in Search
def test_strict_dual_environment_isolation():
    db = TestingSessionLocal()
    try:
        # Search while in DEMO
        demo_search = search_knowledge(
            q="dress code collared shirts",
            environment="DEMO",
            outlet_id=1,
            db=db,
        )
        assert demo_search.total_hits > 0
        for hit in demo_search.results:
            assert hit.environment == "DEMO"
            assert "ESG" not in hit.content  # Real ESG policy must NOT appear in DEMO

        # Search for REAL content inside DEMO -> must return 0 results
        leakage_check = search_knowledge(
            q="zero plastic landfill waste organic farm produce",
            environment="DEMO",
            outlet_id=1,
            db=db,
        )
        assert leakage_check.total_hits == 0

        # Search while in REAL
        real_search = search_knowledge(
            q="zero plastic landfill waste organic farm produce",
            environment="REAL",
            outlet_id=1,
            db=db,
        )
        assert real_search.total_hits > 0
        for hit in real_search.results:
            assert hit.environment == "REAL"
            assert "organic farm produce" in hit.content
    finally:
        db.close()

# 6. Test Environment Switching & Audit Trail
def test_environment_switch_and_audit():
    db = TestingSessionLocal()
    admin = db.query(User).filter(User.id == 1).first()

    # Switch DEMO -> REAL
    res = switch_environment(
        req=EnvironmentSwitchRequest(
            target_environment="REAL",
            reason="Switching to verified corporate documentation for executive board audit.",
            confirm_acknowledgment=True,
        ),
        current_user=admin,
        db=db,
    )
    assert res["success"] is True
    assert res["active_environment"] == "REAL"

    # Verify active environment endpoint reflects REAL
    active = get_active_environment(db=db)
    assert active["environment"] == "REAL"
    assert active["is_demo"] is False

    # Verify audit log was recorded
    audit = db.query(AuditLog).filter(AuditLog.action == "ENVIRONMENT_SWITCH").order_by(AuditLog.id.desc()).first()
    assert audit is not None
    assert audit.environment == "REAL"
    assert "executive board audit" in audit.details

    # Switch back to DEMO
    switch_back = switch_environment(
        req=EnvironmentSwitchRequest(
            target_environment="DEMO",
            reason="Returning to client presentation demo mode.",
            confirm_acknowledgment=True,
        ),
        current_user=admin,
        db=db,
    )
    assert switch_back["active_environment"] == "DEMO"
    db.close()

# 7. Test Document Status Toggle (Deactivation & Activation)
def test_document_status_toggle():
    db = TestingSessionLocal()
    admin = db.query(User).filter(User.id == 1).first()

    doc = db.query(KnowledgeDocument).first()
    assert doc is not None

    # Deactivate
    updated = toggle_document_status(
        doc_id=doc.id,
        req=DocumentStatusUpdateRequest(is_active=False),
        current_user=admin,
        db=db,
    )
    assert updated.is_active is False

    # Chunks must also be deactivated
    chunks = db.query(KnowledgeChunk).filter(KnowledgeChunk.document_id == doc.id).all()
    for c in chunks:
        assert c.is_active is False

    # Search should no longer return deactivated chunks
    search_res = search_knowledge(
        q="collared shirts",
        environment=doc.environment,
        db=db,
    )
    matching_hits = [h for h in search_res.results if h.document_id == doc.id]
    assert len(matching_hits) == 0

    # Reactivate
    reactivated = toggle_document_status(
        doc_id=doc.id,
        req=DocumentStatusUpdateRequest(is_active=True),
        current_user=admin,
        db=db,
    )
    assert reactivated.is_active is True
    db.close()

# 8. Test Knowledge Stats Aggregate Metrics
def test_knowledge_stats():
    db = TestingSessionLocal()
    stats = get_knowledge_stats(db=db)
    assert stats.demo_doc_count >= 1
    assert stats.real_doc_count >= 1
    assert stats.demo_chunk_count >= 1
    assert stats.real_chunk_count >= 1
    assert stats.verified_docs_count >= 1
    assert stats.unverified_docs_count >= 1
    db.close()

if __name__ == "__main__":
    setup_module()
    try:
        print("[1/8] Testing TXT and CSV extraction...")
        test_txt_and_csv_extraction()
        print("  -> PASSED")

        print("[2/8] Testing semantic chunking with overlap...")
        test_semantic_chunking()
        print("  -> PASSED")

        print("[3/8] Testing embedding & cosine similarity...")
        test_embedding_and_cosine()
        print("  -> PASSED")

        print("[4/8] Testing manual knowledge creation in DEMO and REAL...")
        test_manual_knowledge_creation()
        print("  -> PASSED")

        print("[5/8] Testing STRICT dual environment isolation...")
        test_strict_dual_environment_isolation()
        print("  -> PASSED")

        print("[6/8] Testing environment switching & audit trail...")
        test_environment_switch_and_audit()
        print("  -> PASSED")

        print("[7/8] Testing document deactivation/activation cascade...")
        test_document_status_toggle()
        print("  -> PASSED")

        print("[8/8] Testing knowledge stats metrics...")
        test_knowledge_stats()
        print("  -> PASSED")

        print("\nALL 8 PHASE 3 KNOWLEDGE TESTS PASSED SUCCESSFULLY!")
    finally:
        teardown_module()
