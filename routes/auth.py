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


# ── HELPERS ───────────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

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

@router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if db is None:
        raise HTTPException(503, "Database unavailable")

    # Check duplicate email
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(400, "Email already registered")

    # Create user
    user = User(
        id=str(uuid.uuid4()),
        name=req.name,
        email=req.email,
        password_hash=hash_password(req.password),
    )
    db.add(user)
    db.flush()  # Get user.id without full commit yet

    # Create account with starting balance
    account = Account(
        id=str(uuid.uuid4()),
        user_id=user.id,
        account_number=generate_account_number(),
        balance=Decimal("100000.00"),
    )
    db.add(account)
    db.commit()
    db.refresh(user)
    db.refresh(account)

    print(f"[AUTH] Registered user: {user.email} | account: {account.account_number}")

    token = create_token(user.id, user.email)
    return {
        "token":          token,
        "user_id":        user.id,
        "name":           user.name,
        "email":          user.email,
        "account_number": account.account_number,
        "balance":        float(account.balance),
        "message":        "Account created successfully",
    }


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
