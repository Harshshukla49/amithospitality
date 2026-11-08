from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.database import Base

class RevokedToken(Base):
    """
    Tracks rotated, revoked, and blacklisted JWT tokens (access and refresh tokens).
    Provides replay-attack detection and explicit session revocation across server restarts.
    """
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String(255), unique=True, index=True, nullable=False)
    token_type = Column(String(50), default="refresh", nullable=False)  # "refresh" or "access"
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    expires_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    revocation_reason = Column(String(255), default="ROTATED", nullable=False)  # "ROTATED", "LOGOUT", "REPLAY_DETECTED"
