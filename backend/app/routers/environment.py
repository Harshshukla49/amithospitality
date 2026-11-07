from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models.audit import EnvironmentSetting, AuditLog
from app.models.user import User
from app.schemas.knowledge import EnvironmentSwitchRequest
from app.utils.security import require_roles, get_current_user

router = APIRouter(prefix="/api/v1/environment", tags=["Dual Environment Isolation"])

@router.get("/active")
def get_active_environment(db: Session = Depends(get_db)):
    setting = db.query(EnvironmentSetting).order_by(EnvironmentSetting.id.desc()).first()
    active_env = setting.active_environment if setting else "DEMO"
    return {
        "success": True,
        "environment": active_env,
        "is_demo": active_env == "DEMO",
        "last_updated": setting.updated_at if setting else None,
        "switch_reason": setting.switch_reason if setting else None,
        "disclaimer": (
            "DEMO MODE ACTIVE: All menus, pricing, and policies are fictional sample data."
            if active_env == "DEMO"
            else "REAL MODE ACTIVE: Grounded strictly in verified Amit Hospitality corporate documentation."
        ),
    }

@router.post("/switch")
def switch_environment(
    req: EnvironmentSwitchRequest,
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN")),
    db: Session = Depends(get_db),
):
    target = req.target_environment.upper()
    if target not in ["DEMO", "REAL"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid environment specified. Must be either 'DEMO' or 'REAL'."
        )

    if not req.confirm_acknowledgment:
        raise HTTPException(
            status_code=400,
            detail="You must acknowledge the data isolation and AI grounding protocol."
        )

    setting = db.query(EnvironmentSetting).order_by(EnvironmentSetting.id.desc()).first()
    previous_env = setting.active_environment if setting else "DEMO"

    if not setting:
        setting = EnvironmentSetting(
            active_environment=target,
            updated_by_user_id=current_user.id,
            updated_by_name=current_user.full_name,
            switch_reason=req.reason,
        )
        db.add(setting)
    else:
        setting.active_environment = target
        setting.updated_by_user_id = current_user.id
        setting.updated_by_name = current_user.full_name
        setting.switch_reason = req.reason
        setting.updated_at = datetime.utcnow()

    # Create immutable audit log entry
    audit = AuditLog(
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        action="ENVIRONMENT_SWITCH",
        entity_type="ENVIRONMENT_SETTING",
        environment=target,
        details=f"Switched system from {previous_env} to {target}. Reason: {req.reason}",
    )
    db.add(audit)
    db.commit()

    return {
        "success": True,
        "previous_environment": previous_env,
        "active_environment": target,
        "switched_by": current_user.full_name,
        "timestamp": datetime.utcnow().isoformat(),
        "message": f"Successfully switched active knowledge environment to {target} mode.",
    }
