import os
import urllib.parse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import text

def get_corrected_url():
    url = os.getenv("DATABASE_URL", "")
    if not url:
        print("❌ DATABASE_URL is NOT SET")
        return ""

    try:
        # Parse the URL
        # Format: postgresql://user:password@host:port/dbname
        if "://" not in url:
            return url
        
        scheme_part, rest = url.split("://")
        auth_part, host_port_db = rest.rsplit("@", 1)
        user_pass = auth_part.split(":", 1)
        user = user_pass[0]
        password = user_pass[1] if len(user_pass) > 1 else ""
        
        host_port, db_name = host_port_db.split("/", 1)
        if ":" in host_port:
            host, port = host_port.split(":")
        else:
            host, port = host_port, "5432"

        # 1. Force postgres username
        project_ref = ""
        if "." in user:
            # handle "postgres.projectref"
            u_parts = user.split(".")
            user = u_parts[0]
            project_ref = u_parts[1]
        
        if not project_ref and "supabase.co" in host:
            # try to get project ref from host: db.projectref.supabase.co
            h_parts = host.split(".")
            if len(h_parts) >= 3:
                project_ref = h_parts[1]
        
        if not project_ref and "pooler.supabase.com" in host:
            # host: aws-0-ap-southeast-1.pooler.supabase.com
            # we might not have the ref unless it was in the username
            pass

        # 2. Fix host to direct connection if project_ref found
        if project_ref:
            host = f"db.{project_ref}.supabase.co"
        
        # 3. Force port and db
        port = "5432"
        db_name = "postgres"

        # 4. URL encode password
        safe_password = urllib.parse.quote_plus(urllib.parse.unquote(password))

        # 5. Rebuild with +asyncpg
        new_url = f"postgresql+asyncpg://{user}:{safe_password}@{host}:{port}/{db_name}"
        
        print(f"✅ Corrected DATABASE_URL: {new_url.split('@')[0]}@***")
        return new_url
    except Exception as e:
        print(f"⚠️ URL Correction failed: {e}")
        # Fallback to simple replacement if complex parsing fails
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        if "+asyncpg" not in url:
            url = url.replace("postgresql://", "postgresql+asyncpg://")
        return url

DATABASE_URL = get_corrected_url()

# STEP 3: Fix SQLAlchemy connection
engine = create_async_engine(
    DATABASE_URL,
    echo=True, # Log SQL queries
    pool_pre_ping=True,
    connect_args={"ssl": "require"}
)

# Use sessionmaker as requested
AsyncSessionLocal = sessionmaker(
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
    print("🛠 Creating database tables...")
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
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print("❌ DB CONNECTION ERROR:", e)
        return False
