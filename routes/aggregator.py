import os
from dotenv import load_dotenv
load_dotenv()

from groq import Groq
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
router = APIRouter()


# -----------------------------
# REQUEST MODEL
# -----------------------------
class AggregatorRequest(BaseModel):
    user_profile: dict
    external_accounts: List[Dict]  # [{bank, type, balance}]


# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def analyze_accounts(accounts: List[Dict]):
    total_balance = sum(acc.get("balance", 0) for acc in accounts)

    breakdown = {}
    idle_cash = 0
    investments = 0

    for acc in accounts:
        acc_type = acc.get("type", "other")
        balance = acc.get("balance", 0)

        breakdown[acc_type] = breakdown.get(acc_type, 0) + balance

        if acc_type in ["savings", "current"]:
            idle_cash += balance
        elif acc_type in ["investment", "mutual_fund", "stocks"]:
            investments += balance

    distribution = {
        k: round((v / total_balance) * 100, 1) if total_balance else 0
        for k, v in breakdown.items()
    }

    return total_balance, breakdown, distribution, idle_cash, investments


def generate_rule_based_insights(idle_cash, investments, total_balance):
    insights = []

    if total_balance == 0:
        return insights

    # Idle cash check
    if idle_cash > investments * 1.5:
        insights.append("Large portion of funds are idle in savings accounts")

    # Low investment ratio
    if investments / total_balance < 0.25:
        insights.append("Low exposure to investments across accounts")

    # Over-diversification
    if total_balance > 0 and idle_cash > total_balance * 0.7:
        insights.append("Excess liquidity — funds not working efficiently")

    return insights


def generate_suggestions(insights):
    suggestions = []

    for i in insights:
        if "idle" in i.lower():
            suggestions.append("Move excess savings into SIPs or fixed deposits")

        if "low exposure" in i.lower():
            suggestions.append("Increase investment allocation gradually")

        if "liquidity" in i.lower():
            suggestions.append("Rebalance funds to improve returns")

    return list(set(suggestions))


# -----------------------------
# MAIN API
# -----------------------------
@router.post("/aggregate")
def aggregate_wealth(req: AggregatorRequest):

    # -----------------------------
    # ANALYSIS
    # -----------------------------
    total_balance, breakdown, distribution, idle_cash, investments = analyze_accounts(
        req.external_accounts
    )

    insights = generate_rule_based_insights(
        idle_cash, investments, total_balance
    )

    suggestions = generate_suggestions(insights)

    # -----------------------------
    # AI LAYER (ENHANCEMENT)
    # -----------------------------
    prompt = f"""
User has multiple bank accounts.

Total balance: ₹{total_balance}
Idle cash: ₹{idle_cash}
Investments: ₹{investments}

Profile:
Income: ₹{req.user_profile.get('income')}
Goal: {req.user_profile.get('goal')}

Insights:
{insights}

Give 2 short, actionable recommendations for optimizing wealth across accounts.
Avoid generic advice.
"""

    ai_response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=120,
        messages=[{"role": "user", "content": prompt}]
    )

    # -----------------------------
    # RESPONSE
    # -----------------------------
    return {
        "summary": {
            "total_external_balance": total_balance,
            "accounts_count": len(req.external_accounts),
            "idle_cash": idle_cash,
            "investments": investments
        },

        "distribution_percent": distribution,

        "breakdown": breakdown,

        "insights": insights,
        "suggestions": suggestions,

        "ai_recommendation": ai_response.choices[0].message.content.strip(),

        "note": "Simulated Account Aggregator — demo only"
    }