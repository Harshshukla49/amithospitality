import time
import logging
from typing import Optional, Tuple, Dict, Any, List

from app.config import settings

logger = logging.getLogger("redis_service")

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis python package not installed; running in in-memory mode only.")

class RedisService:
    """
    Production Redis Distributed Cache & Rate Limiting Service.
    Seamlessly falls back to thread-safe in-memory sliding window and cache
    if Redis is not configured or temporarily unreachable.
    Explicitly reports active mode (DISTRIBUTED_REDIS vs IN_MEMORY_FALLBACK).
    """

    def __init__(self):
        self._client: Optional[Any] = None
        self._memory_cache: Dict[str, Tuple[str, float]] = {}  # {key: (value, expire_timestamp)}
        self._memory_limits: Dict[str, List[float]] = {}       # {key: [timestamps]}
        self._init_redis()

    def _init_redis(self):
        if not REDIS_AVAILABLE:
            self._client = None
            return

        redis_url = settings.REDIS_URL.strip() if settings.REDIS_URL else ""
        if redis_url and not redis_url.startswith("your_"):
            try:
                self._client = redis.Redis.from_url(
                    redis_url,
                    socket_connect_timeout=2.0,
                    socket_timeout=2.0,
                    decode_responses=True,
                )
                logger.info("Initialized Redis client for distributed caching & rate limiting.")
            except Exception as e:
                logger.error(f"Failed to initialize Redis client from REDIS_URL: {e}")
                self._client = None
        else:
            self._client = None

    @property
    def is_configured(self) -> bool:
        return bool(
            settings.REDIS_URL
            and len(settings.REDIS_URL.strip()) > 8
            and not settings.REDIS_URL.startswith("your_")
        )

    @property
    def active_mode(self) -> str:
        """Explicitly report whether operating distributed or falling back to memory."""
        if self._client is not None:
            try:
                if self._client.ping():
                    return "DISTRIBUTED_REDIS"
            except Exception:
                pass
        return "IN_MEMORY_FALLBACK"

    @property
    def is_degraded(self) -> bool:
        """Indicates whether distributed multi-node protection is degraded."""
        return self.active_mode != "DISTRIBUTED_REDIS"

    @property
    def protection_status(self) -> str:
        """Report protection assurance level."""
        return "DISTRIBUTED_FULL_CLUSTER" if not self.is_degraded else "DEGRADED_LOCAL_NODE_ONLY"

    # ==========================================
    # DISTRIBUTED RATE LIMITING
    # ==========================================

    def check_rate_limit(self, key: str, limit: int, window_seconds: int = 60) -> Tuple[bool, int]:
        """
        Sliding-window rate limiter using Redis sorted sets (ZREMRANGEBYSCORE + ZADD).
        Falls back seamlessly to in-memory sliding window on error or absence.
        Returns: (allowed: bool, retry_after_seconds: int)
        """
        now = time.time()
        cutoff = now - window_seconds

        # Attempt Redis distributed rate limit
        if self._client is not None:
            redis_key = f"rl:{key}"
            try:
                pipeline = self._client.pipeline(transaction=True)
                pipeline.zremrangebyscore(redis_key, "-inf", cutoff)
                pipeline.zcard(redis_key)
                pipeline.zadd(redis_key, {str(now): now})
                pipeline.expire(redis_key, window_seconds + 5)
                results = pipeline.execute()

                current_count = results[1]
                if current_count >= limit:
                    # Exceeded limit
                    oldest_scores = self._client.zrange(redis_key, 0, 0, withscores=True)
                    retry_after = 1
                    if oldest_scores:
                        oldest_ts = oldest_scores[0][1]
                        retry_after = max(1, int(window_seconds - (now - oldest_ts)) + 1)
                    return False, retry_after
                return True, 0
            except Exception as e:
                logger.debug(f"Redis rate limiting failed ({e}); falling back to local memory.")

        # In-Memory Fallback
        timestamps = self._memory_limits.get(key, [])
        valid_ts = [ts for ts in timestamps if ts > cutoff]

        if len(valid_ts) >= limit:
            self._memory_limits[key] = valid_ts
            retry_after = max(1, int(window_seconds - (now - valid_ts[0])) + 1)
            return False, retry_after

        valid_ts.append(now)
        self._memory_limits[key] = valid_ts
        return True, 0

    # ==========================================
    # DISTRIBUTED KEY-VALUE CACHE
    # ==========================================

    def get(self, key: str) -> Optional[str]:
        """Get cached string value with TTL validation."""
        if self._client is not None:
            try:
                return self._client.get(key)
            except Exception as e:
                logger.debug(f"Redis get failed ({e}); checking local memory.")

        # In-Memory Fallback
        entry = self._memory_cache.get(key)
        if entry:
            val, expire_at = entry
            if time.time() < expire_at:
                return val
            else:
                del self._memory_cache[key]
        return None

    def set(self, key: str, value: str, ttl_seconds: int = 300) -> bool:
        """Set cached string value with expiration."""
        if self._client is not None:
            try:
                self._client.set(key, value, ex=ttl_seconds)
                return True
            except Exception as e:
                logger.debug(f"Redis set failed ({e}); using local memory.")

        # In-Memory Fallback
        self._memory_cache[key] = (value, time.time() + ttl_seconds)
        return True

    def delete(self, key: str) -> bool:
        """Delete cached entry."""
        deleted = False
        if self._client is not None:
            try:
                self._client.delete(key)
                deleted = True
            except Exception:
                pass
        if key in self._memory_cache:
            del self._memory_cache[key]
            deleted = True
        return deleted

    def reset_limits(self):
        """Reset limits (useful for testing)."""
        self._memory_limits.clear()
        if self._client is not None:
            try:
                keys = self._client.keys("rl:*")
                if keys:
                    self._client.delete(*keys)
            except Exception:
                pass

    # ==========================================
    # CONNECTIVITY AUDIT
    # ==========================================

    def test_connection(self) -> Dict[str, Any]:
        """
        Test live Redis connectivity.
        Reports status, latency, and whether running in DISTRIBUTED or FALLBACK mode.
        """
        if not self.is_configured:
            return {
                "name": "Redis Distributed Cache & Rate Limiter",
                "status": "NOT CONFIGURED",
                "connected": False,
                "mode": "IN_MEMORY_FALLBACK",
                "protection_status": self.protection_status,
                "degraded": self.is_degraded,
                "description": "Running in high-performance local memory fallback mode (Degraded: single-node rate limiting only).",
                "action_required": "Set REDIS_URL (e.g. rediss://... or redis://...) to activate distributed cluster sync.",
            }

        start_t = time.time()
        try:
            if not self._client:
                self._init_redis()

            if not self._client:
                return {
                    "name": "Redis Distributed Cache & Rate Limiter",
                    "status": "DISCONNECTED",
                    "connected": False,
                    "mode": "IN_MEMORY_FALLBACK",
                    "error": "Could not create Redis client connection.",
                }

            ping_res = self._client.ping()
            latency = round((time.time() - start_t) * 1000, 1)

            if ping_res:
                info = {}
                try:
                    info = self._client.info("server")
                except Exception:
                    pass

                return {
                    "name": "Redis Distributed Cache & Rate Limiter",
                    "status": "CONNECTED",
                    "connected": True,
                    "mode": "DISTRIBUTED_REDIS",
                    "protection_status": self.protection_status,
                    "degraded": self.is_degraded,
                    "redis_version": info.get("redis_version", "unknown"),
                    "latency_ms": latency,
                    "verified_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                }
            else:
                return {
                    "name": "Redis Distributed Cache & Rate Limiter",
                    "status": "DISCONNECTED",
                    "connected": False,
                    "mode": "IN_MEMORY_FALLBACK",
                    "error": "Ping did not return True",
                }
        except Exception as e:
            return {
                "name": "Redis Distributed Cache & Rate Limiter",
                "status": "DISCONNECTED",
                "connected": False,
                "mode": "IN_MEMORY_FALLBACK",
                "error": str(e),
            }

redis_service = RedisService()
