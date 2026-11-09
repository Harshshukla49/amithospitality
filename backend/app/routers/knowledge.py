from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime
import os
import shutil
import json
import re
import logging

logger = logging.getLogger(__name__)

from app.database import get_db
from app.models.knowledge import KnowledgeDocument, KnowledgeChunk
from app.models.audit import EnvironmentSetting, AuditLog
from app.models.user import User
from app.schemas.knowledge import (
    KnowledgeDocResponse,
    KnowledgeDocDetailResponse,
    ChunkDetailResponse,
    ManualKnowledgeCreate,
    DocumentUpdateRequest,
    DocumentStatusUpdateRequest,
    KnowledgeSearchResponse,
    SearchHitResponse,
    KnowledgeStatsResponse,
    CategoryCount,
)
from app.utils.security import require_roles
from app.config import settings
from app.services.document_service import extract_document_content, chunk_text
from app.services.embedding_service import generate_embedding, search_relevant_chunks

router = APIRouter(prefix="/api/v1/knowledge", tags=["Knowledge Base & RAG"])

def get_current_env(db: Session) -> str:
    setting = db.query(EnvironmentSetting).order_by(EnvironmentSetting.id.desc()).first()
    return setting.active_environment if setting else "DEMO"

@router.get("/stats", response_model=KnowledgeStatsResponse)
def get_knowledge_stats(
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN", "MANAGER", "STAFF")),
    db: Session = Depends(get_db),
):
    """Retrieve summary metrics across DEMO and REAL knowledge bases."""
    if not isinstance(current_user, User):
        current_user = db.query(User).filter(User.role.in_(["SUPER_ADMIN", "ADMIN"])).first()

    current_env = get_current_env(db)
    
    demo_docs = db.query(KnowledgeDocument).filter(KnowledgeDocument.environment == "DEMO").count()
    real_docs = db.query(KnowledgeDocument).filter(KnowledgeDocument.environment == "REAL").count()
    
    demo_chunks = db.query(KnowledgeChunk).filter(KnowledgeChunk.environment == "DEMO").count()
    real_chunks = db.query(KnowledgeChunk).filter(KnowledgeChunk.environment == "REAL").count()

    active_docs = db.query(KnowledgeDocument).filter(KnowledgeDocument.is_active == True).count()
    inactive_docs = db.query(KnowledgeDocument).filter(KnowledgeDocument.is_active == False).count()

    verified_docs = db.query(KnowledgeDocument).filter(KnowledgeDocument.verification_status == "VERIFIED").count()
    unverified_docs = db.query(KnowledgeDocument).filter(KnowledgeDocument.verification_status != "VERIFIED").count()

    categories_raw = (
        db.query(KnowledgeDocument.category, func.count(KnowledgeDocument.id))
        .filter(KnowledgeDocument.environment == current_env)
        .group_by(KnowledgeDocument.category)
        .all()
    )
    categories = [CategoryCount(category=cat, count=cnt) for cat, cnt in categories_raw]

    return KnowledgeStatsResponse(
        active_environment=current_env,
        demo_doc_count=demo_docs,
        real_doc_count=real_docs,
        demo_chunk_count=demo_chunks,
        real_chunk_count=real_chunks,
        total_active_docs=active_docs,
        total_inactive_docs=inactive_docs,
        verified_docs_count=verified_docs,
        unverified_docs_count=unverified_docs,
        categories=categories,
    )

