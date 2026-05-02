import os
import urllib.parse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import text

def get_database_url():
    url = os.getenv("DATABASE_URL")
    if not url:
        # Fallback to the exact one requested if env is missing for testing
        url = "postgresql://postgres.xigafgionuxddugjnhlw:Latheesh1@12345@aws-1-ap-southeast-2.pooler.supabase.com:5432/postgres"

    # 1. Fix prefix automatically
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    # 10. Handle special characters in password (URL encode)
    # The password "Latheesh1@12345" has an @ which breaks URL parsing
    if "postgresql+asyncpg://" in url:
        try:
            # Basic split to isolate credentials and host
            prefix, rest = url.split("://")
            auth, host = rest.rsplit("@", 1)
            user, password = auth.split(":", 1)
            
            # Encode password if it contains special chars like @
            encoded_password = urllib.parse.quote_plus(password)
            url = f"{prefix}://{user}:{encoded_password}@{host}"
        except Exception as e:
            print(f"[DB URL FIX] Warning: Could not auto-encode password: {e}")

    return url

DATABASE_URL = get_database_url()

# 4. Engine setup with REQUIRED SSL for Supabase
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    connect_args={"ssl": "require"}
)

# 5. Create async session using sessionmaker
AsyncSessionLocal = sessionmaker(
    bind=engine,
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

# 8. Ensure tables are created on startup
async def create_all_tables():
    try:
        async with engine.begin() as conn:
            # Crucial: Import models so they register with Base
            from models import User, Account, Transaction, Goal, RiskAuditLog # noqa
            await conn.run_sync(Base.metadata.create_all)
        print("✅ DB TABLES VERIFIED/CREATED")
    except Exception as e:
        print(f"❌ DB TABLE CREATION FAILED: {e}")

# 6. Database connection test function
async def check_db_connection():
    try:
        async with engine.begin() as conn:
            # uses run_sync pattern as requested
            await conn.run_sync(lambda conn: None)
        print("✅ DB CONNECTED SUCCESSFULLY")
        return True
    except Exception as e:
        print("DB CONNECTION ERROR:", e)
        return False
