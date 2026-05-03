# PROJECT: SecureWealth Twin | v3.6
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import create_all_tables, check_db_connection

FRONTEND_URL = os.getenv("FRONTEND_URL", "").rstrip('/')

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 SecureWealth Twin API starting...")
    tables_ok = create_all_tables()
    db_ok     = check_db_connection()
    print(f"[DB] Tables: {'✅' if tables_ok else '❌'}  Connection: {'✅' if db_ok else '❌'}")
    yield
    print("SecureWealth Twin shutting down")

app = FastAPI(title="SecureWealth Twin", version="3.6", lifespan=lifespan)

# Build allowed origins
allowed_origins = [
    "http://localhost:5000",
    "http://127.0.0.1:5000",
    "http://localhost:3000",
    "https://securewealth-ai.vercel.app",
]
if FRONTEND_URL:
    allowed_origins.append(FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",  # Allow ALL vercel.app subdomains
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# --- Router Inclusions ---
from routes import chat, risk, simulate, aggregator, networth, profile, execution, auth, transactions, goals

app.include_router(chat.router,         prefix="/api/ai",  tags=["AI Chat"])
app.include_router(simulate.router,     prefix="/api/ai",  tags=["Simulation"])
app.include_router(aggregator.router,   prefix="/api/ai",  tags=["Aggregator"])
app.include_router(networth.router,     prefix="/api/ai",  tags=["Net Worth"])
app.include_router(profile.router,      prefix="/api",     tags=["Profile"])
app.include_router(risk.router,         prefix="/api",     tags=["Risk Engine"])
app.include_router(execution.router,    prefix="/api",     tags=["Execution Engine"])
app.include_router(auth.router,         prefix="/api/auth",tags=["Auth"])
app.include_router(transactions.router, prefix="/api",     tags=["Transactions"])
app.include_router(goals.router,        prefix="/api",     tags=["Goals"])

@app.get("/")
def root():
    return {"status": "SecureWealth Twin v3.6 running ✅"}

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
        "version":        "3.6",
    }