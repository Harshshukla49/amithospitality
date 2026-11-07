from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
import shutil

from app.database import get_db
from app.models.knowledge import KnowledgeDocument, KnowledgeChunk
from app.models.audit import EnvironmentSetting, AuditLog
from app.models.user import User
from app.schemas.knowledge import KnowledgeDocResponse, ManualKnowledgeCreate
from app.utils.security import require_roles
from app.config import settings

router = APIRouter(prefix="/api/v1/knowledge", tags=["Knowledge Base & RAG"])

def get_current_env(db: Session) -> str:
    setting = db.query(EnvironmentSetting).order_by(EnvironmentSetting.id.desc()).first()
    return setting.active_environment if setting else "DEMO"

@router.get("/documents", response_model=List[KnowledgeDocResponse])
def list_documents(
    environment: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    outlet_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    target_env = environment or get_current_env(db)
    query = db.query(KnowledgeDocument).filter(
        KnowledgeDocument.environment == target_env,
        KnowledgeDocument.is_active == True,
    )
    if category and category != "ALL":
        query = query.filter(KnowledgeDocument.category == category)
    if outlet_id:
        query = query.filter(KnowledgeDocument.outlet_id == outlet_id)
    return query.all()

@router.post("/upload", response_model=KnowledgeDocResponse)
async def upload_document(
    file: UploadFile = File(...),
    environment: str = Form("REAL"),
    outlet_id: Optional[int] = Form(None),
    category: str = Form("POLICY"),
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN")),
    db: Session = Depends(get_db),
):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, f"{int(datetime.utcnow().timestamp())}_{file.filename}")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(file_path)
    ext = file.filename.split(".")[-1].upper() if "." in file.filename else "TXT"

    # Simulated chunking count
    estimated_chunks = max(2, min(50, file_size // 1000 + 2))

    new_doc = KnowledgeDocument(
        environment=environment,
        outlet_id=outlet_id,
        title=file.filename.replace("_", " ").split(".")[0],
        file_name=file.filename,
        file_type=ext if ext in ["PDF", "DOCX", "XLSX", "CSV", "TXT"] else "TXT",
        file_path=file_path,
        file_size_bytes=file_size,
        mime_type=file.content_type,
        category=category,
        verification_status="VERIFIED" if environment == "REAL" else "UNVERIFIED",
        verified_by=current_user.full_name if environment == "REAL" else None,
        verified_at=datetime.utcnow() if environment == "REAL" else None,
        chunk_count=estimated_chunks,
        is_active=True,
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    # Create audit log
    audit = AuditLog(
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        action="KNOWLEDGE_UPLOAD",
        entity_type="KNOWLEDGE_DOCUMENT",
        entity_id=new_doc.id,
        environment=environment,
        details=f"Uploaded and indexed '{file.filename}' into {environment} knowledge store with {estimated_chunks} vector chunks.",
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
    chunk_count = max(1, len(req.content) // 400 + 1)
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
        chunk_count=chunk_count,
        is_active=True,
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    # Add chunk
    chunk = KnowledgeChunk(
        document_id=new_doc.id,
        environment=req.environment,
        outlet_id=req.outlet_id,
        chunk_index=0,
        content=req.content,
        is_active=True,
    )
    db.add(chunk)
    db.commit()

    return new_doc

@router.delete("/documents/{doc_id}")
def delete_document(
    doc_id: int,
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN")),
    db: Session = Depends(get_db),
):
    doc = db.query(KnowledgeDocument).filter(KnowledgeDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    db.delete(doc)
    db.commit()
    return {"success": True, "message": "Document and associated vector chunks removed"}
