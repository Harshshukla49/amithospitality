from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any

from app.database import get_db
from app.schemas.guest import (
    GuestLookupRequest,
    GuestLookupResponse,
    GuestVerifyOtpRequest,
    GuestVerifyOtpResponse,
    GuestReservationModifyRequest,
    GuestReservationCancelRequest,
)
from app.services.guest_self_service import guest_self_service
from app.utils.security import decode_token

router = APIRouter(prefix="/api/v1/guest/reservations", tags=["Guest Self-Service Portal"])

def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"

def verify_guest_session_token(
    reference_id: str,
    authorization: Optional[str] = Header(None),
) -> Dict[str, Any]:
    """
    Validate that caller has a valid, unexpired short-lived guest access token
    specifically scoped to this reservation reference ID.
    Prevents cross-guest enumeration and unauthorized modifications.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Guest authentication required. Please verify your reservation via OTP.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization.split(" ")[1]
    payload = decode_token(token)

    token_type = payload.get("type")
    token_ref = payload.get("ref")

    if token_type != "guest_access" or token_ref != reference_id:
        raise HTTPException(
            status_code=403,
            detail="Access forbidden: This verification session does not permit access to this booking.",
        )
    return payload

@router.post("/lookup", response_model=GuestLookupResponse)
def lookup_booking(
    req: GuestLookupRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Initiate guest self-service verification.
    Validates booking reference and contact match, rate-limits attempts,
    and dispatches a 6-digit expiring OTP to registered contact.
    """
    ip_addr = get_client_ip(request)
    u_agent = request.headers.get("User-Agent")
    return guest_self_service.request_verification(
        db=db,
        reference_id=req.reference_id,
        contact=req.contact,
        ip_address=ip_addr,
        user_agent=u_agent,
    )

@router.post("/verify-otp", response_model=GuestVerifyOtpResponse)
def verify_otp(
    req: GuestVerifyOtpRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Verify single-use 6-digit OTP code.
    Upon successful validation, issues a 30-minute signed guest session JWT.
    """
    ip_addr = get_client_ip(request)
    u_agent = request.headers.get("User-Agent")
    return guest_self_service.verify_otp_and_issue_token(
        db=db,
        reference_id=req.reference_id,
        otp=req.otp,
        ip_address=ip_addr,
        user_agent=u_agent,
    )

@router.get("/{reference_id}")
def get_reservation_details(
    reference_id: str,
    db: Session = Depends(get_db),
    guest_session: Dict[str, Any] = Depends(verify_guest_session_token),
):
    """
    Retrieve reservation details, outlet policies, and permitted self-service actions.
    Requires verified guest session token for the matching reference ID.
    """
    return guest_self_service.get_verified_reservation(db=db, reference_id=reference_id)

@router.patch("/{reference_id}/modify")
def modify_reservation(
    reference_id: str,
    req: GuestReservationModifyRequest,
    db: Session = Depends(get_db),
    guest_session: Dict[str, Any] = Depends(verify_guest_session_token),
):
    """
    Self-service booking modification for verified guests.
    Re-validates outlet operating hours and table capacity within a locked transaction.
    If party size changes significantly, flags for restaurant manager approval.
    """
    return guest_self_service.modify_verified_reservation(
        db=db,
        reference_id=reference_id,
        req=req,
    )

@router.post("/{reference_id}/cancel")
def cancel_reservation(
    reference_id: str,
    req: GuestReservationCancelRequest,
    db: Session = Depends(get_db),
    guest_session: Dict[str, Any] = Depends(verify_guest_session_token),
):
    """
    Self-service cancellation for verified guests.
    Enforces cancellation policy, transitions lifecycle state, and notifies guest.
    """
    return guest_self_service.cancel_verified_reservation(
        db=db,
        reference_id=reference_id,
        reason=req.cancellation_reason,
    )
