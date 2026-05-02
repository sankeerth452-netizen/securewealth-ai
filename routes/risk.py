# PROJECT: SecureWealth Twin | v3.3
import os
import datetime
import time
from dotenv import load_dotenv
load_dotenv()

from groq import Groq
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from database import get_db
from models import RiskAuditLog
from routes.user_history import USER_HISTORY

api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None
router = APIRouter()

WEIGHTS = {
    "new_device":            25,
    "fast_action":           20,
    "night_activity":        20,
    "high_amount":           30,
    "first_time_investment": 15,
    "otp_retries":           20,
    "round_number":          15,
    "multiple_firsts":       25
}

MAX_SCORE = 100
audit_log = []

class RiskRequest(BaseModel):
    action_type: str
    amount: float
    avg_amount: float
    is_new_device: bool
    seconds_since_login: int
    is_first_investment_type: bool
    otp_retry_count: int
    hour_of_day: int          = 12
    is_round_number: bool     = False
    first_time_count: int     = 0

def calculate_risk_score(req: RiskRequest) -> tuple[int, list]:
    req.avg_amount = USER_HISTORY["avg_transaction"]
    score   = 0
    signals = []
    if req.amount > 3 * req.avg_amount:
        score += 30
        signals.append("Amount unusually high compared to your normal transactions")
    login_time = USER_HISTORY.get("login_time")
    if login_time:
        time_since_login = time.time() - login_time
        if time_since_login < 10:
            score += 20
            signals.append("Action performed too quickly after login")
    if USER_HISTORY.get("trusted_device") is False:
        score += 20
        signals.append("New or untrusted device detected")
    last_txs = USER_HISTORY.get("last_transactions", [])
    if len(last_txs) >= 3:
        similar_count = sum(1 for tx in last_txs[-3:] if abs(tx - req.amount) < (req.amount * 0.1))
        if similar_count == 3:
            score += 10
            signals.append("Repeated transaction pattern detected")
    if 0 <= req.hour_of_day <= 5:
        score += WEIGHTS.get("night_activity", 20)
        signals.append(f"Unusual time: {req.hour_of_day}:00 AM")
    if req.otp_retry_count > 1:
        score += WEIGHTS.get("otp_retries", 20)
        signals.append(f"{req.otp_retry_count} OTP retries detected")
    if req.is_round_number:
        score += WEIGHTS.get("round_number", 10)
        signals.append("Round number amount (possible external influence)")
    score = min(score, 100)
    return score, signals

def build_trust_pyramid(signals: list) -> dict:
    return {
        "identity": any("device" in s.lower() for s in signals),
        "context":  any("quickly" in s.lower() or "time" in s.lower() or "login" in s.lower() for s in signals),
        "behavior": any("pattern" in s.lower() or "usual" in s.lower() or "transaction" in s.lower() for s in signals),
        "intent":   any("otp" in s.lower() or "round" in s.lower() or "first-time" in s.lower() for s in signals)
    }

def get_decision(score: int) -> str:
    if score < 30: return "ALLOW"
    if score < 60: return "WARN"
    return "BLOCK"

def get_level(score: int) -> str:
    if score < 30: return "LOW"
    if score < 60: return "MEDIUM"
    return "HIGH"

def generate_reason(req: RiskRequest, score: int, signals: list, decision: str) -> str:
    if decision == "ALLOW":
        return "This action matches your normal behavior and appears safe."
    tone = ""
    if decision == "BLOCK":
        tone = "This action appears highly unusual and has been blocked to protect your account. "
    elif decision == "WARN":
        tone = "This action shows some unusual patterns. Please review before proceeding. "
    parts = []
    if req.avg_amount > 0:
        multiplier = req.amount / req.avg_amount
        if multiplier > 1.5:
            parts.append(f"this transaction of ₹{req.amount:,.0f} is {multiplier:.1f}× higher than your usual ₹{req.avg_amount:,.0f}")
    login_time = USER_HISTORY.get("login_time")
    if login_time:
        tsl = round(time.time() - login_time)
        if tsl < 30:
            parts.append(f"was initiated within {tsl}s of login")
    if not parts:
        if signals:
            combined = " and ".join([s.lower() for s in signals[:2]])
            return f"{tone}We noticed {combined}."
        return f"{tone}This action deviates from your typical patterns."
    if len(parts) == 1:
        explanation = parts[0]
    else:
        explanation = f"{parts[0]}, and {parts[1]}"
    return f"{tone}We noticed {explanation}."

@router.post("/risk/check")
def risk_check(req: RiskRequest, db: Session = Depends(get_db)):
    score, signals = calculate_risk_score(req)
    decision = get_decision(score)
    level    = get_level(score)
    reason   = generate_reason(req, score, signals, decision)
    pyramid  = build_trust_pyramid(signals)

    record = {
        "timestamp":     datetime.datetime.now().isoformat(),
        "action_type":   req.action_type,
        "amount":        req.amount,
        "risk_score":    score,
        "level":         level,
        "decision":      decision,
        "signals":       signals,
        "trust_pyramid": pyramid,
        "reason":        reason
    }
    audit_log.append(record)

    if db:
        try:
            from decimal import Decimal
            new_audit = RiskAuditLog(
                action_type=req.action_type,
                amount=Decimal(str(req.amount)),
                risk_score=score,
                level=level,
                decision=decision,
                reason=reason,
                signals=signals,
                trust_pyramid=pyramid
            )
            db.add(new_audit)
            db.commit()
            print(f"[DB DEBUG] ✅ RiskAuditLog written for score={score}")
        except Exception as e:
            if db: db.rollback()
            print(f"[DB ERROR] ❌ Failed to write RiskAuditLog to DB: {e}")

    return {
        "risk_score":    score,
        "level":         level,
        "decision":      decision,
        "reason":        reason,
        "signals":       signals,
        "trust_pyramid": pyramid,
        "message": (
            "Action approved" if decision == "ALLOW"
            else "Additional verification recommended" if decision == "WARN"
            else "Action temporarily blocked for safety"
        )
    }

@router.get("/risk/audit")
def get_audit_log(db: Session = Depends(get_db)):
    if db:
        try:
            logs = db.query(RiskAuditLog).order_by(RiskAuditLog.timestamp.desc()).limit(50).all()
            if logs:
                return {
                    "total_evaluations": len(logs),
                    "recent": [{
                        "id": str(log.id),
                        "action_type": log.action_type,
                        "amount": float(log.amount) if log.amount else 0.0,
                        "risk_score": log.risk_score,
                        "level": log.level,
                        "decision": log.decision,
                        "reason": log.reason,
                        "signals": log.signals,
                        "trust_pyramid": log.trust_pyramid,
                        "timestamp": log.timestamp.isoformat()
                    } for log in reversed(logs)]
                }
        except Exception as e:
            print(f"DB read error: {e}")
    
    return {
        "total_evaluations": len(audit_log),
        "recent": audit_log[-20:]
    }