import os
from groq import Groq
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from routes.user_history import USER_HISTORY
from routes.risk import audit_log

router = APIRouter()

# 1. CENTRALIZED AI INITIALIZATION
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = None
if GROQ_API_KEY:
    try:
        client = Groq(api_key=GROQ_API_KEY)
        print("✅ Groq AI Client Initialized")
    except Exception as e:
        print(f"❌ Groq Init Failed: {e}")
else:
    print("⚠️ GROQ_API_KEY is missing in environment")

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
        body = await request.json()
        req = AnalyzeRequest(**body)
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": f"Invalid body: {e}"})

    savings_rate = 0.0
    if req.income > 0:
        savings_rate = ((req.income - req.monthly_expenses) / req.income) * 100

    behavior_score = 75
    # (Existing scoring logic maintained for internal consistency)
    try:
        score = min(max(0, savings_rate), 30) / 30 * 40
        txs = USER_HISTORY.get("last_transactions", [])
        if txs:
            avg = sum(txs) / len(txs)
            if avg > 0:
                score += max(0, 30 - ((sum(abs(t - avg) for t in txs) / len(txs)) / avg * 30))
        behavior_score = min(100, round(score + 30)) # Baseline + risk adjustment
    except: 
        pass

    # 2. AI ANALYSIS WITH ROBUST FALLBACK
    if client:
        try:
            prompt = f"Analyze: age {req.age}, income {req.income}, savings rate {savings_rate:.1f}%, risk {req.risk_appetite}, score {behavior_score}/100. Format: ARCHETYPE: [Name], STRENGTH: [Short], WEAKNESS: [Short], TIP: [Short], SCORE_EXPLANATION: [Short]."
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                max_tokens=150,
                messages=[{"role": "user", "content": prompt}]
            )
            text = response.choices[0].message.content.strip()
            lines = text.split("\n")
            result = {"behavior_score": behavior_score, "behavior_label": "Good" if behavior_score >= 70 else "Average"}
            for line in lines:
                for key in ["ARCHETYPE", "STRENGTH", "WEAKNESS", "TIP", "SCORE_EXPLANATION"]:
                    if f"{key}:" in line: 
                        result[key.lower()] = line.split(f"{key}:")[-1].strip()
            return result
        except Exception as e:
            print(f"GROQ ERROR: {e}")

    # FALLBACK (Rule-based)
    archetype = "Bold Grower" if req.risk_appetite == "high" else "Steady Planner" if req.risk_appetite == "medium" else "Cautious Builder"
    return {
        "archetype": archetype,
        "strength": "Consistent core savings",
        "weakness": "Limited asset diversification",
        "tip": f"Consider investing ₹{int(req.income * 0.1):,} monthly.",
        "score_explanation": "Based on your income-to-expense ratio and saving habits.",
        "behavior_score": behavior_score,
        "behavior_label": "Good" if behavior_score >= 70 else "Average",
        "savings_rate": round(savings_rate, 1),
        "note": "AI Service unavailable - using local analyzer"
    }