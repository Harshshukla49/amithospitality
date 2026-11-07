import time
import re
import html
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
    Pure ASGI middleware injecting enterprise security headers.
    Protects against MIME-sniffing, XSS, and unauthorized clickjacking.
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers["X-Content-Type-Options"] = "nosniff"
                headers["X-XSS-Protection"] = "1; mode=block"
                headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
                headers["Content-Security-Policy"] = (
                    "frame-ancestors 'self' https://amithospitality.com https://*.amithospitality.com "
                    "http://localhost:* http://127.0.0.1:*;"
                )
            await send(message)

        await self.app(scope, receive, send_wrapper)


# --- 3. IN-MEMORY RATE LIMITING ASGI MIDDLEWARE ---

class RateLimiter:
    """
    Sliding window in-memory rate limiter per IP address.
    """
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = {}

    def is_allowed(self, client_ip: str, limit: int = None) -> Tuple[bool, int]:
        max_allowed = limit or self.max_requests
        now = time.time()
        cutoff = now - self.window_seconds

        client_timestamps = self.requests.get(client_ip, [])
        client_timestamps = [ts for ts in client_timestamps if ts > cutoff]

        if len(client_timestamps) >= max_allowed:
            self.requests[client_ip] = client_timestamps
            retry_after = int(self.window_seconds - (now - client_timestamps[0])) + 1
            return False, max(1, retry_after)

        client_timestamps.append(now)
        self.requests[client_ip] = client_timestamps
        return True, 0

    def reset(self):
        """Reset rate limiter state (useful for tests)."""
        self.requests.clear()

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
