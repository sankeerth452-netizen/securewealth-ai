# PROJECT: SecureWealth Twin | v3.2
import os
import time
import asyncpg
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text

# Import database and models explicitly
from database import create_all_tables, get_db, check_db_connection, engine
import models
from models import *

from routes import (
    chat, risk, simulate,
    aggregator, networth, profile, execution,
    transactions, goals
)
from routes.auth import router as auth_router

FRONTEND_URL = os.getenv("FRONTEND_URL", "https://securewealth-ai.vercel.app")

# ----------------------------
# STEP 4: LIFESPAN (Startup/Shutdown)
# ----------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 SecureWealth Twin API starting...")
    
    # STEP 5: Clear logging
    db_url = os.getenv("DATABASE_URL", "")
    print("==== DEBUG DATABASE URL ====")
    if db_url:
        # show only safe preview
        print(f"URL Provided: {db_url[:40]}...")
    else:
        print("DATABASE_URL is NOT SET")
    print("============================")
    
    # Create tables
    await create_all_tables()
    
    # Verify connection
    db_ok = await check_db_connection()
    if db_ok:
        print("✅ Database connection verified successfully.")
    else:
        print("❌ Database connection FAILED.")
    
    yield

# ----------------------------
# APP INIT
# ----------------------------
app = FastAPI(
    title="SecureWealth Twin",
    version="3.2",
    lifespan=lifespan
)

# ----------------------------
# CORS
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://securewealth-ai.vercel.app",
        "http://localhost:3000",
        "http://localhost:5000",
        "http://127.0.0.1:5000",
        FRONTEND_URL,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# LOGGING MIDDLEWARE
# ----------------------------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        print(f"[REQ] {request.method} {request.url.path} - {response.status_code} ({process_time:.3f}s)")
        return response
    except Exception as e:
        print(f"[ERR] API Failure on {request.method} {request.url.path}: {str(e)}")
        raise

# ----------------------------
# STEP 1: DEBUG ENDPOINTS
# ----------------------------

@app.get("/debug/env")
async def debug_env():
    url = os.getenv("DATABASE_URL")
    return {
        "exists": url is not None,
        "preview": url[:50] + "..." if url else None
    }

@app.get("/debug/url")
async def debug_url():
    url = os.getenv("DATABASE_URL", "")
    from database import DATABASE_URL as fixed_url
    return {
        "raw_starts_with_postgresql": url.startswith("postgresql"),
        "fixed_has_asyncpg": "+asyncpg" in fixed_url,
        "fixed_has_supabase_host": "supabase.co" in fixed_url,
        "fixed_has_port": ":5432" in fixed_url,
        "fixed_preview": fixed_url[:60] + "..."
    }

@app.get("/debug/raw-db")
async def raw_db():
    from database import DATABASE_URL as fixed_url
    try:
        # We need to strip the +asyncpg for the raw asyncpg driver if it doesn't support it
        # But actually asyncpg uses postgresql:// or postgres://
        raw_url = fixed_url.replace("+asyncpg", "")
        conn = await asyncpg.connect(raw_url)
        await conn.execute("SELECT 1")
        await conn.close()
        return {"connected": True}
    except Exception as e:
        return {"connected": False, "error": str(e)}

# ----------------------------
# ROUTES
# ----------------------------
app.include_router(auth_router,       prefix="/api",    tags=["Auth"])
app.include_router(chat.router,       prefix="/api/ai", tags=["AI Chat"])
app.include_router(simulate.router,   prefix="/api/ai", tags=["Simulation"])
app.include_router(aggregator.router, prefix="/api/ai", tags=["Aggregator"])
app.include_router(networth.router,   prefix="/api/ai", tags=["Net Worth"])
app.include_router(profile.router,    prefix="/api/ai", tags=["Profile"])
app.include_router(risk.router,       prefix="/api",    tags=["Risk Engine"])
app.include_router(execution.router,  prefix="/api",    tags=["Execution Engine"])
app.include_router(transactions.router, prefix="/api",  tags=["Transactions"])
app.include_router(goals.router,        prefix="/api",  tags=["Goals"])

# ----------------------------
# ROOT & HEALTH
# ----------------------------
@app.get("/")
def root():
    return {
        "status": "SecureWealth Twin AI is running ✅",
        "version": "3.2",
        "db": "PostgreSQL via Supabase"
    }

@app.get("/health")
async def health():
    db_ok = await check_db_connection()
    tables_exist = False
    if db_ok:
        async with engine.connect() as conn:
            r = await conn.execute(text(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name='users')"
            ))
            tables_exist = r.scalar()
    
    return {
        "db_connected": db_ok,
        "tables_exist": tables_exist
    }