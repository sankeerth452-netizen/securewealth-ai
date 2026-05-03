# PROJECT: SecureWealth Twin | v3.4
import os
import uuid
import random
import string
from datetime import datetime, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt

from database import get_db
from models import User, Account

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET    = os.getenv("JWT_SECRET", "fallback-secret-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24


import hashlib

def hash_password(password: str) -> str:
    """
    Safely hashes password by pre-hashing with SHA-256 
    to bypass bcrypt's 72-byte limitation.
    """
    hashed_input = hashlib.sha256(password.encode()).hexdigest()
    return pwd_context.hash(hashed_input)

def verify_password(plain: str, hashed: str) -> bool:
    """
    Verifies a plain password against a hash by pre-hashing 
    the plain password first.
    """
    hashed_input = hashlib.sha256(plain.encode()).hexdigest()
    return pwd_context.verify(hashed_input, hashed)

def create_token(user_id: str, email: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS)
    return jwt.encode(
        {"sub": user_id, "email": email, "exp": expire},
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )

def decode_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

def generate_account_number() -> str:
    return "NOVA" + "".join(random.choices(string.digits, k=10))


# ── REQUEST MODELS ────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    name:     str
    email:    str
    password: str

class LoginRequest(BaseModel):
    email:    str
    password: str

class TransferRequest(BaseModel):
    sender_account_number:   str
    recipient_account_number: str
    amount:                  float
    note:                    str = ""
    token:                   str  # JWT passed from frontend session


# ── REGISTER ──────────────────────────────────────────────────────────────────

from fastapi.responses import JSONResponse

@router.post("/register")
async def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """
    Production-ready registration endpoint.
    - Resolves bcrypt 72-byte limit with pre-hashing.
    - Hardened input validation and error responses.
    """
    try:
        # Log body (Safe for debugging, but be cautious with passwords in real logs)
        print("REGISTER BODY:", req.dict(exclude={"password"}))

        # 1. Validation
        if not req.email or "@" not in req.email:
            return JSONResponse(status_code=400, content={"error": "Invalid email address"})
        if not req.password or len(req.password) < 6:
            return JSONResponse(status_code=400, content={"error": "Password must be at least 6 characters"})
        if not req.name:
            return JSONResponse(status_code=400, content={"error": "Name is required"})

        if db is None:
            raise Exception("Database connection failed")

        # 2. Duplicate Check
        existing_user = db.query(User).filter(User.email == req.email).first()
        if existing_user:
            return JSONResponse(status_code=400, content={"error": "Email already registered"})

        # 3. Create User & Account
        user_id = str(uuid.uuid4())
        new_user = User(
            id=user_id,
            name=req.name,
            email=req.email,
            password_hash=hash_password(req.password),
        )
        db.add(new_user)
        
        new_account = Account(
            id=str(uuid.uuid4()),
            user_id=user_id,
            account_number=generate_account_number(),
            balance=Decimal("100000.00"),
        )
        db.add(new_account)
        db.commit()

        # 4. Success Response
        token = create_token(user_id, req.email)
        return {
            "success": True,
            "token": token,
            "user": {
                "id": user_id,
                "name": req.name,
                "email": req.email,
                "account_number": new_account.account_number,
                "balance": float(new_account.balance)
            }
        }

    except Exception as e:
        if db: db.rollback()
        print("REGISTER ERROR:", str(e))
        return JSONResponse(
            status_code=500,
            content={"error": "Registration failed", "details": str(e)}
        )


# ── LOGIN ─────────────────────────────────────────────────────────────────────

@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    if db is None:
        raise HTTPException(503, "Database unavailable")

    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")

    account = db.query(Account).filter(Account.user_id == user.id).first()

    print(f"[AUTH] Login: {user.email}")

    token = create_token(user.id, user.email)
    return {
        "token":          token,
        "user_id":        user.id,
        "name":           user.name,
        "email":          user.email,
        "account_number": account.account_number if account else "",
        "balance":        float(account.balance) if account else 0,
        "message":        "Login successful",
    }


# ── ME ────────────────────────────────────────────────────────────────────────

@router.get("/me")
def get_me(token: str, db: Session = Depends(get_db)):
    if db is None:
        raise HTTPException(503, "Database unavailable")
    try:
        payload = decode_token(token)
        user_id = payload["sub"]
    except Exception:
        raise HTTPException(401, "Invalid or expired token")

    user    = db.query(User).filter(User.id == user_id).first()
    account = db.query(Account).filter(Account.user_id == user_id).first()

    if not user:
        raise HTTPException(404, "User not found")

    return {
        "user_id":        user.id,
        "name":           user.name,
        "email":          user.email,
        "account_number": account.account_number if account else "",
        "balance":        float(account.balance) if account else 0,
    }

# ── TRANSFER ──────────────────────────────────────────────────────────────────

@router.post("/transfer")
def do_transfer(req: TransferRequest, db: Session = Depends(get_db)):
    if db is None:
        raise HTTPException(503, "Database unavailable")

    # Verify token
    try:
        payload = decode_token(req.token)
    except Exception:
        raise HTTPException(401, "Invalid token")

    sender_acc    = db.query(Account).filter(Account.account_number == req.sender_account_number).first()
    recipient_acc = db.query(Account).filter(Account.account_number == req.recipient_account_number).first()

    if not sender_acc:
        raise HTTPException(404, "Sender account not found")
    if not recipient_acc:
        raise HTTPException(404, "Recipient account not found")
    if sender_acc.id == recipient_acc.id:
        raise HTTPException(400, "Cannot transfer to yourself")

    amount = Decimal(str(req.amount))
    if amount <= 0:
        raise HTTPException(400, "Amount must be positive")
    if sender_acc.balance < amount:
        raise HTTPException(400, "Insufficient balance")

    # Execute transfer
    sender_acc.balance    -= amount
    recipient_acc.balance += amount

    from models import Transaction
    txn = Transaction(
        id=str(uuid.uuid4()),
        sender_id=sender_acc.id,
        receiver_id=recipient_acc.id,
        amount=amount,
        note=req.note,
        status="completed",
    )
    db.add(txn)
    db.commit()

    print(f"[DB] ✅ Transfer saved: ₹{amount} | {sender_acc.account_number} → {recipient_acc.account_number}")

    return {
        "status":          "success",
        "transaction_id":  txn.id,
        "amount":          float(amount),
        "sender_balance":  float(sender_acc.balance),
        "message":         f"₹{amount:,.2f} transferred successfully",
    }


# ── RE-EXPORTS & DEPENDENCIES ──────────────────────────────────────────────────

from models import User  # noqa — re-export for other routes
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    FastAPI dependency. Decodes JWT and returns the User from DB.
    Raises 401 if token is missing, expired, or invalid.
    """
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload  = decode_token(token)
        user_id  = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except Exception:
        raise HTTPException(status_code=401, detail="Token expired or invalid")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
