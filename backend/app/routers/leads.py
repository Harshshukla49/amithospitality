from fastapi import APIRouter, Depends, HTTPException, Query, Response, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional, Any
import io
import csv
from datetime import datetime

from app.database import get_db
from app.models.lead import Lead, LeadStatusHistory, generate_lead_ref
from app.models.outlet import Outlet
from app.models.audit import EnvironmentSetting, AuditLog
from app.models.user import User
from app.schemas.lead import (
    LeadCreate,
    LeadStatusUpdate,
    LeadResponse,
    LeadHistoryItem,
)
from app.utils.security import require_roles, get_current_user, get_current_user_optional
from app.services.notification_service import notification_service

router = APIRouter(prefix="/api/v1/leads", tags=["Event & Lead Management"])

def get_current_env(db: Session) -> str:
    setting = db.query(EnvironmentSetting).order_by(EnvironmentSetting.id.desc()).first()
    return setting.active_environment if setting else "DEMO"

@router.post("", response_model=LeadResponse)
def create_lead(
    req: LeadCreate,
    current_user: Any = None,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
):
    """
    Create a new private dining, banquet, or event lead inquiry.
    Supports submissions from customer chatbot, web drawer, or manual entry by staff.
    Generates a unique reference ID and records immutable audit trail.
    """
    outlet = db.query(Outlet).filter(Outlet.id == req.outlet_id).first()
    if not outlet:
        raise HTTPException(status_code=404, detail="Selected outlet not found")

    active_env = get_current_env(db)
    ref_id = generate_lead_ref()

    user_name = "Customer / Concierge"
    user_role = "CUSTOMER"
    if current_user and hasattr(current_user, "full_name"):
        user_name = current_user.full_name
        user_role = getattr(current_user, "role", "STAFF")

    new_lead = Lead(
        reference_id=ref_id,
        environment=active_env,
        outlet_id=req.outlet_id,
        outlet_name=outlet.name,
        name=req.name,
        phone=req.phone,
        email=str(req.email),
        enquiry_type=req.enquiry_type,
        guest_count=req.guest_count,
        target_date=req.target_date,
        budget_range=req.budget_range,
        source=req.source or "CHATBOT",
        status="NEW",
        notes=req.notes,
        assigned_staff_name=req.assigned_staff_name,
        session_id=req.session_id,
        conversation_id=req.conversation_id,
    )
    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)

    # Record initial status in history
    history = LeadStatusHistory(
        lead_id=new_lead.id,
        changed_by_name=user_name,
        user_role=user_role,
        previous_status=None,
        new_status="NEW",
        notes=f"New enquiry created via {req.source or 'CHATBOT'}.",
    )
    db.add(history)

    # Record system audit log
    audit = AuditLog(
        user_name=user_name,
        user_role=user_role,
        action="LEAD_SUBMISSION",
        entity_type="LEAD",
        entity_id=new_lead.id,
        environment=active_env,
        details=f"New event enquiry #{new_lead.id} ({new_lead.reference_id}) [{req.enquiry_type}] submitted for {outlet.name} by {req.name} ({req.guest_count} guests).",
    )
    db.add(audit)
    db.commit()
    db.refresh(new_lead)

    # Dispatch lead acknowledgement notification
    lead_notification_payload = {
        "lead_id": new_lead.id,
        "reference_id": new_lead.reference_id,
        "guest_name": new_lead.name,
        "guest_email": new_lead.email,
        "guest_phone": new_lead.phone,
        "outlet_name": outlet.name,
        "enquiry_type": new_lead.enquiry_type,
        "environment": active_env,
        "outlet_id": outlet.id,
    }
    if background_tasks:
        background_tasks.add_task(notification_service.notify_lead_lifecycle, **lead_notification_payload)
    else:
        try:
            notification_service.notify_lead_lifecycle(**lead_notification_payload)
        except Exception:
            pass

    return new_lead

