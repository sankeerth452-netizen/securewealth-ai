# PROJECT: SecureWealth Twin | v3.2
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text

def get_database_url():
    url = os.getenv("DATABASE_URL", "")
    if not url:
        print("[DB] WARNING: DATABASE_URL not set")
        return None
    # Fix common prefix mistakes
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url

DATABASE_URL = get_database_url()

engine = None
AsyncSessionLocal = None

if DATABASE_URL:
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        connect_args={"ssl": "require"},
    )
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    print(f"[DB] Engine created for host: {DATABASE_URL.split('@')[-1].split('/')[0]}")
else:
    print("[DB] No DATABASE_URL — running in memory-only mode")


class Base(DeclarativeBase):
    pass


async def get_db():
    if not AsyncSessionLocal:
        yield None
        return
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_all_tables():
    if not engine:
        print("[DB] Skipping table creation — no engine")
        return
    try:
        async with engine.begin() as conn:
            from models import User, Account, Transaction, Goal, RiskAuditLog  # noqa
            await conn.run_sync(Base.metadata.create_all)
        print("[DB] ✅ All tables created / verified")
    except Exception as e:
        print(f"[DB] ❌ Table creation failed: {e}")


async def check_db_connection():
    if not AsyncSessionLocal:
        return False
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"[DB] Health check failed: {e}")
        return False
