import time
import json
import logging
import urllib.request
import urllib.error
from typing import Optional, List, Dict, Any

from app.config import settings

logger = logging.getLogger("gemini_service")

class GeminiService:
    """
    Production-grade Google Gemini AI Service integration.
    Features:
    - Grounded RAG-based responses with zero-hallucination prompts.
    - Retries with exponential backoff on transient network / rate-limit failures.
    - Multi-turn conversation context history support.
    - English, Hindi, and Hinglish multilingual instruction enforcement.
    - Token tracking and latency measurement.
    - Graceful fallback when API key is missing or quota is exceeded.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL or "gemini-1.5-flash"
        self.endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 5 and not self.api_key.startswith("your_"))

    def generate_grounded_response(
        self,
        prompt: str,
        system_instruction: str,
        environment: str = "DEMO",
        history: Optional[List[Dict[str, str]]] = None,
        max_retries: int = 2,
        timeout: int = 10,
    ) -> Optional[Dict[str, Any]]:
        """
        Generate grounded concierge response via Google Gemini API with retries and fallback.
        Returns Dict with 'reply', 'tokens_used', 'latency_ms', or None if unavailable.
        """
        if not self.is_configured:
            return None

        url = f"{self.endpoint}?key={self.api_key}"

        # Construct multi-turn contents
        contents: List[Dict[str, Any]] = []
        if history:
            for turn in history[-6:]:  # Keep recent 3 dialogue turns
                role = "user" if turn.get("role") == "user" else "model"
                contents.append({"role": role, "parts": [{"text": turn.get("content", "")}]})

        contents.append({"role": "user", "parts": [{"text": prompt}]})

        payload = {
            "contents": contents,
            "systemInstruction": {"parts": [{"text": system_instruction}]},
            "generationConfig": {
                "temperature": 0.15 if environment == "REAL" else 0.3,
                "maxOutputTokens": 700,
                "topP": 0.8,
            },
        }

        data_bytes = json.dumps(payload).encode("utf-8")

        for attempt in range(max_retries + 1):
            start_t = time.time()
            try:
                req = urllib.request.Request(
                    url,
                    data=data_bytes,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    latency = round((time.time() - start_t) * 1000, 1)
                    if response.status == 200:
                        res_data = json.loads(response.read().decode("utf-8"))
                        candidates = res_data.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            if parts:
                                reply_text = parts[0].get("text", "").strip()
                                usage = res_data.get("usageMetadata", {})
                                total_tokens = usage.get("totalTokenCount", len(reply_text) // 4)
                                return {
                                    "reply": reply_text,
                                    "tokens_used": total_tokens,
                                    "latency_ms": latency,
                                    "model": self.model,
                                    "provider": "gemini",
                                }
            except urllib.error.HTTPError as http_err:
                status_code = http_err.code
                error_body = http_err.read().decode("utf-8", errors="ignore")
                logger.warning(f"Gemini API HTTP {status_code} (attempt {attempt + 1}/{max_retries + 1}): {error_body[:200]}")
                if status_code in (429, 503) and attempt < max_retries:
                    time.sleep(1.0 * (2 ** attempt))  # Exponential backoff
                    continue
                break
            except Exception as e:
                logger.warning(f"Gemini API network error (attempt {attempt + 1}/{max_retries + 1}): {e}")
                if attempt < max_retries:
                    time.sleep(0.5)
                    continue
                break

        return None

    def test_connectivity(self) -> Dict[str, Any]:
        """
        Perform an authentic live verification check against the Google Gemini API.
        Never fabricates connection success.
        """
        if not self.is_configured:
            return {
                "name": "Google Gemini Generative AI",
                "status": "NOT CONFIGURED",
                "connected": False,
                "error": "GEMINI_API_KEY is not set or uses a placeholder.",
                "action_required": "Provide a valid Google AI Studio Gemini API key.",
            }

        start_t = time.time()
        url = f"{self.endpoint}?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": "Ping"}]}],
            "generationConfig": {"maxOutputTokens": 5},
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=8) as response:
                latency = round((time.time() - start_t) * 1000, 1)
                if response.status == 200:
                    return {
                        "name": "Google Gemini Generative AI",
                        "status": "CONNECTED",
                        "connected": True,
                        "model": self.model,
                        "latency_ms": latency,
                        "verified_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    }
                else:
                    return {
                        "name": "Google Gemini Generative AI",
                        "status": "DISCONNECTED",
                        "connected": False,
                        "error": f"HTTP status {response.status}",
                    }
        except urllib.error.HTTPError as he:
            err_msg = he.read().decode("utf-8", errors="ignore")
            return {
                "name": "Google Gemini Generative AI",
                "status": "DISCONNECTED",
                "connected": False,
                "error": f"HTTP {he.code}: {err_msg[:250]}",
            }
        except Exception as e:
            return {
                "name": "Google Gemini Generative AI",
                "status": "DISCONNECTED",
                "connected": False,
                "error": str(e),
            }

    def test_connection(self) -> Dict[str, Any]:
        """Alias for test_connectivity."""
        return self.test_connectivity()

    def format_grounded_prompt(
        self,
        system_instruction: str,
        context_chunks: List[str],
        user_message: str,
        chat_history: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """
        Assemble strict grounding context and instructions.
        """
        context_text = "\n---\n".join(context_chunks)
        assembled = f"{system_instruction}\n\n[VERIFIED CONTEXT CHUNKS]:\n{context_text}\n\n[USER INQUIRY]:\n{user_message}"
        return assembled

    def calculate_token_usage(self, prompt: str, completion: str) -> Dict[str, int]:
        """Calculate approximate token usage for input and output."""
        prompt_tokens = max(1, len(prompt) // 4)
        completion_tokens = max(1, len(completion) // 4)
        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        }

gemini_service = GeminiService()
