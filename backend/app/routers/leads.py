from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from typing import List, Optional
import io
import csv

from app.database import get_db
from app.models.lead import Lead
from app.models.outlet import Outlet
from app.models.audit import EnvironmentSetting, AuditLog
from app.models.user import User
from app.schemas.lead import LeadCreate, LeadStatusUpdate, LeadResponse
from app.utils.security import require_roles

router = APIRouter(prefix="/api/v1/leads", tags=["Event & Lead Management"])

def get_current_env(db: Session) -> str:
    setting = db.query(EnvironmentSetting).order_by(EnvironmentSetting.id.desc()).first()
    return setting.active_environment if setting else "DEMO"

@router.post("", response_model=LeadResponse)
def create_lead(req: LeadCreate, db: Session = Depends(get_db)):
    outlet = db.query(Outlet).filter(Outlet.id == req.outlet_id).first()
    if not outlet:
        raise HTTPException(status_code=404, detail="Outlet not found")

    active_env = get_current_env(db)

    new_lead = Lead(
        environment=active_env,
        outlet_id=req.outlet_id,
        outlet_name=outlet.name,
        name=req.name,
        phone=req.phone,
        email=req.email,
        enquiry_type=req.enquiry_type,
        guest_count=req.guest_count,
        target_date=req.target_date,
        budget_range=req.budget_range,
        notes=req.notes,
        status="NEW",
    )
    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)

    audit = AuditLog(
        user_name="Customer / Concierge",
        user_role="CUSTOMER",
        action="LEAD_SUBMISSION",
        entity_type="LEAD",
        entity_id=new_lead.id,
        environment=active_env,
        details=f"New event enquiry #{new_lead.id} ({req.enquiry_type}) submitted for {outlet.name} by {req.name} ({req.guest_count} guests).",
    )
    db.add(audit)
    db.commit()

    return new_lead

@router.get("", response_model=List[LeadResponse])
def list_leads(
    outlet_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    environment: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    target_env = environment if isinstance(environment, str) else get_current_env(db)
    query = db.query(Lead).filter(Lead.environment == target_env)

    if outlet_id and isinstance(outlet_id, int):
        query = query.filter(Lead.outlet_id == outlet_id)
    if status and isinstance(status, str) and status != "ALL":
        query = query.filter(Lead.status == status)

    return query.order_by(Lead.created_at.desc()).all()

@router.patch("/{lead_id}/status", response_model=LeadResponse)
def update_lead_status(
    lead_id: int,
    status_update: LeadStatusUpdate,
    db: Session = Depends(get_db),
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    old_status = lead.status
    lead.status = status_update.status
    if status_update.notes:
        lead.notes = status_update.notes

    audit = AuditLog(
        user_name="Events Manager",
        user_role="MANAGER",
        action="LEAD_STATUS_UPDATE",
        entity_type="LEAD",
        entity_id=lead.id,
        environment=lead.environment,
        details=f"Event Lead #{lead.id} ({lead.name}) status updated: {old_status} -> {status_update.status}.",
    )
    db.add(audit)
    db.commit()
    db.refresh(lead)
    return lead

@router.get("/export")
def export_leads_csv(
    environment: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    target_env = environment if isinstance(environment, str) else get_current_env(db)
    leads = db.query(Lead).filter(Lead.environment == target_env).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Environment", "Outlet", "Name", "Phone", "Email",
        "Enquiry Type", "Guest Count", "Target Date", "Budget", "Status", "Notes"
    ])

    for l in leads:
        writer.writerow([
            l.id, l.environment, l.outlet_name, l.name, l.phone,
            l.email, l.enquiry_type, l.guest_count, l.target_date,
            l.budget_range, l.status, l.notes or ""
        ])

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=leads_{target_env.lower()}.csv"},
    )
