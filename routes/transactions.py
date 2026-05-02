# PROJECT: SecureWealth Twin | v3.2-production
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from decimal import Decimal
from typing import Optional
import uuid

from database import get_db
from models import Transaction, Account
from routes.auth import get_current_user, User

router = APIRouter()

class TransactionCreate(BaseModel):
    recipient_account: str
    amount: float
    note: Optional[str] = "Transfer"

@router.post("/transactions")
async def create_transaction(
    req: TransactionCreate, 
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    print("Incoming data:", req.dict())
    
    # 1. Get sender account
    acc_res = await db.execute(
        Account.__table__.select().where(Account.user_id == current_user.id)
    )
    # Using raw table select for quick check or models
    from sqlalchemy import select
    acc_res = await db.execute(select(Account).where(Account.user_id == current_user.id))
    sender_account = acc_res.scalar_one_or_none()
    
    if not sender_account:
        raise HTTPException(status_code=404, detail="Sender account not found")
        
    if sender_account.balance < req.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    print("Writing to DB...")
    try:
        # 2. Create transaction record
        new_tx = Transaction(
            sender_id=sender_account.id,
            amount=Decimal(str(req.amount)),
            note=req.note,
            status="completed"
        )
        
        # 3. Update balance
        sender_account.balance -= Decimal(str(req.amount))
        
        db.add(new_tx)
        await db.commit()
        await db.refresh(new_tx)
        
        print(f"[DB DEBUG] ✅ Transaction created: {new_tx.id}")
        return {
            "transaction_id": str(new_tx.id),
            "new_balance": float(sender_account.balance),
            "status": "success"
        }
    except Exception as e:
        await db.rollback()
        print("DB WRITE ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))
