# PROJECT: SecureWealth Twin | v3.2-production
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
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
async def create_transaction(data: TransactionCreate, db: AsyncSession = Depends(get_db)):
    try:
        print("🔥 ENDPOINT HIT: /api/transactions")
        print("📥 Incoming data:", data)

        # Map string IDs to UUIDs if provided
        s_id = uuid.UUID(data.sender_id) if data.sender_id else None
        r_id = uuid.UUID(data.receiver_id) if data.receiver_id else None

        new_txn = Transaction(
            sender_id=s_id,
            receiver_id=r_id,
            amount=Decimal(str(data.amount)),
            note=data.note,
            status="completed"
        )

        print("🛠 Creating DB object")

        db.add(new_txn)

        print("💾 Committing...")
        await db.commit()

        print("✅ Commit done")

        await db.refresh(new_txn)

        print("🎉 Insert success:", new_txn.id)

        return {
            "success": True,
            "transaction_id": str(new_txn.id)
        }

    except Exception as e:
        print("❌ INSERT FAILED:", str(e))
        traceback.print_exc()
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
