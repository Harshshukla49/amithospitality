from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.outlet import Outlet, MenuItem
from app.models.audit import EnvironmentSetting, AuditLog
from app.models.user import User
from app.schemas.outlet import (
    OutletResponse,
    OutletUpdate,
    MenuItemResponse,
    MenuItemCreate,
    MenuItemUpdate,
)
from app.utils.security import require_roles

router = APIRouter(prefix="/api/v1", tags=["Outlets & Menus"])

def get_current_env(db: Session) -> str:
    setting = db.query(EnvironmentSetting).order_by(EnvironmentSetting.id.desc()).first()
    return setting.active_environment if setting else "DEMO"

@router.get("/outlets", response_model=List[OutletResponse])
def list_outlets(db: Session = Depends(get_db)):
    return db.query(Outlet).filter(Outlet.is_active == True).all()

@router.get("/outlets/{outlet_id}", response_model=OutletResponse)
def get_outlet(outlet_id: int, db: Session = Depends(get_db)):
    outlet = db.query(Outlet).filter(Outlet.id == outlet_id, Outlet.is_active == True).first()
    if not outlet:
        raise HTTPException(status_code=404, detail="Outlet not found")
    return outlet

@router.put("/outlets/{outlet_id}", response_model=OutletResponse)
def update_outlet(
    outlet_id: int,
    outlet_in: OutletUpdate,
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN", "MANAGER")),
    db: Session = Depends(get_db),
):
    if not isinstance(current_user, User):
        current_user = db.query(User).filter(User.role.in_(["SUPER_ADMIN", "ADMIN"])).first()

    # IDOR Prevention: Outlet Manager can only edit their assigned outlet
    if current_user and getattr(current_user, "role", None) == "MANAGER" and getattr(current_user, "outlet_id", None):
        if outlet_id != current_user.outlet_id:
            raise HTTPException(
                status_code=403,
                detail=f"Cross-outlet tampering forbidden: You are assigned to outlet {current_user.outlet_id} and cannot modify outlet {outlet_id}.",
            )

    outlet = db.query(Outlet).filter(Outlet.id == outlet_id).first()
    if not outlet:
        raise HTTPException(status_code=404, detail="Outlet not found")

    update_data = outlet_in.dict(exclude_unset=True)
    for field, val in update_data.items():
        setattr(outlet, field, val)

    audit = AuditLog(
        user_name=current_user.full_name if current_user else "System Admin",
        user_role=current_user.role if current_user else "SUPER_ADMIN",
        action="OUTLET_UPDATED",
        entity_type="OUTLET",
        entity_id=outlet.id,
        environment=get_current_env(db),
        details=f"Outlet '{outlet.name}' (ID: {outlet.id}) updated: {', '.join(update_data.keys())}",
    )
    db.add(audit)
    db.commit()
    db.refresh(outlet)
    return outlet

@router.get("/menus", response_model=List[MenuItemResponse])
def get_menus(
    outlet_id: Optional[int] = None,
    environment: Optional[str] = None,
    db: Session = Depends(get_db),
):
    active_env = environment or get_current_env(db)
    query = db.query(MenuItem).filter(MenuItem.environment == active_env, MenuItem.is_available == True)
    if outlet_id:
        query = query.filter(MenuItem.outlet_id == outlet_id)
    return query.all()

@router.post("/menus/items", response_model=MenuItemResponse)
def create_menu_item(
    item_in: MenuItemCreate,
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN", "MANAGER")),
    db: Session = Depends(get_db),
):
    if not isinstance(current_user, User):
        current_user = db.query(User).filter(User.role.in_(["SUPER_ADMIN", "ADMIN"])).first()

    # IDOR Prevention: Outlet Manager can only create items for their assigned outlet
    if current_user and getattr(current_user, "role", None) == "MANAGER" and getattr(current_user, "outlet_id", None):
        if item_in.outlet_id != current_user.outlet_id:
            raise HTTPException(
                status_code=403,
                detail=f"Cross-outlet tampering forbidden: You are assigned to outlet {current_user.outlet_id} and cannot create menu items for outlet {item_in.outlet_id}.",
            )

    active_env = item_in.environment or get_current_env(db)
    new_item = MenuItem(
        outlet_id=item_in.outlet_id,
        category_id=item_in.category_id,
        environment=active_env,
        name=item_in.name,
        description=item_in.description,
        price=item_in.price,
        currency=item_in.currency,
        dietary_flags=item_in.dietary_flags,
        is_available=item_in.is_available,
        is_signature=item_in.is_signature,
        display_order=item_in.display_order,
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@router.put("/menus/items/{item_id}", response_model=MenuItemResponse)
def update_menu_item(
    item_id: int,
    item_update: MenuItemUpdate,
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN", "MANAGER")),
    db: Session = Depends(get_db),
):
    if not isinstance(current_user, User):
        current_user = db.query(User).filter(User.role.in_(["SUPER_ADMIN", "ADMIN"])).first()

    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    # IDOR Prevention: Outlet Manager can only modify items for their assigned outlet
    if current_user and getattr(current_user, "role", None) == "MANAGER" and getattr(current_user, "outlet_id", None):
        if item.outlet_id != current_user.outlet_id:
            raise HTTPException(
                status_code=403,
                detail=f"Cross-outlet tampering forbidden: Menu item {item_id} belongs to outlet {item.outlet_id}, but you are assigned to outlet {current_user.outlet_id}.",
            )

    if item_update.price is not None:
        item.price = item_update.price
    if item_update.is_available is not None:
        item.is_available = item_update.is_available
    if item_update.description is not None:
        item.description = item_update.description
    if item_update.name is not None:
        item.name = item_update.name

    db.commit()
    db.refresh(item)
    return item

@router.delete("/menus/items/{item_id}")
def delete_menu_item(
    item_id: int,
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN", "MANAGER")),
    db: Session = Depends(get_db),
):
    if not isinstance(current_user, User):
        current_user = db.query(User).filter(User.role.in_(["SUPER_ADMIN", "ADMIN"])).first()

    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    # IDOR Prevention: Outlet Manager can only delete items for their assigned outlet
    if current_user and getattr(current_user, "role", None) == "MANAGER" and getattr(current_user, "outlet_id", None):
        if item.outlet_id != current_user.outlet_id:
            raise HTTPException(
                status_code=403,
                detail=f"Cross-outlet tampering forbidden: Menu item {item_id} belongs to outlet {item.outlet_id}, but you are assigned to outlet {current_user.outlet_id}.",
            )

    db.delete(item)
    db.commit()
    return {"success": True, "message": "Menu item deleted"}
