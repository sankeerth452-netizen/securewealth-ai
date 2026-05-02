from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


# -----------------------------
# REQUEST MODEL
# -----------------------------
class NetWorthRequest(BaseModel):
    savings: float
    investments: float
    property_value: Optional[float] = 0
    gold_value: Optional[float] = 0
    vehicle_value: Optional[float] = 0
    other_assets: Optional[float] = 0
    loans: Optional[float] = 0
    credit_card_debt: Optional[float] = 0


# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def calculate_health_score(assets: float, liabilities: float, investments: float, savings: float):
    score = 100
    insights = []

    # Debt penalty
    if liabilities > assets * 0.5:
        score -= 30
        insights.append("High debt compared to assets")

    elif liabilities > assets * 0.3:
        score -= 15
        insights.append("Moderate debt level")

    # Investment ratio
    if assets > 0:
        invest_ratio = investments / assets

        if invest_ratio < 0.2:
            score -= 20
            insights.append("Low investment allocation")

        elif invest_ratio > 0.7:
            score -= 10
            insights.append("Overexposed to investments")

    # Savings idle check
    if savings > investments * 2:
        score -= 10
        insights.append("Too much idle cash, consider investing")

    # Normalize
    score = max(0, min(score, 100))

    # Status
    if score >= 75:
        status = "Excellent"
    elif score >= 60:
        status = "Good"
    elif score >= 40:
        status = "Average"
    else:
        status = "Needs Attention"

    return score, status, insights


def calculate_distribution(req: NetWorthRequest, total_assets: float):
    if total_assets == 0:
        return {}

    return {
        "savings_%": round((req.savings / total_assets) * 100, 1),
        "investments_%": round((req.investments / total_assets) * 100, 1),
        "property_%": round((req.property_value / total_assets) * 100, 1),
        "gold_%": round((req.gold_value / total_assets) * 100, 1),
        "vehicles_%": round((req.vehicle_value / total_assets) * 100, 1),
        "other_%": round((req.other_assets / total_assets) * 100, 1),
    }


def generate_suggestions(insights: list):
    suggestions = []

    for i in insights:
        if "debt" in i.lower():
            suggestions.append("Focus on reducing high-interest debt first")

        if "investment" in i.lower():
            suggestions.append("Increase SIP contributions for long-term growth")

        if "idle cash" in i.lower():
            suggestions.append("Move excess savings into investments or FD")

    return list(set(suggestions))  # remove duplicates


# -----------------------------
# MAIN API
# -----------------------------
@router.post("/networth")
def calculate_networth(req: NetWorthRequest):

    # --- CALCULATIONS ---
    total_assets = (
        req.savings + req.investments + req.property_value +
        req.gold_value + req.vehicle_value + req.other_assets
    )

    total_liabilities = req.loans + req.credit_card_debt
    net_worth = total_assets - total_liabilities

    # --- HEALTH SCORE ---
    score, status, insights = calculate_health_score(
        total_assets,
        total_liabilities,
        req.investments,
        req.savings
    )

    # --- DISTRIBUTION ---
    distribution = calculate_distribution(req, total_assets)

    # --- SUGGESTIONS ---
    suggestions = generate_suggestions(insights)

    return {
        "summary": {
            "total_assets": total_assets,
            "total_liabilities": total_liabilities,
            "net_worth": net_worth
        },

        "health_score": {
            "score": score,
            "status": status
        },

        "breakdown": {
            "savings": req.savings,
            "investments": req.investments,
            "property": req.property_value,
            "gold": req.gold_value,
            "vehicles": req.vehicle_value,
            "other": req.other_assets
        },

        "distribution_percent": distribution,

        "insights": insights,
        "suggestions": suggestions,

        "note": "For simulation purposes only"
    }