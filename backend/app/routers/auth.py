from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm.exc import FlushError
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models.user import User
from app.models.token import RevokedToken
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    UserResponse,
    UserCreate,
    PasswordResetRequest,
    RefreshTokenRequest,
)
from app.utils.security import (
    verify_password,
    hash_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    require_roles,
    oauth2_scheme,
    validate_password_policy,
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

@router.post("/refresh", response_model=TokenResponse)
def refresh_token_endpoint(req: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Exchange valid refresh token for a newly issued access token.
    Validates token signature, expiration, token type == 'refresh', and active user status.
    """
    payload = decode_token(req.refresh_token)
    token_type = payload.get("type")
    if token_type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type for refresh. Expected refresh token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token subject invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.email == email, User.is_active == True).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account no longer active or found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Replay protection & Token rotation check
    jti = payload.get("jti")
    if jti:
        already_revoked = db.query(RevokedToken).filter(RevokedToken.jti == jti).first()
        if already_revoked:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has already been consumed or revoked (token replay protection).",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Mark the presented refresh token as rotated / revoked
        exp_ts = payload.get("exp")
        exp_dt = datetime.utcfromtimestamp(exp_ts) if exp_ts else datetime.utcnow() + timedelta(days=7)
        db.add(RevokedToken(
            jti=jti,
            token_type="refresh",
            user_id=user.id,
            expires_at=exp_dt,
            revoked_at=datetime.utcnow(),
            revocation_reason="ROTATED",
        ))
        try:
            db.commit()
        except (IntegrityError, FlushError, SQLAlchemyError):
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has already been consumed or revoked (concurrent replay detected).",
                headers={"WWW-Authenticate": "Bearer"},
            )

    new_access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "name": user.full_name}
    )
    new_refresh_token = create_refresh_token(data={"sub": user.email})

    return TokenResponse(
        access_token=new_access_token,
        token_type="bearer",
        refresh_token=new_refresh_token,
        role=user.role,
        full_name=user.full_name,
        email=user.email,
    )

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/logout")
def logout(
    token: str = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Revoke caller's access token and blacklist its JTI to prevent reuse.
    """
    try:
        payload = decode_token(token)
        jti = payload.get("jti")
        if jti:
            exp_ts = payload.get("exp")
            exp_dt = datetime.utcfromtimestamp(exp_ts) if exp_ts else datetime.utcnow() + timedelta(hours=24)
            db.add(RevokedToken(
                jti=jti,
                token_type="access",
                user_id=current_user.id,
                expires_at=exp_dt,
                revoked_at=datetime.utcnow(),
                revocation_reason="LOGOUT",
            ))
            db.commit()
    except Exception:
        pass
    return {"success": True, "message": "Successfully logged out and session revoked"}

@router.post("/reset-password")
def reset_password(
    req: PasswordResetRequest,
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN")),
    db: Session = Depends(get_db),
):
    validate_password_policy(req.new_password)
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
    validate_password_policy(req.password)
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
