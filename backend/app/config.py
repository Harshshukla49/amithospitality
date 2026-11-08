import os
from typing import List, Optional
from pydantic import model_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application Environment (development | staging | production)
    APP_NAME: str = "Amit AI Concierge"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Database
    DATABASE_URL: str = "sqlite:///./amit_concierge.db"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800

    # Security & JWT
    JWT_SECRET_KEY: str = "amit_hospitality_super_secure_jwt_secret_key_2026_change_in_production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Initial Administrator
    INITIAL_ADMIN_EMAIL: str = "admin@amithospitality.com"
    INITIAL_ADMIN_PASSWORD: str = "AmitConcierge2026!Secure"

    # Environment
    DEFAULT_ENVIRONMENT: str = "DEMO"

    # AI Configuration
    AI_PROVIDER: str = "gemini"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 25

    # Allowed Origins for CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"

    # External Integrations (Meta WhatsApp, Twilio Voice, Email/SMS, Redis)
    WHATSAPP_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_VERIFY_TOKEN: str = ""
    WHATSAPP_APP_SECRET: str = ""
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "concierge@amithospitality.com"
    SENDGRID_API_KEY: str = ""
    REDIS_URL: str = ""
    SENTRY_DSN: str = ""

    # Hospitality Hotline & Escalation Numbers (Configurable, never hardcoded)
    HOTLINE_PHONE_NUMBER: str = "+91 11 4050 9900"
    HOTLINE_EMAIL: str = "guestrelations@amithospitality.com"
    ESCALATION_PHONE_NUMBER: str = "+911140509900"

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    @property
    def clean_database_url(self) -> str:
        """Normalize database URL for SQLAlchemy compatibility across hosting providers."""
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg2://", 1)
        elif url.startswith("postgresql://") and "+psycopg2" not in url:
            url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
        return url

    @model_validator(mode="after")
    def validate_production_configuration(self) -> "Settings":
        """
        Enforce strict production safeguards:
        - Rejects default JWT secrets.
        - Rejects default admin passwords.
        - Rejects SQLite in production mode.
        - Enforces DEBUG=False in production mode.
        """
        if self.APP_ENV == "production":
            if self.JWT_SECRET_KEY == "amit_hospitality_super_secure_jwt_secret_key_2026_change_in_production":
                raise ValueError("Production security violation: JWT_SECRET_KEY cannot use default development placeholder.")
            if len(self.JWT_SECRET_KEY) < 32:
                raise ValueError("Production security violation: JWT_SECRET_KEY must be at least 32 characters long.")
            if self.INITIAL_ADMIN_PASSWORD == "AmitConcierge2026!Secure":
                raise ValueError("Production security violation: INITIAL_ADMIN_PASSWORD cannot use default development placeholder.")
            if self.clean_database_url.startswith("sqlite"):
                raise ValueError("Production database violation: SQLite is prohibited in production. A PostgreSQL + pgvector DATABASE_URL is required.")
            if self.DEBUG:
                raise ValueError("Production configuration violation: DEBUG must be False in production.")
        return self

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
