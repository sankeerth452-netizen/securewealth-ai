from fastapi import APIRouter
from pydantic import BaseModel
import math

router = APIRouter()

# -----------------------------
# REQUEST MODEL
# -----------------------------
class SimulateRequest(BaseModel):
    monthly_amount: float = 0
    years: int
    annual_rate: float = 12.0
    goal_amount: float = 0   # NEW (optional goal-based simulation)


# -----------------------------
# SIP CALCULATION
# -----------------------------
def calculate_sip(monthly: float, months: int, rate: float) -> list:
    monthly_rate = rate / (12 * 100)
    data = []
    total_invested = 0

    for m in range(1, months + 1):
        total_invested += monthly

        value = monthly * (
            (((1 + monthly_rate) ** m) - 1) / monthly_rate
        ) * (1 + monthly_rate)

        if m % 6 == 0 or m == 1:
            data.append({
                "month": m,
                "invested": round(total_invested),
                "value": round(value)
            })

    return data


# -----------------------------
# GOAL-BASED CALCULATION
# -----------------------------
def calculate_required_sip(goal: float, months: int, rate: float):
    monthly_rate = rate / (12 * 100)

    if monthly_rate == 0:
        return goal / months

    sip = goal / (
        (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)
    )

    return round(sip)


# -----------------------------
# MAIN API
# -----------------------------
@router.post("/simulate")
def simulate(req: SimulateRequest):
    total_months = req.years * 12

    # -----------------------------
    # CASE 1: GOAL-BASED SIMULATION
    # -----------------------------
    if req.goal_amount > 0:
        required_sip = calculate_required_sip(
            req.goal_amount,
            total_months,
            req.annual_rate
        )

        projection = calculate_sip(
            required_sip,
            total_months,
            req.annual_rate
        )

        final_value = projection[-1]["value"] if projection else 0

        return {
            "type": "goal_based",
            "goal_amount": req.goal_amount,
            "required_monthly_investment": required_sip,
            "projection": projection,
            "summary": {
                "target": req.goal_amount,
                "achieved": final_value,
                "message": f"To reach ₹{req.goal_amount:,.0f}, invest ₹{required_sip:,}/month"
            }
        }

    # -----------------------------
    # CASE 2: NORMAL SIP SIMULATION
    # -----------------------------
    start_now = calculate_sip(
        req.monthly_amount,
        total_months,
        req.annual_rate
    )

    start_later = calculate_sip(
        req.monthly_amount,
        total_months - 12,
        req.annual_rate
    )

    final_now = start_now[-1]["value"] if start_now else 0
    final_later = start_later[-1]["value"] if start_later else 0

    total_invested = req.monthly_amount * total_months
    wealth_gain = final_now - total_invested
    opportunity_cost = final_now - final_later

    return {
        "type": "sip_projection",
        "start_now": start_now,
        "start_later": start_later,
        "summary": {
            "invested": total_invested,
            "final_value_now": final_now,
            "final_value_later": final_later,
            "wealth_gain": wealth_gain,
            "opportunity_cost": opportunity_cost,
            "nudge": f"Delaying by 1 year costs ₹{opportunity_cost:,.0f}",
            "insight": (
                "Compounding rewards early investing. Even small delays reduce long-term wealth."
            )
        }
    }