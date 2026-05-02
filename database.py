# PROJECT: SecureWealth Twin | v3.3
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from typing import Generator

def get_database_url() -> str | None:
    url = os.getenv("DATABASE_URL", "").strip()
    if not url:
        print("[DB] WARNING: DATABASE_URL not set — running memory-only mode")
        return None
    # Normalize prefix for psycopg2
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
    elif url.startswith("postgresql://") and "+psycopg2" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
    
    # Clean up any residual double protocols if they exist
    if "postgresql+psycopg2+asyncpg://" in url:
        url = url.replace("postgresql+psycopg2+asyncpg://", "postgresql+psycopg2://", 1)

    host = url.split("@")[-1].split("/")[0] if "@" in url else "unknown"
    print(f"[DB] Connecting to: {host}")
    return url

DATABASE_URL = get_database_url()

engine = None
SessionLocal = None

if DATABASE_URL:
    try:
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            connect_args={"sslmode": "require"},
        )
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
        print("[DB] Engine created successfully")
    except Exception as e:
        print(f"[DB] Engine creation failed: {e}")
        engine = None
        SessionLocal = None


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency — yields a sync DB session."""
    if not SessionLocal:
        yield None
        return
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_all_tables() -> bool:
    """Call on startup. Creates tables if they don't exist."""
    if not engine:
        print("[DB] Skipping table creation — no engine")
        return False
    try:
        from models import User, Account, Transaction, Goal, RiskAuditLog  # noqa
        Base.metadata.create_all(bind=engine)
        print("[DB] ✅ All tables created / verified")
        return True
    except Exception as e:
        print(f"[DB] ❌ Table creation failed: {e}")
        return False


def check_db_connection() -> bool:
    """Returns True if DB is reachable."""
    if not SessionLocal:
        return False
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception as e:
        print(f"[DB] Health check failed: {e}")
        return False