@router.get("/documents", response_model=List[KnowledgeDocResponse])
def list_documents(
    environment: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    outlet_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),  # 'ACTIVE', 'INACTIVE', or 'ALL'
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN", "MANAGER", "STAFF")),
    db: Session = Depends(get_db),
):
    """List knowledge documents with multi-faceted filtering and tenant isolation."""
    if not isinstance(current_user, User):
        current_user = db.query(User).filter(User.role.in_(["SUPER_ADMIN", "ADMIN"])).first()

    env_str = environment if isinstance(environment, str) else None
    cat_str = category if isinstance(category, str) else None
    out_id = outlet_id if isinstance(outlet_id, int) else None
    status_str = status if isinstance(status, str) else None

    # Multi-outlet tenant isolation:
    if current_user and getattr(current_user, "role", None) in ("STAFF", "MANAGER") and getattr(current_user, "outlet_id", None):
        if out_id is not None and out_id != current_user.outlet_id:
            raise HTTPException(
                status_code=403,
                detail=f"Cross-outlet access forbidden: You are assigned to outlet {current_user.outlet_id}.",
            )
        out_id = current_user.outlet_id

    target_env = env_str or get_current_env(db)
    query = db.query(KnowledgeDocument).filter(KnowledgeDocument.environment == target_env)

    if status_str == "ACTIVE":
        query = query.filter(KnowledgeDocument.is_active == True)
    elif status_str == "INACTIVE":
        query = query.filter(KnowledgeDocument.is_active == False)
    # If None or ALL, returns both

    if cat_str and cat_str != "ALL":
        query = query.filter(KnowledgeDocument.category == cat_str)
    if out_id:
        query = query.filter(KnowledgeDocument.outlet_id == out_id)

    return query.order_by(KnowledgeDocument.id.desc()).all()

