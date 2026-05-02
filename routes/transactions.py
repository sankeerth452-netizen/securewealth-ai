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
from routes.auth import get_current_user, User

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

@router.get("/transactions")
def get_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from models import Account, Transaction
    account = db.query(Account).filter(Account.user_id == current_user.id).first()
    if not account:
        return {"transactions": []}
    txns = db.query(Transaction).filter(
        (Transaction.sender_id == account.id) | (Transaction.receiver_id == account.id)
    ).order_by(Transaction.timestamp.desc()).limit(50).all()
    return {
        "transactions": [
            {
                "id":        t.id,
                "amount":    float(t.amount),
                "note": t.note,
                "status": t.status,
                "type": "sent" if t.sender_id == account.id else "received",
                "timestamp": t.timestamp.isoformat(),
                "risk_score": t.risk_score,
                "risk_decision": t.risk_decision,
            }
            for t in txns
        ]
    }
