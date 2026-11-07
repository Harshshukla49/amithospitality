from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.config import settings
from app.database import Base, engine
from app.utils.security_middleware import SecurityHeadersMiddleware, RateLimitMiddleware
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
)

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
    return {
        "status": "healthy",
        "database": "connected",
        "environment": settings.APP_ENV,
    }
