# Redis Distributed Cache & Rate Limiting Configuration Guide
## Amit AI Concierge — Amit Hospitality (https://amithospitality.com/)

---

### 1. Overview
The Redis integration enables multi-instance distributed cluster synchronization for:
1. **Sliding-Window Rate Limiting:** Enforces abuse limits across load-balanced backend containers using Redis sorted sets (`ZADD`, `ZREMRANGEBYSCORE`, `ZCARD`, `EXPIRE`).
2. **Distributed Key-Value Caching:** Caches high-throughput queries (outlet directories, verified knowledge fragments, auth session states) with TTL expiration.
3. **Seamless In-Memory Fallback:** If `REDIS_URL` is unconfigured or temporarily unreachable, the service transparently falls back to a thread-safe local sliding-window limiter without crashing or degrading application availability.
4. **Transparent Status Reporting:** Explicitly reports active mode (`DISTRIBUTED_REDIS` vs. `IN_MEMORY_FALLBACK`).

---

### 2. Environment Configuration

Add the following variable to `.env`:

```env
# Local Redis instance:
REDIS_URL=redis://localhost:6379/0

# Secure Cloud Redis (Render KeyDB / AWS ElastiCache / Redis Cloud / GCP Memorystore):
# REDIS_URL=rediss://default:your_redis_password@your-redis-host.com:6380/0
```

---

### 3. Architecture & Sliding-Window Algorithm

```mermaid
flowchart TD
    Client[Incoming Request] --> Mid[RateLimitMiddleware]
    Mid --> RedisCheck{Redis Configured & Reachable?}
    RedisCheck -- Yes --> ZSet[Redis Sorted Set: ZREMRANGEBYSCORE & ZADD]
    ZSet --> CountCheck{Count > Limit?}
    CountCheck -- Exceeded --> Block[HTTP 429 Too Many Requests]
    CountCheck -- Allowed --> Pass[Process API Handler]

    RedisCheck -- No / Down --> MemFallback[In-Memory Sliding Window Fallback]
    MemFallback --> MemCheck{Count > Limit?}
    MemCheck -- Exceeded --> Block
    MemCheck -- Allowed --> Pass
```

---

### 4. Service Interface & Usage

Defined in [`backend/app/services/redis_service.py`](file:///c:/Users/india/Desktop/amit%20hospitality/backend/app/services/redis_service.py):

```python
from app.services.redis_service import redis_service

# 1. Rate Limiting Check
allowed, retry_after = redis_service.check_rate_limit(
    key="client_ip_192.168.1.1",
    limit=50,
    window_seconds=60,
)
if not allowed:
    print(f"Rate limit exceeded. Retry after {retry_after}s.")

# 2. Key-Value Caching
redis_service.set("outlet:amber-terrace", "{...}", ttl_seconds=300)
cached_value = redis_service.get("outlet:amber-terrace")

# 3. Active Mode Check
print("Operating Mode:", redis_service.active_mode)
# Outputs: 'DISTRIBUTED_REDIS' or 'IN_MEMORY_FALLBACK'
```

---

### 5. Diagnostics & Verification

Execute live diagnostic tests:
```bash
curl -X POST http://localhost:8000/api/v1/integrations/test/redis \
  -H "Authorization: Bearer <ADMIN_JWT_TOKEN>"
```
Expected response in local fallback mode:
```json
{
  "name": "Redis Distributed Cache & Rate Limiter",
  "status": "NOT CONFIGURED",
  "connected": false,
  "mode": "IN_MEMORY_FALLBACK",
  "description": "Running in high-performance local memory fallback mode.",
  "action_required": "Set REDIS_URL (e.g. rediss://... or redis://...) to activate distributed cluster sync."
}
```
Expected response when connected to live Redis:
```json
{
  "name": "Redis Distributed Cache & Rate Limiter",
  "status": "CONNECTED",
  "connected": true,
  "mode": "DISTRIBUTED_REDIS",
  "redis_version": "7.2.4",
  "latency_ms": 1.8,
  "verified_at": "2026-11-08T18:45:00Z"
}
```
