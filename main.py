# PROJECT: SecureWealth Twin | v3.4
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import create_all_tables, check_db_connection

FRONTEND_URL = os.getenv("FRONTEND_URL", "https://securewealth-ai.vercel.app")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 SecureWealth Twin API starting...")
    tables_ok = create_all_tables()       # sync call — no await needed
    db_ok     = check_db_connection()     # sync call — no await needed
    print(f"[DB] Tables: {'✅' if tables_ok else '❌'}  Connection: {'✅' if db_ok else '❌'}")
    yield
    print("SecureWealth Twin shutting down")

app = FastAPI(title="SecureWealth Twin", version="3.4", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5000",
        "http://127.0.0.1:5000",
        "https://securewealth-ai.vercel.app",
        FRONTEND_URL,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Router Inclusions ---
from routes import chat, risk, simulate, aggregator, networth, profile, execution, auth, transactions, goals

app.include_router(chat.router,         prefix="/api/ai",  tags=["AI Chat"])
app.include_router(simulate.router,     prefix="/api/ai",  tags=["Simulation"])
app.include_router(aggregator.router,   prefix="/api/ai",  tags=["Aggregator"])
app.include_router(networth.router,     prefix="/api/ai",  tags=["Net Worth"])
app.include_router(profile.router,      prefix="/api/ai",  tags=["Profile"])
app.include_router(risk.router,         prefix="/api",     tags=["Risk Engine"])
app.include_router(execution.router,    prefix="/api",     tags=["Execution Engine"])
app.include_router(auth.router,         prefix="/api/auth",tags=["Auth"])
app.include_router(transactions.router, prefix="/api",     tags=["Transactions"])
app.include_router(goals.router,        prefix="/api",     tags=["Goals"])

@app.get("/")
def root():
    return {"status": "SecureWealth Twin v3.4 running ✅"}

@app.get("/health")
def health():
    db_ok     = check_db_connection()
    tables_ok = False
    if db_ok:
        from database import SessionLocal
        from sqlalchemy import text
        db = SessionLocal()
        try:
            r = db.execute(text(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name='users')"
            ))
            tables_ok = r.scalar()
        finally:
            db.close()
    return {
        "status":         "healthy",
        "db":             "connected" if db_ok else "offline",
        "tables_created": tables_ok,
        "agents":         7,
        "version":        "3.4",
    }