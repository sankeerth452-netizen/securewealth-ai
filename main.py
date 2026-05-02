# PROJECT: SecureWealth Twin | v3.2
import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text

from database import create_all_tables, get_db, check_db_connection
from models import Account, Transaction, RiskAuditLog
import models  # ensures all models are registered with Base

from routes import (
    chat, risk, simulate,
    aggregator, networth, profile, execution
)
from routes.auth import router as auth_router

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5000")

# ----------------------------
# LIFESPAN (replaces @on_event)
# ----------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 SecureWealth Twin API starting...")
    await create_all_tables()
    db_ok = await check_db_connection()
    print(f"[DB] Status: {'✅ connected' if db_ok else '❌ offline — degraded mode'}")
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
        "http://localhost:5000",
        "http://127.0.0.1:5000",
        FRONTEND_URL,
    ],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


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
# ROOT
# ----------------------------
@app.get("/")
def root():
    return {
        "status": "SecureWealth Twin AI is running ✅",
        "version": "3.2",
        "agents": 7,
        "db": "PostgreSQL via Supabase",
        "auth": "JWT (HS256)",
    }


# ----------------------------
# HEALTH CHECK (with DB)
# ----------------------------
@app.get("/health")
async def health():
    db_ok = await check_db_connection()
    tables_ok = False
    if db_ok:
        from database import AsyncSessionLocal
        from sqlalchemy import text
        async with AsyncSessionLocal() as s:
            r = await s.execute(text(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name='users')"
            ))
            tables_ok = r.scalar()
    return {
        "status": "healthy",
        "db": "connected" if db_ok else "offline",
        "tables_created": tables_ok,
        "agents": 7,
        "version": "3.2"
    }


# ----------------------------
# USER SUMMARY ENDPOINT
# ----------------------------
@app.get("/api/ai/user-summary")
async def user_summary(user_id: str, db: AsyncSession = Depends(get_db)):
    """
    Returns live dashboard data for a user from the database.
    Powers the real-time dashboard after login.
    """
    if not db:
        return {"error": "DB offline"}
    try:
        from uuid import UUID
        uid = UUID(user_id)

        # Fetch account
        acc_result = await db.execute(
            select(Account).where(Account.user_id == uid)
        )
        account = acc_result.scalar_one_or_none()
        if not account:
            return {"error": "Account not found"}

        balance = float(account.balance)
        acc_id  = account.id

        # Last 5 transactions
        tx_result = await db.execute(
            select(Transaction)
            .where(Transaction.sender_id == acc_id)
            .order_by(Transaction.timestamp.desc())
            .limit(5)
        )
        last_txns = [{
            "amount": float(t.amount),
            "note":   t.note,
            "status": t.status,
            "decision": t.risk_decision or "ALLOW",
            "timestamp": t.timestamp.isoformat()
        } for t in tx_result.scalars().all()]

        # This month totals
        now         = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0)

        sent_result = await db.execute(
            select(func.sum(Transaction.amount))
            .where(Transaction.sender_id == acc_id)
            .where(Transaction.timestamp >= month_start)
        )
        total_sent = float(sent_result.scalar() or 0)

        recv_result = await db.execute(
            select(func.sum(Transaction.amount))
            .where(Transaction.receiver_id == acc_id)
            .where(Transaction.timestamp >= month_start)
        )
        total_received = float(recv_result.scalar() or 0)

        # Risk events this week
        week_start = now - timedelta(days=7)
        risk_result = await db.execute(
            select(func.count(RiskAuditLog.id))
            .where(RiskAuditLog.account_id == acc_id)
            .where(RiskAuditLog.timestamp >= week_start)
            .where(RiskAuditLog.decision != "ALLOW")
        )
        risk_events = int(risk_result.scalar() or 0)

        return {
            "account_number": account.account_number,
            "balance":         balance,
            "last_transactions": last_txns,
            "total_sent_this_month":     total_sent,
            "total_received_this_month": total_received,
            "risk_events_this_week":     risk_events
        }

    except Exception as e:
        return {"error": str(e)}


# ----------------------------
# LEGACY USER PROFILE (unchanged — keeps frontend working)
# ----------------------------
@app.get("/api/user/profile")
def get_user_profile():
    return {
        "name": "Priya",
        "income": 55000,
        "goal": "buy a house in 7 years",
        "risk_appetite": "medium",
        "current_savings": 120000,
        "avg_investment": 5000,
        "investments_value": 60000
    }