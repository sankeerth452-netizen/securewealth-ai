import os
import traceback
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text

def get_database_url():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise ValueError("CRITICAL ERROR: DATABASE_URL environment variable is missing.")
    
    # Supabase/PostgreSQL dynamic correction for asyncpg
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
    # Handle both postgresql+asyncpg://user:pass and postgresql://user:pass
    protocol_user = auth_part.split('://')[1]
    user = protocol_user.split(':')[0]
    masked_url = f"postgresql+asyncpg://{user}:****@{host_part}"
    print(f"DB URL: {masked_url}")
except Exception:
    print("DB URL: (exists, masked)")

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
            # Crucial: Import all models so they register with Base.metadata
            from models import User, Account, Transaction, Goal, RiskAuditLog # noqa
            await conn.run_sync(Base.metadata.create_all)
        print("✅ DB TABLES VERIFIED/CREATED")
    except Exception as e:
        print(f"❌ DB TABLE CREATION FAILED: {e}")
        traceback.print_exc()

async def check_db_connection():
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        print("✅ DB CONNECTED SUCCESSFULLY")
        return True
    except Exception as e:
        print("❌ DB CONNECTION FAILED")
        traceback.print_exc()
        return False