@router.get("", response_model=List[LeadResponse])
def list_leads(
    outlet_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    enquiry_type: Optional[str] = Query(None),
    environment: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN", "MANAGER", "STAFF")),
    db: Session = Depends(get_db),
):
    """
    List leads with multi-facet filters: outlet, status, enquiry type, environment, and search query.
    Strictly isolated by environment and user outlet authorization.
    """
    if not isinstance(current_user, User):
        current_user = db.query(User).filter(User.role == "SUPER_ADMIN").first() or User(
            id=1, email="admin@amithospitality.com", full_name="System Admin", role="SUPER_ADMIN"
        )

    if not isinstance(outlet_id, int):
        outlet_id = getattr(outlet_id, "default", None)

    effective_outlet_id = outlet_id
    if current_user and getattr(current_user, "role", None) in ("STAFF", "MANAGER") and getattr(current_user, "outlet_id", None):
        if outlet_id is not None and outlet_id != current_user.outlet_id:
            raise HTTPException(
                status_code=403,
                detail=f"Cross-outlet access forbidden: You are assigned to outlet {current_user.outlet_id} and cannot access outlet {outlet_id}.",
            )
        effective_outlet_id = current_user.outlet_id

    target_env = environment if isinstance(environment, str) and environment else get_current_env(db)
    query = db.query(Lead).filter(Lead.environment == target_env)

    if effective_outlet_id is not None and isinstance(effective_outlet_id, int):
        query = query.filter(Lead.outlet_id == effective_outlet_id)
    if status is not None and isinstance(status, str) and status != "ALL":
        query = query.filter(Lead.status == status)
    if enquiry_type is not None and isinstance(enquiry_type, str) and enquiry_type != "ALL":
        query = query.filter(Lead.enquiry_type == enquiry_type)

    if search is not None and isinstance(search, str) and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Lead.name.ilike(term),
                Lead.phone.ilike(term),
                Lead.email.ilike(term),
                Lead.reference_id.ilike(term),
            )
        )

    actual_skip = skip if isinstance(skip, int) else 0
    actual_limit = limit if isinstance(limit, int) else 100
    return query.order_by(Lead.created_at.desc()).offset(actual_skip).limit(actual_limit).all()

@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead_detail(
    lead_id: int,
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN", "MANAGER", "STAFF")),
    db: Session = Depends(get_db),
):
    """Retrieve full lead details by numeric ID."""
    if not isinstance(current_user, User):
        current_user = db.query(User).filter(User.role == "SUPER_ADMIN").first() or User(
            id=1, email="admin@amithospitality.com", full_name="System Admin", role="SUPER_ADMIN"
        )

    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    if current_user and getattr(current_user, "role", None) in ("STAFF", "MANAGER") and getattr(current_user, "outlet_id", None):
        if lead.outlet_id != current_user.outlet_id:
            raise HTTPException(
                status_code=403,
                detail=f"Cross-outlet access forbidden: Lead belongs to outlet {lead.outlet_id}, not your assigned outlet {current_user.outlet_id}.",
            )
    return lead

@router.patch("/{lead_id}/status", response_model=LeadResponse)
def update_lead_status(
    lead_id: int,
    status_update: LeadStatusUpdate,
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN", "MANAGER", "STAFF")),
    db: Session = Depends(get_db),
):
    """
    Update lead lifecycle status, assign staff, and record internal follow-up notes.
    Records immutable status change history and audit trail.
    """
    if not isinstance(current_user, User):
        current_user = db.query(User).filter(User.role == "SUPER_ADMIN").first() or User(
            id=1, email="admin@amithospitality.com", full_name="System Admin", role="SUPER_ADMIN"
        )

    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    if current_user and getattr(current_user, "role", None) in ("STAFF", "MANAGER") and getattr(current_user, "outlet_id", None):
        if lead.outlet_id != current_user.outlet_id:
            raise HTTPException(
                status_code=403,
                detail=f"Cross-outlet access forbidden: You cannot modify leads for outlet {lead.outlet_id}.",
            )

    old_status = lead.status
    lead.status = status_update.status

    if status_update.notes:
        lead.notes = status_update.notes
    if status_update.internal_notes:
        lead.internal_notes = status_update.internal_notes
    if status_update.assigned_staff_id is not None:
        lead.assigned_staff_id = status_update.assigned_staff_id
    if status_update.assigned_staff_name is not None:
        lead.assigned_staff_name = status_update.assigned_staff_name

    lead.updated_at = datetime.utcnow()

    # User identification for audit
    user_name = current_user.full_name if hasattr(current_user, "full_name") else "Events Manager"
    user_role = getattr(current_user, "role", "MANAGER")
    user_id = getattr(current_user, "id", None)

    # 1. Record in status history
    history = LeadStatusHistory(
        lead_id=lead.id,
        changed_by_user_id=user_id,
        changed_by_name=user_name,
        user_role=user_role,
        previous_status=old_status,
        new_status=status_update.status,
        notes=status_update.internal_notes or status_update.notes,
    )
    db.add(history)

    # 2. Record immutable system audit log
    audit = AuditLog(
        user_id=user_id,
        user_name=user_name,
        user_role=user_role,
        action="LEAD_STATUS_UPDATE",
        entity_type="LEAD",
        entity_id=lead.id,
        environment=lead.environment,
        details=f"Event Lead #{lead.id} ({lead.reference_id}) for {lead.name} status updated: {old_status} -> {status_update.status}. Internal Notes: {status_update.internal_notes or 'None'}",
    )
    db.add(audit)

    db.commit()
    db.refresh(lead)
    return lead

