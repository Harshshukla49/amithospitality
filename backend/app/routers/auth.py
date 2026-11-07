from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    UserResponse,
    UserCreate,
    PasswordResetRequest,
)
from app.utils.security import (
    verify_password,
    hash_password,
    create_access_token,
    create_refresh_token,
    get_current_user,
    require_roles,
)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication & RBAC"])

@router.post("/login", response_model=TokenResponse)
def login(creds: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == creds.email, User.is_active == True).first()
    if not user or not verify_password(creds.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "name": user.full_name}
    )
    refresh_token = create_refresh_token(data={"sub": user.email})

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        refresh_token=refresh_token,
        role=user.role,
        full_name=user.full_name,
        email=user.email,
    )

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    # In JWT stateless auth, client discards token; optionally token can be blacklisted
    return {"success": True, "message": "Successfully logged out"}

@router.post("/reset-password")
def reset_password(
    req: PasswordResetRequest,
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN")),
    db: Session = Depends(get_db),
):
    target_user = db.query(User).filter(User.email == req.email).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User account not found")

    target_user.password_hash = hash_password(req.new_password)
    db.commit()
    return {"success": True, "message": f"Password reset for {target_user.email}"}

@router.get("/users", response_model=List[UserResponse])
def list_users(
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
    db: Session = Depends(get_db),
):
    return db.query(User).all()

@router.post("/users", response_model=UserResponse)
def create_user(
    req: UserCreate,
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
    db: Session = Depends(get_db),
):
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    new_user = User(
        email=req.email,
        password_hash=hash_password(req.password),
        full_name=req.full_name,
        role=req.role,
        outlet_id=req.outlet_id,
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
