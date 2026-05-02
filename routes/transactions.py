# PROJECT: SecureWealth Twin | v3.3
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from decimal import Decimal
from typing import Optional
import uuid
import traceback

from database import get_db
from models import Transaction

router = APIRouter()

class TransactionCreate(BaseModel):
    sender_id: Optional[str] = None
    receiver_id: Optional[str] = None
    amount: float
    note: Optional[str] = "Transfer"

@router.post("/transactions")
def create_transaction(data: TransactionCreate, db: Session = Depends(get_db)):
    try:
        print("🔥 ENDPOINT HIT: /api/transactions")
        print("📥 Incoming data:", data)

        new_txn = Transaction(
            sender_id=data.sender_id,
            receiver_id=data.receiver_id,
            amount=Decimal(str(data.amount)),
            note=data.note,
            status="completed"
        )

        print("🛠 Creating DB object")
        db.add(new_txn)

        print("💾 Committing...")
        db.commit()

        print("✅ Commit done")
        db.refresh(new_txn)

        print("🎉 Insert success:", new_txn.id)

        return {
            "success": True,
            "transaction_id": str(new_txn.id)
        }

    except Exception as e:
        print("❌ INSERT FAILED:", str(e))
        traceback.print_exc()
        if db:
            db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
