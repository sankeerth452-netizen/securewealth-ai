import os
from dotenv import load_dotenv

load_dotenv()

from groq import Groq
from fastapi import APIRouter
from pydantic import BaseModel

from routes.user_history import USER_HISTORY
from routes.risk import audit_log

api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None
router = APIRouter()


class ProfileRequest(BaseModel):
    age: int
    income: float
    monthly_expenses: float
    current_savings: float
    risk_appetite: str
    goal: str
    investment_experience: str  # "none", "beginner", "intermediate"


@router.post("/profile/analyze")
def analyze_profile(req: ProfileRequest):
    savings_rate = ((req.income - req.monthly_expenses) / req.income) * 100

    # Deterministic score calculation
    # A. Savings Rate (0-40)
    score = min(savings_rate, 30) / 30 * 40
    
    # B. Stability (0-30)
    txs = USER_HISTORY.get("last_transactions", [])
    if not txs:
        score += 20
    else:
        avg = sum(txs) / len(txs)
        if avg > 0:
            avg_diff = sum(abs(t - avg) for t in txs) / len(txs)
            volatility = avg_diff / avg
            score += max(0, 30 - (volatility * 30))
        else:
            score += 15
            
    # C. Risk History (0-30)
    recent_logs = audit_log[-10:]
    deductions = 0
    for log in recent_logs:
        if log["decision"] == "BLOCK": deductions += 10
        elif log["decision"] == "WARN": deductions += 5
    score += max(0, 30 - deductions)
    behavior_score = min(100, round(score))

    prompt = f"""Analyze this person's financial profile and assign them ONE archetype name 
(2-3 words, creative but professional, e.g. "Cautious Builder", "Bold Grower", "Steady Planner").

Profile: age {req.age}, income ₹{req.income}, expenses ₹{req.monthly_expenses},
savings rate {savings_rate:.1f}%, risk appetite {req.risk_appetite},
goal: {req.goal}, experience: {req.investment_experience}.
Financial Behavior Score: {behavior_score}/100.

Respond in this exact format:
ARCHETYPE: [name]
STRENGTH: [one strength in 8 words max]
WEAKNESS: [one weakness in 8 words max]
TIP: [one actionable tip in 12 words max]
SCORE_EXPLANATION: [one sentence explaining the behavior score based on their profile and score]"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=120,
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.choices[0].message.content.strip()

    # Parse the structured response
    lines = text.split("\n")
    result = {}
    for line in lines:
        if "ARCHETYPE:" in line:
            result["archetype"] = line.split("ARCHETYPE:")[1].strip()
        elif "STRENGTH:" in line:
            result["strength"] = line.split("STRENGTH:")[1].strip()
        elif "WEAKNESS:" in line:
            result["weakness"] = line.split("WEAKNESS:")[1].strip()
        elif "TIP:" in line:
            result["tip"] = line.split("TIP:")[1].strip()
        elif "SCORE_EXPLANATION:" in line:
            result["score_explanation"] = line.split("SCORE_EXPLANATION:")[1].strip()

    result["behavior_score"] = behavior_score
    result["behavior_label"] = "Good" if behavior_score >= 70 else "Average" if behavior_score >= 40 else "Poor"

    result["savings_rate"] = round(savings_rate, 1)
    result["note"] = "For simulation purposes only"
    return result