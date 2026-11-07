from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.outlet import Outlet, MenuItem
from app.models.audit import EnvironmentSetting
from app.models.user import User
from app.schemas.outlet import (
    OutletResponse,
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
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

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
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    db.delete(item)
    db.commit()
    return {"success": True, "message": "Menu item deleted"}
