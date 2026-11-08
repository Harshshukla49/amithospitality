from contextlib import asynccontextmanager
from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
import os

from app.config import settings
from app.database import Base, engine, check_database_health
from app.utils.security_middleware import SecurityHeadersMiddleware, RateLimitMiddleware
from app.utils.monitoring import init_sentry
from app.routers import (
    auth,
    environment,
    outlets,
    knowledge,
    reservations,
    leads,
    chat,
    analytics,
    audit,
    integrations,
    whatsapp,
    voice,
    notifications,
)

# Initialize production error telemetry
init_sentry()

# Initialize tables and storage directory on import
Base.metadata.create_all(bind=engine)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise AI Hospitality Management & Customer Concierge Platform for Amit Hospitality",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)

app.include_router(auth.router)
app.include_router(environment.router)
app.include_router(outlets.router)
app.include_router(knowledge.router)
app.include_router(reservations.router)
app.include_router(leads.router)
app.include_router(chat.router)
app.include_router(analytics.router)
app.include_router(audit.router)
app.include_router(integrations.router)
app.include_router(whatsapp.router, prefix="/api/v1")
app.include_router(voice.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")

@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "documentation": "/docs",
        "status": "operational",
    }

@app.get("/api/v1/health")
def healthcheck():
    """
    Comprehensive service health inspection endpoint.
    Verifies live database connectivity, latency, active dialect, and environment mode.
    """
    db_health = check_database_health()
    overall_status = "healthy" if db_health.get("connected") else "unhealthy"

    return {
        "status": overall_status,
        "app_name": settings.APP_NAME,
        "app_env": settings.APP_ENV,
        "version": "1.0.0",
        "database": db_health,
        "default_environment": settings.DEFAULT_ENVIRONMENT,
    }

@app.get("/api/v1/health/ready")
def readiness_probe(response: Response):
    """Kubernetes / Cloud container readiness probe."""
    db_health = check_database_health()
    if not db_health.get("connected"):
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"ready": False, "status": "unhealthy", "reason": "Database unreachable"}
    return {"ready": True, "status": "healthy"}

@app.get("/api/v1/health/live")
def liveness_probe():
    """Kubernetes / Cloud container liveness probe."""
    return {"live": True}
