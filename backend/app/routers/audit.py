from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.audit import AuditLog
from app.models.user import User
from app.utils.security import require_roles

router = APIRouter(prefix="/api/v1/audit", tags=["Audit & Compliance"])

@router.get("/logs")
def get_audit_logs(
    limit: int = Query(50, le=100),
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN")),
    db: Session = Depends(get_db),
):
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
    return [
        {
            "id": l.id,
            "timestamp": l.created_at.isoformat() if l.created_at else "",
            "userName": l.user_name,
            "userRole": l.user_role,
            "action": l.action,
            "entityType": l.entity_type,
            "environment": l.environment,
            "details": l.details,
        }
        for l in logs
    ]
