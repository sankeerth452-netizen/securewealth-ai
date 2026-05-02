import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import text

DATABASE_URL = os.getenv("DATABASE_URL")

# FORCE correct async format
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

print("USING DB URL:", DATABASE_URL[:60] if DATABASE_URL else "NOT SET")

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    connect_args={"ssl": "require"}
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
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
            from models import User, Account, Transaction, Goal, RiskAuditLog # noqa
            await conn.run_sync(Base.metadata.create_all)
        print("✅ DB TABLES VERIFIED/CREATED")
    except Exception as e:
        print(f"❌ DB TABLE CREATION FAILED: {e}")

async def check_db_connection():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(lambda conn: None)
        return True
    except Exception as e:
        print("DB CONNECTION ERROR:", e)
        return False
