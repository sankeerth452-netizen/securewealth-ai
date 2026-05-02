# PROJECT: SecureWealth Twin | v3.0-production
import datetime
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from routes.risk import calculate_risk_score, get_decision, get_level, generate_reason, RiskRequest, build_trust_pyramid
from routes.simulate import calculate_sip
from routes.user_history import init_login_time, add_transaction, USER_HISTORY
from database import get_db
from models import RiskAuditLog

router = APIRouter()

# Standalone in-memory audit log (fallback)
audit_log = []


# -----------------------------
# REQUEST MODEL
# -----------------------------
class ExecuteRequest(BaseModel):
    action_type: str
    amount: float

    avg_amount: float
    is_new_device: bool = False
    seconds_since_login: int = 60
    is_first_investment_type: bool = False
    otp_retry_count: int = 0
    hour_of_day: Optional[int] = None
    is_round_number: Optional[bool] = None
    first_time_count: int = 0

    monthly_amount: Optional[float] = None
    years: Optional[int] = None
    expected_return: float = 12.0

    user_profile: Optional[Dict[str, Any]] = None
    transaction_id: Optional[str] = None  # NEW: optional DB transaction ref


# -----------------------------
# HELPERS
# -----------------------------
def normalize_score(score: int) -> int:
    return min(score, 100)


def generate_simulation(amount: float, years: int, rate: float) -> dict:
    months = years * 12
    data = calculate_sip(amount, months, rate)
    later_data = calculate_sip(amount, max(months - 12, 1), rate)

    final_now   = data[-1]["value"]       if data       else 0
    final_later = later_data[-1]["value"] if later_data else 0
    opportunity_cost = round(final_now - final_later)

    return {
        "projection":       data,
        "start_later":      later_data,
        "final_value":      final_now,
        "opportunity_cost": opportunity_cost,
        "nudge_message":    f"Starting 1 year later costs you ₹{opportunity_cost:,}",
        "summary":          f"Investing ₹{amount:,.0f}/month for {years} years could grow to ₹{final_now:,.0f}"
    }


def generate_ai_nudge(req: ExecuteRequest, risk_level: str) -> str:
    if risk_level == "HIGH":
        return "⚠️ This action is significantly unusual for your account. Please review carefully."
    if req.amount > req.avg_amount * 2:
        return "📊 This is higher than your usual investment amount."
    if req.seconds_since_login < 10:
        return "⏱️ You're acting very quickly after login — take a moment to review."
    return "✅ This action aligns with your normal financial behavior."


async def write_audit_log(db, entry: dict):
    """Write to DB audit log. Silently falls back if DB unavailable."""
    if db is None:
        return
    try:
        from models import RiskAuditLog
        from decimal import Decimal
        import json
        log = RiskAuditLog(
            action_type=entry.get("action_type", "unknown"),
            amount=Decimal(str(entry.get("amount", 0))),
            risk_score=entry.get("risk_score", 0),
            level=entry.get("level", ""),
            decision=entry.get("decision", ""),
            reason=entry.get("reason", ""),
            signals=entry.get("signals", []),
            trust_pyramid=entry.get("trust_pyramid", {}),
        )
        db.add(log)
        await db.commit()
        print(f"[DB] Audit log written: {entry.get('decision')} score={entry.get('risk_score')}")
    except Exception as e:
        print(f"[DB] Audit log write failed (non-critical): {e}")


