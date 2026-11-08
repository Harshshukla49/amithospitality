import time
import re
import html
import uuid
from typing import Dict, List, Tuple
from starlette.datastructures import MutableHeaders
from starlette.responses import JSONResponse

# --- 1. PROMPT INJECTION & INPUT SANITIZATION ---

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|rules)",
    r"(reveal|print|show|output|leak)\s+(your\s+)?(system\s+prompt|initial\s+prompt|hidden\s+instructions)",
    r"you\s+are\s+now\s+(in\s+)?(developer\s+mode|dan\s+mode|unrestricted|god\s+mode)",
    r"jailbreak",
    r"bypass\s+(safety|content|operational)\s+guidelines",
    r"disregard\s+(all\s+)?(safety|rules|instructions)",
    r"forget\s+(all\s+)?(prior|previous)\s+(context|rules|instructions|prompts)",
]

COMPILED_INJECTION_REGEX = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]

def detect_prompt_injection(text: str) -> bool:
    """Return True if text matches known adversarial prompt injection patterns."""
    if not text:
        return False
    return any(rx.search(text) for rx in COMPILED_INJECTION_REGEX)

def sanitize_input_text(text: str) -> str:
    """
    Sanitize text input by removing dangerous HTML/script tags and control characters,
    while preserving natural guest queries and international Unicode characters.
    """
    if not text:
        return ""
    # Strip dangerous HTML tags
    cleaned = re.sub(r"<\s*(script|iframe|object|embed|style|meta)[^>]*>.*?<\s*/\s*\1\s*>", "", text, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r"<\s*(script|iframe|object|embed|style|meta|input|form)[^>]*>", "", cleaned, flags=re.IGNORECASE)
    # Strip null bytes and non-printable control chars except standard whitespace
    cleaned = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", cleaned)
    return cleaned.strip()


# --- 2. SECURITY HEADERS ASGI MIDDLEWARE ---

class SecurityHeadersMiddleware:
    """
    Pure ASGI middleware injecting enterprise security headers and request correlation IDs.
    Protects against MIME-sniffing, XSS, unauthorized clickjacking, and facilitates distributed tracing.
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Extract or generate unique correlation Request ID
        request_id = None
        for h_name, h_val in scope.get("headers", []):
            if h_name.lower() == b"x-request-id":
                request_id = h_val.decode("latin1").strip()
                break
        if not request_id:
            request_id = f"req_{uuid.uuid4().hex[:16]}"

        if "state" not in scope:
            scope["state"] = {}
        scope["state"]["request_id"] = request_id

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers["X-Request-ID"] = request_id
                headers["X-Content-Type-Options"] = "nosniff"
                headers["X-Frame-Options"] = "SAMEORIGIN"
                headers["X-XSS-Protection"] = "1; mode=block"
                headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
                headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
                headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
                headers["Content-Security-Policy"] = (
                    "frame-ancestors 'self' https://amithospitality.com https://*.amithospitality.com "
                    "http://localhost:* http://127.0.0.1:*;"
                )
            await send(message)

        await self.app(scope, receive, send_wrapper)


# --- 3. IN-MEMORY RATE LIMITING ASGI MIDDLEWARE ---

from app.services.redis_service import redis_service

class RateLimiter:
    """
    Sliding window rate limiter per IP address.
    Backing store powered by Redis distributed sorted sets with automatic local in-memory fallback.
    """
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    def is_allowed(self, client_ip: str, limit: int = None) -> Tuple[bool, int]:
        max_allowed = limit or self.max_requests
        return redis_service.check_rate_limit(client_ip, limit=max_allowed, window_seconds=self.window_seconds)

    def reset(self):
        """Reset rate limiter state (useful for tests)."""
        redis_service.reset_limits()

global_rate_limiter = RateLimiter(max_requests=80, window_seconds=60)

class RateLimitMiddleware:
    """
    Pure ASGI middleware guarding sensitive endpoints (chat, login) against abuse.
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        limit = None
        if path.startswith("/api/v1/chat/messages"):
            limit = 50  # 50 turns per minute per IP
        elif path.startswith("/api/v1/auth/login"):
            limit = 15  # 15 login attempts per minute per IP

        if limit is not None:
            client_ip = "127.0.0.1"
            client = scope.get("client")
            if client:
                client_ip = client[0]

            for header_name, header_val in scope.get("headers", []):
                if header_name.lower() == b"x-forwarded-for":
                    client_ip = header_val.decode("latin1").split(",")[0].strip()
                    break

            allowed, retry_after = global_rate_limiter.is_allowed(client_ip, limit=limit)
            if not allowed:
                response = JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Too many requests. Please wait a moment before sending another message.",
                        "retry_after_seconds": retry_after,
                    },
                    headers={"Retry-After": str(retry_after)},
                )
                await response(scope, receive, send)
                return

        await self.app(scope, receive, send)
