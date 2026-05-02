# PROJECT: SecureWealth Twin | v3.2
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text

# Import database and models explicitly
from database import create_all_tables, get_db, check_db_connection
import models # Ensures all models are registered
from models import * # Explicitly compliant with Step 7

from routes import (
    chat, risk, simulate,
    aggregator, networth, profile, execution
)
from routes.auth import router as auth_router

FRONTEND_URL = os.getenv("FRONTEND_URL", "https://securewealth-ai.vercel.app")

# ----------------------------
# LIFESPAN (Startup/Shutdown)
# ----------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 SecureWealth Twin API starting...")
    has_url = os.getenv("DATABASE_URL") is not None
    print(f"DATABASE_URL Configured: {'✅' if has_url else '❌ MISSING'}")
    
    await create_all_tables()
    db_ok = await check_db_connection()
    print(f"Startup DB Check: {'✅ SUCCESS' if db_ok else '❌ FAILED'}")
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

# ----------------------------
# ROOT & DEBUG
# ----------------------------
@app.get("/")
def root():
    return {
        "status": "SecureWealth Twin AI is running ✅",
        "version": "3.2",
        "db": "PostgreSQL via Supabase"
    }

@app.get("/debug-db")
async def debug_db():
    db_url = os.getenv("DATABASE_URL")
    return {
        "has_db_url": db_url is not None,
        "preview": db_url[:30] if db_url else None,
        "fixed_format": db_url.replace("postgres://", "postgresql+asyncpg://")[:40] if db_url else None
    }

@app.get("/health")
async def health():
    db_ok = await check_db_connection()
    tables_exist = False
    if db_ok:
        from database import AsyncSessionLocal
        async with AsyncSessionLocal() as s:
            r = await s.execute(text(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name='users')"
            ))
            tables_exist = r.scalar()
    
    return {
        "db_connected": db_ok,
        "tables_exist": tables_exist
    }

# ----------------------------
# USER SUMMARY ENDPOINT (Live Dashboard)
# ----------------------------
@app.get("/api/ai/user-summary")
async def user_summary(user_id: str, db: AsyncSession = Depends(get_db)):
    if not db:
        return {"error": "DB offline"}
    try:
        from uuid import UUID
        uid = UUID(user_id)
        acc_result = await db.execute(select(Account).where(Account.user_id == uid))
        account = acc_result.scalar_one_or_none()
        if not account: return {"error": "Account not found"}
        
        # Monthly totals
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0)
        sent_res = await db.execute(select(func.sum(Transaction.amount)).where(Transaction.sender_id == account.id, Transaction.timestamp >= month_start))
        
        return {
            "account_number": account.account_number,
            "balance": float(account.balance),
            "total_sent_this_month": float(sent_res.scalar() or 0)
        }
    except Exception as e:
        return {"error": str(e)}