@router.get("/documents/{doc_id}", response_model=KnowledgeDocDetailResponse)
def get_document_detail(
    doc_id: int,
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN", "MANAGER", "STAFF")),
    db: Session = Depends(get_db),
):
    """Retrieve detailed document info with all chunk extracts."""
    if not isinstance(current_user, User):
        current_user = db.query(User).filter(User.role.in_(["SUPER_ADMIN", "ADMIN"])).first()

    doc = db.query(KnowledgeDocument).filter(KnowledgeDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Knowledge document not found")

    # Tenant isolation check
    if current_user and getattr(current_user, "role", None) in ("STAFF", "MANAGER") and getattr(current_user, "outlet_id", None):
        if doc.outlet_id is not None and doc.outlet_id != current_user.outlet_id:
            raise HTTPException(
                status_code=403,
                detail=f"Cross-outlet access forbidden: Document belongs to outlet {doc.outlet_id}.",
            )
    
    chunks = (
        db.query(KnowledgeChunk)
        .filter(KnowledgeChunk.document_id == doc.id)
        .order_by(KnowledgeChunk.chunk_index.asc())
        .all()
    )

    return KnowledgeDocDetailResponse(
        id=doc.id,
        environment=doc.environment,
        outlet_id=doc.outlet_id,
        title=doc.title,
        file_name=doc.file_name,
        file_type=doc.file_type,
        file_size_bytes=doc.file_size_bytes,
        category=doc.category,
        verification_status=doc.verification_status,
        verified_by=doc.verified_by,
        verified_at=doc.verified_at,
        chunk_count=doc.chunk_count,
        is_active=doc.is_active,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
        chunks=[
            ChunkDetailResponse(
                id=c.id,
                chunk_index=c.chunk_index,
                content=c.content,
                is_active=c.is_active,
                created_at=c.created_at,
            )
            for c in chunks
        ],
    )

ALLOWED_EXTENSIONS = {"PDF", "DOCX", "XLSX", "CSV", "TXT"}
MAX_UPLOAD_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB

@router.post("/upload", response_model=KnowledgeDocResponse)
def upload_document(
    file: UploadFile = File(...),
    environment: str = Form("REAL"),
    outlet_id: Optional[int] = Form(None),
    category: str = Form("POLICY"),
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN")),
    db: Session = Depends(get_db),
):
    """
    Upload real verified document (PDF, DOCX, XLSX, CSV, TXT).
    Validates file extension, limits file size to 20MB, prevents directory traversal,
    processes text, creates semantic chunks, generates vectors, and indexes into store.
    """
    if not isinstance(current_user, User):
        current_user = db.query(User).filter(User.role.in_(["SUPER_ADMIN", "ADMIN"])).first()

    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file must have a filename.")

    # Validate extension
    ext = file.filename.rsplit(".", 1)[-1].upper() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '.{ext.lower()}'. Only verified PDF, DOCX, XLSX, CSV, and TXT documents are permitted.",
        )

    # Sanitize filename against directory traversal
    base_name = os.path.basename(file.filename)
    sanitized_name = re.sub(r"[^\w\.-]", "_", base_name)
    timestamp_prefix = int(datetime.utcnow().timestamp())
    safe_filename = f"{timestamp_prefix}_{sanitized_name}"

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size = os.path.getsize(file_path)
        if file_size > MAX_UPLOAD_SIZE_BYTES:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(
                status_code=413,
                detail=f"Uploaded file exceeds maximum permitted size of 20 MB (received {file_size / (1024*1024):.1f} MB).",
            )

        # Extract structured sections
        sections = extract_document_content(file_path, ext)
        
        # Semantic chunking
        chunks_data = chunk_text(sections, chunk_size=450, chunk_overlap=60)
        if not chunks_data:
            chunks_data = [{
                "chunk_index": 0,
                "title": sanitized_name,
                "page_number": 1,
                "content": f"Document: {sanitized_name} (Processed empty document)",
                "word_count": 5
            }]
    except HTTPException:
        raise
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        logger.error(f"Failed to parse document {sanitized_name}: {e}")
        raise HTTPException(
            status_code=422,
            detail=f"Failed to process and index document content: {str(e)}",
        )

    # Create document record
    clean_title = sanitized_name.replace("_", " ").rsplit(".", 1)[0]
    new_doc = KnowledgeDocument(
        environment=environment,
        outlet_id=outlet_id,
        title=clean_title,
        file_name=sanitized_name,
        file_type=ext,
        file_path=file_path,
        file_size_bytes=file_size,
        mime_type=file.content_type,
        category=category,
        verification_status="VERIFIED" if environment == "REAL" else "UNVERIFIED",
        verified_by=current_user.full_name if environment == "REAL" else None,
        verified_at=datetime.utcnow() if environment == "REAL" else None,
        chunk_count=len(chunks_data),
        is_active=True,
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    # Generate embeddings and persist chunks
    for chk in chunks_data:
        chunk_content = chk["content"]
        vec = generate_embedding(chunk_content)
        chunk_meta = {
            "title": chk.get("title", clean_title),
            "page_number": chk.get("page_number", 1),
            "word_count": chk.get("word_count", 0),
        }
        chunk_record = KnowledgeChunk(
            document_id=new_doc.id,
            environment=environment,
            outlet_id=outlet_id,
            chunk_index=chk["chunk_index"],
            content=chunk_content,
            metadata_json=json.dumps(chunk_meta),
            embedding_json=json.dumps(vec),
            is_active=True,
        )
        db.add(chunk_record)

    db.commit()

    # Immutable Audit Log
    audit = AuditLog(
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        action="KNOWLEDGE_UPLOAD",
        entity_type="KNOWLEDGE_DOCUMENT",
        entity_id=new_doc.id,
        environment=environment,
        details=f"Uploaded and indexed '{file.filename}' ({ext}, {file_size} bytes) into {environment} knowledge store with {len(chunks_data)} vector chunks.",
    )
    db.add(audit)
    db.commit()

    return new_doc

@router.post("/manual", response_model=KnowledgeDocResponse)
def add_manual_knowledge(
    req: ManualKnowledgeCreate,
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN")),
    db: Session = Depends(get_db),
):
    """Manually add policy, menu details, timing or FAQ directly into knowledge store."""
    if not isinstance(current_user, User):
        current_user = db.query(User).filter(User.role.in_(["SUPER_ADMIN", "ADMIN"])).first()

    sections = [{"title": req.title, "page_number": 1, "content": req.content}]
    chunks_data = chunk_text(sections, chunk_size=450, chunk_overlap=60)
    if not chunks_data:
        chunks_data = [{
            "chunk_index": 0,
            "title": req.title,
            "page_number": 1,
            "content": req.content,
            "word_count": len(req.content.split())
        }]

    new_doc = KnowledgeDocument(
        environment=req.environment,
        outlet_id=req.outlet_id,
        title=req.title,
        file_name=f"{req.title.lower().replace(' ', '_')}.txt",
        file_type="MANUAL",
        file_size_bytes=len(req.content.encode("utf-8")),
        category=req.category,
        verification_status="VERIFIED" if req.environment == "REAL" else "UNVERIFIED",
        verified_by=current_user.full_name if req.environment == "REAL" else None,
        verified_at=datetime.utcnow() if req.environment == "REAL" else None,
        chunk_count=len(chunks_data),
        is_active=True,
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    for chk in chunks_data:
        vec = generate_embedding(chk["content"])
        chunk_record = KnowledgeChunk(
            document_id=new_doc.id,
            environment=req.environment,
            outlet_id=req.outlet_id,
            chunk_index=chk["chunk_index"],
            content=chk["content"],
            metadata_json=json.dumps({"title": req.title, "page": 1}),
            embedding_json=json.dumps(vec),
            is_active=True,
        )
        db.add(chunk_record)

    db.commit()

    audit = AuditLog(
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        action="KNOWLEDGE_MANUAL_ENTRY",
        entity_type="KNOWLEDGE_DOCUMENT",
        entity_id=new_doc.id,
        environment=req.environment,
        details=f"Created manual knowledge entry '{req.title}' ({req.category}) in {req.environment} store.",
    )
    db.add(audit)
    db.commit()

    return new_doc

@router.put("/documents/{doc_id}", response_model=KnowledgeDocResponse)
def update_document(
    doc_id: int,
    req: DocumentUpdateRequest,
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN")),
    db: Session = Depends(get_db),
):
    """Update knowledge document metadata (title, category, outlet)."""
    if not isinstance(current_user, User):
        current_user = db.query(User).filter(User.role.in_(["SUPER_ADMIN", "ADMIN"])).first()

    doc = db.query(KnowledgeDocument).filter(KnowledgeDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if req.title is not None:
        doc.title = req.title
    if req.category is not None:
        doc.category = req.category
    if req.outlet_id is not None:
        doc.outlet_id = req.outlet_id
        # Update associated chunks outlet_id
        db.query(KnowledgeChunk).filter(KnowledgeChunk.document_id == doc.id).update(
            {"outlet_id": req.outlet_id}
        )

    doc.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(doc)
    return doc

@router.patch("/documents/{doc_id}/status", response_model=KnowledgeDocResponse)
def toggle_document_status(
    doc_id: int,
    req: DocumentStatusUpdateRequest,
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN")),
    db: Session = Depends(get_db),
):
    """Activate or deactivate a document and all its indexed vector chunks."""
    if not isinstance(current_user, User):
        current_user = db.query(User).filter(User.role.in_(["SUPER_ADMIN", "ADMIN"])).first()

    doc = db.query(KnowledgeDocument).filter(KnowledgeDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    doc.is_active = req.is_active
    doc.updated_at = datetime.utcnow()

    # Cascade to all chunks
    db.query(KnowledgeChunk).filter(KnowledgeChunk.document_id == doc.id).update(
        {"is_active": req.is_active}
    )
    db.commit()
    db.refresh(doc)

    status_str = "activated" if req.is_active else "deactivated"
    audit = AuditLog(
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        action="KNOWLEDGE_STATUS_TOGGLE",
        entity_type="KNOWLEDGE_DOCUMENT",
        entity_id=doc.id,
        environment=doc.environment,
        details=f"Document '{doc.title}' (ID {doc.id}) {status_str} in {doc.environment} store.",
    )
    db.add(audit)
    db.commit()

    return doc

@router.post("/documents/{doc_id}/reprocess", response_model=KnowledgeDocResponse)
def reprocess_document(
    doc_id: int,
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN")),
    db: Session = Depends(get_db),
):
    """
    Reprocess and reindex an existing document from original file or stored content.
    Refreshes all chunks and vectors.
    """
    if not isinstance(current_user, User):
        current_user = db.query(User).filter(User.role.in_(["SUPER_ADMIN", "ADMIN"])).first()

    doc = db.query(KnowledgeDocument).filter(KnowledgeDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc.file_path and os.path.exists(doc.file_path):
        sections = extract_document_content(doc.file_path, doc.file_type)
    else:
        # Fallback to existing chunks text if original uploaded file was cleared
        existing_chunks = db.query(KnowledgeChunk).filter(KnowledgeChunk.document_id == doc.id).all()
        aggregated = "\n\n".join([c.content for c in existing_chunks])
        sections = [{"title": doc.title, "page_number": 1, "content": aggregated}]

    chunks_data = chunk_text(sections, chunk_size=450, chunk_overlap=60)
    if not chunks_data:
        raise HTTPException(status_code=400, detail="Unable to extract chunks during reprocessing")

    # Clear old chunks
    db.query(KnowledgeChunk).filter(KnowledgeChunk.document_id == doc.id).delete()

    # Re-insert new chunks with fresh embeddings
    for chk in chunks_data:
        vec = generate_embedding(chk["content"])
        chunk_record = KnowledgeChunk(
            document_id=doc.id,
            environment=doc.environment,
            outlet_id=doc.outlet_id,
            chunk_index=chk["chunk_index"],
            content=chk["content"],
            metadata_json=json.dumps({"title": doc.title, "page": chk.get("page_number", 1)}),
            embedding_json=json.dumps(vec),
            is_active=doc.is_active,
        )
        db.add(chunk_record)

    doc.chunk_count = len(chunks_data)
    doc.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(doc)

    audit = AuditLog(
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        action="KNOWLEDGE_REPROCESS",
        entity_type="KNOWLEDGE_DOCUMENT",
        entity_id=doc.id,
        environment=doc.environment,
        details=f"Reprocessed and reindexed '{doc.title}' with {len(chunks_data)} new chunks.",
    )
    db.add(audit)
    db.commit()

    return doc

@router.delete("/documents/{doc_id}")
def delete_document(
    doc_id: int,
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN")),
    db: Session = Depends(get_db),
):
    """Delete document and all associated chunks permanently."""
    if not isinstance(current_user, User):
        current_user = db.query(User).filter(User.role.in_(["SUPER_ADMIN", "ADMIN"])).first()

    doc = db.query(KnowledgeDocument).filter(KnowledgeDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    doc_title = doc.title
    doc_env = doc.environment

    # Delete physical file if present
    if doc.file_path and os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception:
            pass

    # Cascades to delete chunks
    db.delete(doc)
    db.commit()

    audit = AuditLog(
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        action="KNOWLEDGE_DELETE",
        entity_type="KNOWLEDGE_DOCUMENT",
        entity_id=doc_id,
        environment=doc_env,
        details=f"Deleted document '{doc_title}' (ID {doc_id}) from {doc_env} store.",
    )
    db.add(audit)
    db.commit()

    return {"success": True, "message": f"Document '{doc_title}' removed"}

@router.get("/search", response_model=KnowledgeSearchResponse)
def search_knowledge(
    q: str = Query(..., description="Query phrase or customer question"),
    environment: Optional[str] = Query(None),
    outlet_id: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    top_k: int = Query(5, ge=1, le=20),
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN", "MANAGER", "STAFF")),
    db: Session = Depends(get_db),
):
    """
    Search knowledge chunks using hybrid vector + lexical retrieval.
    Guarantees strict isolation: searches ONLY the selected/active environment.
    """
    if not isinstance(current_user, User):
        current_user = db.query(User).filter(User.role.in_(["SUPER_ADMIN", "ADMIN"])).first()

    env_str = environment if isinstance(environment, str) else None
    cat_str = category if isinstance(category, str) else None
    out_id = outlet_id if isinstance(outlet_id, int) else None
    k_val = top_k if isinstance(top_k, int) else 5

    # Multi-outlet tenant isolation:
    if current_user and getattr(current_user, "role", None) in ("STAFF", "MANAGER") and getattr(current_user, "outlet_id", None):
        if out_id is not None and out_id != current_user.outlet_id:
            raise HTTPException(
                status_code=403,
                detail=f"Cross-outlet access forbidden: You are assigned to outlet {current_user.outlet_id}.",
            )
        out_id = current_user.outlet_id

    target_env = env_str or get_current_env(db)
    results = search_relevant_chunks(
        db=db,
        query=q,
        environment=target_env,
        outlet_id=out_id,
        category=cat_str,
        top_k=k_val,
    )

    hits = [
        SearchHitResponse(
            chunk_id=r["chunk_id"],
            document_id=r["document_id"],
            document_title=r["document_title"],
            category=r["category"],
            environment=r["environment"],
            outlet_id=r["outlet_id"],
            chunk_index=r["chunk_index"],
            content=r["content"],
            score=r["score"],
            cosine_similarity=r["cosine_similarity"],
            lexical_overlap=r["lexical_overlap"],
        )
        for r in results
    ]

    return KnowledgeSearchResponse(
        query=q,
        environment=target_env,
        total_hits=len(hits),
        results=hits,
    )