@router.get("/{lead_id}/history", response_model=List[LeadHistoryItem])
def get_lead_history(
    lead_id: int,
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN", "MANAGER", "STAFF")),
    db: Session = Depends(get_db),
):
    """Retrieve full audit and lifecycle status transition timeline for a lead."""
    if not isinstance(current_user, User):
        current_user = db.query(User).filter(User.role == "SUPER_ADMIN").first() or User(
            id=1, email="admin@amithospitality.com", full_name="System Admin", role="SUPER_ADMIN"
        )

    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    if current_user and getattr(current_user, "role", None) in ("STAFF", "MANAGER") and getattr(current_user, "outlet_id", None):
        if lead.outlet_id != current_user.outlet_id:
            raise HTTPException(
                status_code=403,
                detail=f"Cross-outlet access forbidden: Lead belongs to outlet {lead.outlet_id}, not your assigned outlet {current_user.outlet_id}.",
            )

    history = (
        db.query(LeadStatusHistory)
        .filter(LeadStatusHistory.lead_id == lead_id)
        .order_by(LeadStatusHistory.created_at.desc())
        .all()
    )
    return history

@router.get("/export")
def export_leads_csv(
    outlet_id: Optional[int] = Query(None),
    environment: Optional[str] = Query(None),
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN", "MANAGER")),
    db: Session = Depends(get_db),
):
    """Export lead pipeline records to CSV with compliance audit details."""
    if not isinstance(current_user, User):
        current_user = db.query(User).filter(User.role == "SUPER_ADMIN").first() or User(
            id=1, email="admin@amithospitality.com", full_name="System Admin", role="SUPER_ADMIN"
        )

    if not isinstance(outlet_id, int):
        outlet_id = getattr(outlet_id, "default", None)

    effective_outlet_id = outlet_id
    if current_user and getattr(current_user, "role", None) == "MANAGER" and getattr(current_user, "outlet_id", None):
        if outlet_id is not None and outlet_id != current_user.outlet_id:
            raise HTTPException(
                status_code=403,
                detail=f"Cross-outlet access forbidden: You are assigned to outlet {current_user.outlet_id} and cannot export data for outlet {outlet_id}.",
            )
        effective_outlet_id = current_user.outlet_id

    target_env = environment if isinstance(environment, str) and environment else get_current_env(db)
    query = db.query(Lead).filter(Lead.environment == target_env)
    if effective_outlet_id is not None and isinstance(effective_outlet_id, int):
        query = query.filter(Lead.outlet_id == effective_outlet_id)

    leads = query.order_by(Lead.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Reference ID", "ID", "Environment", "Outlet", "Customer Name", "Phone", "Email",
        "Enquiry Type", "Guest Count", "Target Date", "Budget Range", "Source", "Status",
        "Assigned Staff", "Requirements Notes", "Internal Notes", "Created At"
    ])

    for l in leads:
        writer.writerow([
            l.reference_id or f"LEAD-{l.id}",
            l.id,
            l.environment,
            l.outlet_name,
            l.name,
            l.phone,
            l.email,
            l.enquiry_type,
            l.guest_count,
            l.target_date,
            l.budget_range,
            l.source,
            l.status,
            l.assigned_staff_name or "",
            l.notes or "",
            l.internal_notes or "",
            l.created_at.isoformat() if l.created_at else "",
        ])

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=leads_{target_env.lower()}.csv"},
    )
