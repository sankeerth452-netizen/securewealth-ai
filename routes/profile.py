import os
from dotenv import load_dotenv
load_dotenv()

from groq import Groq
from fastapi import APIRouter
from pydantic import BaseModel

from routes.user_history import USER_HISTORY
from routes.risk import audit_log

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter()

class AnalyzeRequest(BaseModel):
    age: int | None = 28
    income: float | None = 0
    monthly_expenses: float | None = 0
    current_savings: float | None = 0
    risk_appetite: str | None = "medium"
    goal: str | None = "general savings"
    investment_experience: str | None = "beginner"

@router.post("/analyze")
@router.post("/profile/analyze")
async def analyze_profile(request: Request):
    try:
        # Debug Log
        body = await request.json()
        print("ANALYZE BODY:", body)
        
        # Pydantic Validation
        req = AnalyzeRequest(**body)
    except Exception as e:
        print(f"[Profile] Validation Error: {e}")
        return JSONResponse(
            status_code=400,
            content={"error": f"Invalid request body: {str(e)}"}
        )
    savings_rate = 0.0
    try:
        if req.income > 0:
            savings_rate = ((req.income - req.monthly_expenses) / req.income) * 100
    except Exception:
        savings_rate = 0.0

    # Deterministic behavior score calculation
    behavior_score = 75 # Default
    try:
        score = min(max(0, savings_rate), 30) / 30 * 40
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
        recent_logs = audit_log[-10:]
        deductions = 0
        for log in recent_logs:
            if log.get("decision") == "BLOCK": deductions += 10
            elif log.get("decision") == "WARN": deductions += 5
        score += max(0, 30 - deductions)
        behavior_score = min(100, round(score))
    except Exception:
        behavior_score = 75

    # Try AI analysis — fall back gracefully if Groq is unavailable
    try:
        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key:
            raise ValueError("GROQ_API_KEY not set")

        client = Groq(api_key=api_key)
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
SCORE_EXPLANATION: [one sentence explaining the behavior score]"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=120,
            messages=[{"role": "user", "content": prompt}]
        )

        text = response.choices[0].message.content.strip()
        lines = text.split("\n")
        result = {}
        for line in lines:
            if "ARCHETYPE:" in line:
                result["archetype"] = line.split("ARCHETYPE:")[-1].strip()
            elif "STRENGTH:" in line:
                result["strength"] = line.split("STRENGTH:")[-1].strip()
            elif "WEAKNESS:" in line:
                result["weakness"] = line.split("WEAKNESS:")[-1].strip()
            elif "TIP:" in line:
                result["tip"] = line.split("TIP:")[-1].strip()
            elif "SCORE_EXPLANATION:" in line:
                result["score_explanation"] = line.split("SCORE_EXPLANATION:")[-1].strip()

        result["behavior_score"] = behavior_score
        result["behavior_label"] = "Good" if behavior_score >= 70 else "Average" if behavior_score >= 40 else "Poor"
        result["savings_rate"] = round(savings_rate, 1)
        result["note"] = "For simulation purposes only"
        return result

    except Exception as e:
        print(f"[Profile] AI analysis failed: {e} — returning fallback archetype")
        archetype = (
            "Bold Grower"   if req.risk_appetite == "high"   else
            "Steady Planner" if req.risk_appetite == "medium" else
            "Cautious Builder"
        )
        return {
            "archetype":    archetype,
            "strength":     "Consistent saving habits",
            "weakness":     "Could diversify investments more",
            "tip":          f"Invest {int(req.income * 0.15):,} monthly in SIPs",
            "score_explanation": "Your score reflects steady financial discipline.",
            "behavior_score": behavior_score,
            "behavior_label": "Good" if behavior_score >= 70 else "Average" if behavior_score >= 40 else "Poor",
            "savings_rate": round(savings_rate, 1),
            "note":         "AI offline — showing rule-based archetype",
        }