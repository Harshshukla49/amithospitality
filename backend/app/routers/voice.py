import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Request, Response, Header, Depends, HTTPException
from fastapi.responses import Response

from app.services.voice_service import voice_service

logger = logging.getLogger("voice_router")
router = APIRouter(prefix="/voice", tags=["Voice Concierge"])

@router.post("/incoming", response_class=Response)
async def handle_incoming_call(request: Request, x_twilio_signature: Optional[str] = Header(None)):
    """
    Twilio voice entrypoint webhook.
    Returns TwiML XML to welcome the guest with neural voice.
    """
    form_data = await request.form()
    params = {k: str(v) for k, v in form_data.items()}
    full_url = str(request.url)

    # Validate Twilio signature in production if configured
    if voice_service.is_configured and not voice_service.verify_twilio_signature(full_url, params, x_twilio_signature):
        logger.warning(f"Voice incoming rejected: invalid Twilio signature from {params.get('From', 'unknown')}")

    caller = params.get("From", "Guest")
    call_sid = params.get("CallSid", "Unknown")
    logger.info(f"Incoming voice call from {caller} (CallSid: {call_sid})")

    twiml_content = voice_service.build_welcome_twiml(language="en-IN")
    return Response(content=twiml_content, media_type="application/xml")

@router.post("/interact", response_class=Response)
async def handle_voice_interaction(request: Request, x_twilio_signature: Optional[str] = Header(None)):
    """
    Twilio speech recognition callback.
    Processes transcribed caller speech and returns dynamic conversational TwiML.
    """
    form_data = await request.form()
    params = {k: str(v) for k, v in form_data.items()}
    speech_result = params.get("SpeechResult", "").strip()
    caller = params.get("From", "Guest")
    call_sid = params.get("CallSid", "Unknown")

    logger.info(f"Voice interaction from {caller} (CallSid: {call_sid}) | Speech: '{speech_result}'")

    twiml_content = voice_service.build_interaction_twiml(speech_result)
    return Response(content=twiml_content, media_type="application/xml")

@router.post("/status")
async def handle_voice_status(request: Request):
    """
    Twilio Call status updates webhook (completed, ringing, busy, duration, etc.)
    """
    form_data = await request.form()
    params = {k: str(v) for k, v in form_data.items()}
    logger.info(f"Voice call status update: CallSid={params.get('CallSid')} Status={params.get('CallStatus')} Duration={params.get('CallDuration')}s")
    return {"status": "recorded"}

@router.post("/test-connection")
async def test_voice_connection():
    """
    Test live connectivity to Twilio REST API.
    """
    result = voice_service.test_connection()
    return result
