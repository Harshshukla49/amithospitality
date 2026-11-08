import time
from typing import Dict, Any
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

db_url = settings.clean_database_url

engine_kwargs: Dict[str, Any] = {
    "echo": False,
}

if db_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # PostgreSQL production connection pooling configuration
    engine_kwargs["pool_size"] = settings.DB_POOL_SIZE
    engine_kwargs["max_overflow"] = settings.DB_MAX_OVERFLOW
    engine_kwargs["pool_timeout"] = settings.DB_POOL_TIMEOUT
    engine_kwargs["pool_recycle"] = settings.DB_POOL_RECYCLE
    engine_kwargs["pool_pre_ping"] = True  # Automatically detect and recover from dropped pool connections

engine = create_engine(db_url, **engine_kwargs)

# On PostgreSQL connections, ensure pgvector extension is ready
if not db_url.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def on_connect(dbapi_con, connection_record):
        cursor = dbapi_con.cursor()
        try:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            dbapi_con.commit()
        except Exception:
            # Continue if user lacks superuser permissions or extension is pre-installed
            pass
        finally:
            cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_database_health() -> Dict[str, Any]:
    """Execute live ping against configured engine to verify database connectivity and response latency."""
    start_time = time.time()
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        latency_ms = round((time.time() - start_time) * 1000, 2)
        dialect = "sqlite" if db_url.startswith("sqlite") else "postgresql"
        return {
            "status": "healthy",
            "dialect": dialect,
            "latency_ms": latency_ms,
            "connected": True,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "connected": False,
        }
