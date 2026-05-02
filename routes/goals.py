# PROJECT: SecureWealth Twin | v3.2-production
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from decimal import Decimal
from typing import Optional
from datetime import datetime
import uuid

from database import get_db
from models import Goal
from routes.auth import get_current_user, User

router = APIRouter()

class GoalCreate(BaseModel):
    name: str
    target_amount: float
    target_date: Optional[datetime] = None

@router.post("/goals")
async def create_goal(
    req: GoalCreate, 
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    print("Incoming data:", req.dict())
    print("Writing to DB...")
    
    try:
        new_goal = Goal(
            user_id=current_user.id,
            name=req.name,
            target_amount=Decimal(str(req.target_amount)),
            current_amount=Decimal("0.00"),
            target_date=req.target_date
        )
        
        db.add(new_goal)
        await db.commit()
        await db.refresh(new_goal)
        
        print(f"[DB DEBUG] ✅ Goal created: {new_goal.name}")
        return {
            "goal_id": str(new_goal.id),
            "name": new_goal.name,
            "status": "success"
        }
    except Exception as e:
        await db.rollback()
        print("DB WRITE ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))
