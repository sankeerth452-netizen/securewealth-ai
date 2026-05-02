import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text

def get_database_url():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise ValueError("CRITICAL ERROR: DATABASE_URL environment variable is missing.")
    
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url

DATABASE_URL = get_database_url()

# Mask password for logging
try:
    auth_part = DATABASE_URL.split('@')[0]
    host_part = DATABASE_URL.split('@')[1]
    user_part = auth_part.split(':')[1]
    masked_url = f"postgresql+asyncpg://{user_part.replace('//', '')}:***@{host_part}"
    print(f"[DB INIT] Using DATABASE_URL: {masked_url}")
except Exception:
    print("[DB INIT] Using DATABASE_URL: (masked)")

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    connect_args={"ssl": "require"}
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def create_all_tables():
    try:
        async with engine.begin() as conn:
            from models import User, Account, Transaction, Goal, RiskAuditLog  # noqa
            await conn.run_sync(Base.metadata.create_all)
        print("[DB SETUP] ✅ All tables created or verified successfully.")
    except Exception as e:
        print(f"[DB SETUP ERROR] ❌ Table creation failed: {e}")

async def check_db_connection():
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        print("[DB STATUS] ✅ Database connection successful.")
        return True
    except Exception as e:
        print("DB CONNECTION ERROR:", e)
        return False