# -----------------------------
# MAIN EXECUTION ENDPOINT
# -----------------------------
@router.post("/execute")
async def execute_action(req: ExecuteRequest, db: AsyncSession = Depends(get_db)):
    init_login_time()

    req.avg_amount = USER_HISTORY["avg_transaction"]

    current_hour = req.hour_of_day if req.hour_of_day is not None \
                   else datetime.datetime.now().hour

    is_round = req.is_round_number if req.is_round_number is not None \
               else (req.amount % 10000 == 0)

    # ── STEP 1: BUILD RISK REQUEST ──────────────
    risk_req = RiskRequest(
        action_type=req.action_type,
        amount=req.amount,
        avg_amount=req.avg_amount,
        is_new_device=req.is_new_device,
        seconds_since_login=req.seconds_since_login,
        is_first_investment_type=req.is_first_investment_type,
        otp_retry_count=req.otp_retry_count,
        hour_of_day=current_hour,
        is_round_number=is_round,
        first_time_count=req.first_time_count
    )

    # ── STEP 2: RISK ANALYSIS ───────────────────
    score, signals = calculate_risk_score(risk_req)
    score    = normalize_score(score)
    decision = get_decision(score)
    level    = get_level(score)
    reason   = generate_reason(risk_req, score, signals, decision)
    pyramid  = build_trust_pyramid(signals)

    # ── STEP 3: IN-MEMORY AUDIT LOG ─────────────
    print("Decision:", decision)
    print("Score:", score)

    audit_entry = {
        "timestamp":   datetime.datetime.now().isoformat(),
        "action_type": req.action_type,
        "amount":      req.amount,
        "signals":     signals,
        "risk_score":  score,
        "level":       level,
        "decision":    decision,
        "reason":      reason,
        "trust_pyramid": pyramid
    }
    audit_log.append(audit_entry)

    # ── STEP 3b: DB AUDIT WRITE ─────────────────
    await write_audit_log(db, audit_entry)

    # ── STEP 4: BASE RESPONSE ───────────────────
    response = {
        "action_type": req.action_type,
        "amount":      req.amount,
        "timestamp":   datetime.datetime.now().isoformat(),
        "risk": {
            "score":         score,
            "level":         level,
            "decision":      decision,
            "reason":        reason,
            "signals":       signals,
            "trust_pyramid": pyramid
        }
    }

    # ── STEP 5: OUTCOME ─────────────────────────
    monthly = req.monthly_amount or (req.amount / 10)
    years   = req.years or 10

    if decision == "BLOCK":
        cd = 10
        response["status"]         = "blocked"
        response["message"]        = f"Action temporarily blocked. Try again after {cd} seconds."
        response["next_step"]      = "Please contact your bank or try again after 24 hours."
        response["cooldown"]       = cd
        response["nudge"]          = generate_ai_nudge(req, level)
        response["recommendation"] = f"Try investing ₹10,000 first or wait {cd*2} seconds before retrying."
        return response

    elif decision == "WARN":
        cd = 5
        response["status"]             = "delayed"
        response["message"]            = f"Please wait {cd} seconds before proceeding."
        response["cooldown"]           = cd
        response["nudge"]              = generate_ai_nudge(req, level)
        response["simulation_preview"] = generate_simulation(monthly, years, req.expected_return)
        response["recommendation"]     = "Proceed with a smaller amount or confirm after the cooldown."
        return response

    else:
        add_transaction(req.amount)
        response["status"]     = "approved"
        response["message"]    = "Action approved successfully."
        response["nudge"]      = generate_ai_nudge(req, level)
        response["simulation"] = generate_simulation(monthly, years, req.expected_return)
        return response


# -----------------------------
# SIMULATE FRAUD ENDPOINT
# -----------------------------
@router.post("/simulate/fraud")
async def simulate_fraud(db: AsyncSession = Depends(get_db)):
    req = ExecuteRequest(
        action_type="High-Value Investment",
        amount=500000.0,
        avg_amount=USER_HISTORY["avg_transaction"],
        is_new_device=True,
        seconds_since_login=3,
        otp_retry_count=3,
        hour_of_day=2,
        is_round_number=True,
        is_first_investment_type=True
    )
    res = await execute_action(req, db)
    res["ai_explanation"] = "⚠️ Suspicious activity detected — action blocked to protect you."
    return res


# -----------------------------
# AUDIT LOG ENDPOINT
# -----------------------------
@router.get("/execute/audit")
async def get_execution_audit(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(RiskAuditLog).order_by(desc(RiskAuditLog.timestamp)).limit(20)
        )
        logs = result.scalars().all()
        if logs:
            return {
                "total_evaluations": len(logs),
                "log": [{
                    "timestamp":   log.timestamp.isoformat(),
                    "action_type": log.action_type,
                    "amount":      float(log.amount) if log.amount else 0.0,
                    "risk_score":  log.risk_score,
                    "level":       log.level,
                    "decision":    log.decision,
                    "signals":     log.signals or [],
                    "reason":      log.reason
                } for log in reversed(logs)]
            }
    except Exception as e:
        print(f"[DB] Audit log fallback to in-memory: {e}")

    return {
        "total_evaluations": len(audit_log),
        "log": audit_log[-20:]
    }