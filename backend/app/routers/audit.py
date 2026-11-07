import csv
import io
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.audit import AuditLog
from app.models.user import User
from app.utils.security import require_roles

router = APIRouter(prefix="/api/v1/audit", tags=["Audit & Compliance"])

@router.get("/logs")
def get_audit_logs(
    limit: int = Query(50, le=200),
    action: Optional[str] = Query(None),
    environment: Optional[str] = Query(None),
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN")),
    db: Session = Depends(get_db),
):
    query = db.query(AuditLog)
    
    if action is not None and isinstance(action, str) and action != "":
        query = query.filter(AuditLog.action == action)
    if environment is not None and isinstance(environment, str) and environment != "":
        query = query.filter(AuditLog.environment == environment)
        
    actual_limit = limit if isinstance(limit, int) else 50
    logs = query.order_by(AuditLog.created_at.desc()).limit(actual_limit).all()
    
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

@router.get("/export")
def export_audit_logs_csv(
    environment: Optional[str] = Query(None),
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN")),
    db: Session = Depends(get_db),
):
    query = db.query(AuditLog)
    if environment is not None and isinstance(environment, str) and environment != "":
        query = query.filter(AuditLog.environment == environment)
        
    logs = query.order_by(AuditLog.created_at.desc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Timestamp", "Administrator", "Role", "Action", "Entity Type", "Environment", "Details"
    ])
    
    for l in logs:
        ts = l.created_at.isoformat() if l.created_at else ""
        writer.writerow([
            l.id, ts, l.user_name, l.user_role, l.action, l.entity_type, l.environment, l.details
        ])
        
    env_label = environment if isinstance(environment, str) and environment else "all"
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=audit_trail_{env_label.lower()}.csv"},
    )
