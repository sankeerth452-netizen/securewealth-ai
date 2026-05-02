# PROJECT: SecureWealth Twin | v3.3
import os
import uuid
import random
import string
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from sqlalchemy import select

from database import get_db
from models import User, Account

router = APIRouter()

# ----------------------------
# CONFIG
# ----------------------------
JWT_SECRET    = os.getenv("JWT_SECRET", "devsecret-change-in-production-min32chars!!")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


# ----------------------------
# REQUEST / RESPONSE MODELS
# ----------------------------
class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str


# ----------------------------
# HELPERS
# ----------------------------
def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_jwt(user_id: str, email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS)
    payload = {"sub": str(user_id), "email": email, "exp": expire}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def generate_account_number() -> str:
    digits = ''.join(random.choices(string.digits, k=10))
    return f"NOVA{digits}"


# ----------------------------
# JWT DEPENDENCY
# ----------------------------
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"}
    )
    if not token:
        raise credentials_exc
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            raise credentials_exc
    except JWTError:
        raise credentials_exc

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise credentials_exc
    return user


# ----------------------------
# POST /api/auth/register
# ----------------------------
@router.post("/auth/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    print("Incoming data:", req.email)
    
    # Check duplicate email
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    print("Writing to DB (User)...")
    try:
        # Create user
        user = User(
            name=req.name,
            email=req.email,
            password_hash=hash_password(req.password)
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        print("Writing to DB (Account)...")
        # Create account with ₹1,00,000 starting balance
        account = Account(
            user_id=user.id,
            account_number=generate_account_number(),
            balance=100000.00
        )
        db.add(account)
        db.commit()
        db.refresh(account)
        
        print(f"[DB DEBUG] ✅ User and Account created: {user.email}")
    except Exception as e:
        db.rollback()
        print("DB WRITE ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))

    token = create_jwt(str(user.id), user.email)
    return {
        "user_id": str(user.id),
        "name": user.name,
        "email": user.email,
        "account_number": account.account_number,
        "balance": float(account.balance),
        "token": token
    }


# ----------------------------
# POST /api/auth/login
# ----------------------------
@router.post("/auth/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()

    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Fetch account
    account = db.query(Account).filter(Account.user_id == user.id).first()

    token = create_jwt(str(user.id), user.email)
    return {
        "user_id": str(user.id),
        "name": user.name,
        "email": user.email,
        "account_number": account.account_number if account else None,
        "balance": float(account.balance) if account else 0.0,
        "financial_profile": user.financial_profile or {},
        "token": token
    }

# ----------------------------
# TEST ROUTE
# ----------------------------
@router.get("/test-db-write")
def test_db_write(db: Session = Depends(get_db)):
    print("Testing DB write...")
    try:
        test_email = f"test_{uuid.uuid4().hex[:6]}@test.com"
        test = User(name="Test Bot", email=test_email, password_hash="123")
        db.add(test)
        db.commit()
        db.refresh(test)
        return {"message": "inserted", "email": test_email}
    except Exception as e:
        db.rollback()
        print("DB WRITE ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))
