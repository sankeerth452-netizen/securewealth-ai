import os
import re
import datetime
from dotenv import load_dotenv
load_dotenv()

from groq import Groq
from fastapi import APIRouter
from pydantic import BaseModel
from prompts.wealth_coach import build_system_prompt
from routes.user_history import init_login_time, USER_HISTORY

api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None
router = APIRouter()


# -----------------------------
# REQUEST MODEL
# -----------------------------
class ChatRequest(BaseModel):
    message: str
    user_profile: dict


# -----------------------------
# INTENT DETECTION
# -----------------------------
def detect_intent(message: str) -> dict:
    msg = message.lower()

    # Detect investment intent — handles ₹1,00,000 and 100000 and 1 lakh
    invest_match = re.search(r'(invest|sip|put|start)\s*₹?\s*([\d,]+)', msg)
    lakh_match = re.search(r'(invest|sip|put|start)\s*₹?\s*(\d+)\s*lakh', msg)

    if lakh_match:
        amount = float(lakh_match.group(2)) * 100000
        return {"type": "investment", "amount": amount}

    if invest_match:
        amount_str = invest_match.group(2).replace(",", "")
        amount = float(amount_str)
        return {"type": "investment", "amount": amount}

    # Detect simulation intent
    sim_match = re.search(r'(\d+)\s*(years|year)', msg)
    if "what if" in msg or "future" in msg or "grow" in msg or sim_match:
        return {"type": "simulation"}

    # Detect net worth intent
    if any(word in msg for word in ["net worth", "assets", "property", "gold", "total wealth"]):
        return {"type": "networth"}

    return {"type": "chat"}


# -----------------------------
# CALL EXECUTION ENGINE (fixed — no hardcoded risky values)
# -----------------------------
def call_execution_engine(amount: float, user_profile: dict):
    try:
        # Import directly — no HTTP call, avoids hanging
        from routes.execution import execute_action, ExecuteRequest

        req = ExecuteRequest(
            action_type="invest",
            amount=amount,
            avg_amount=USER_HISTORY["avg_transaction"],
            is_new_device=False,                          # realistic default
            seconds_since_login=60,                       # realistic default
            is_first_investment_type=False,               # realistic default
            otp_retry_count=0,                            # realistic default
            hour_of_day=datetime.datetime.now().hour,     # real current hour
            first_time_count=0,
            monthly_amount=amount / 10,
            years=10
        )
        return execute_action(req)

    except Exception as e:
        return {"error": str(e)}


# -----------------------------
# MAIN CHAT ENDPOINT
# -----------------------------
@router.post("/chat")
def wealth_chat(req: ChatRequest):
    init_login_time()
    intent = detect_intent(req.message)
    system_prompt = build_system_prompt(req.user_profile)

    # -----------------------------
    # CASE 1: INVESTMENT INTENT
    # -----------------------------
    if intent["type"] == "investment":
        amount = intent["amount"]
        exec_result = call_execution_engine(amount, req.user_profile)

        decision = exec_result.get("risk", {}).get("decision", "UNKNOWN")
        reason   = exec_result.get("risk", {}).get("reason", "")
        status   = exec_result.get("status", "")

        # AI generates a calm, human explanation of what happened
        explanation_prompt = f"""
A user wanted to invest ₹{amount:,.0f}.
The system decision was: {decision}.
Reason: {reason}
Status: {status}

Write 2 short, calm, friendly sentences explaining this to the user.
If BLOCK — reassure them it's for their safety.
If WARN — tell them to wait briefly and confirm.
If approved — congratulate and mention the investment was approved.
No jargon.
"""
        explanation = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=120,
            messages=[{"role": "user", "content": explanation_prompt}]
        ).choices[0].message.content.strip()

        return {
            "type": "action_response",
            "user_intent": "investment",
            "amount": amount,
            "ai_explanation": explanation,
            "execution": exec_result
        }

    # -----------------------------
    # CASE 2: SIMULATION INTENT
    # -----------------------------
    elif intent["type"] == "simulation":
        # Extract years if mentioned
        years_match = re.search(r'(\d+)\s*(years|year)', req.message.lower())
        years = int(years_match.group(1)) if years_match else 10

        # Extract amount if mentioned
        amount_match = re.search(r'₹?\s*([\d,]+)', req.message)
        monthly = float(amount_match.group(1).replace(",", "")) if amount_match else (
            req.user_profile.get("income", 50000) * 0.15
        )

        # Call simulator directly
        from routes.simulate import calculate_sip
        months = years * 12
        projection = calculate_sip(monthly, months, 12.0)
        final_value = projection[-1]["value"] if projection else 0
        opportunity_cost = final_value - (calculate_sip(monthly, months - 12, 12.0)[-1]["value"] if months > 12 else 0)

        sim_prompt = f"""
User wants to understand future wealth.
Profile: Income ₹{req.user_profile.get('income')}, goal: {req.user_profile.get('goal')}.
If they invest ₹{monthly:,.0f}/month for {years} years at 12% returns,
they could accumulate ₹{final_value:,.0f}.
Starting 1 year later costs them ₹{opportunity_cost:,.0f}.

Explain this in 2 exciting, motivating sentences. Mention the numbers.
"""
        sim_response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=150,
            messages=[{"role": "user", "content": sim_prompt}]
        )

        return {
            "type": "simulation_advice",
            "reply": sim_response.choices[0].message.content.strip(),
            "projection": projection,
            "summary": {
                "monthly_investment": monthly,
                "years": years,
                "final_value": final_value,
                "opportunity_cost": round(opportunity_cost),
                "nudge_message": f"Starting 1 year later costs you ₹{opportunity_cost:,.0f}"
            }
        }

    # -----------------------------
    # CASE 3: NET WORTH INTENT
    # -----------------------------
    elif intent["type"] == "networth":
        profile = req.user_profile
        savings = profile.get("current_savings", 0)
        investments = profile.get("investments_value", 0)

        nw_prompt = f"""
User asked about their net worth.
Known data: savings ₹{savings}, investments ₹{investments},
income ₹{profile.get('income', 0)}, goal: {profile.get('goal', 'wealth building')}.

In 2 sentences, give them a snapshot of their financial health
and one actionable tip to improve their net worth.
"""
        nw_response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=150,
            messages=[{"role": "user", "content": nw_prompt}]
        )

        return {
            "type": "networth_snapshot",
            "reply": nw_response.choices[0].message.content.strip(),
            "known_data": {
                "savings": savings,
                "investments": investments
            }
        }

    # -----------------------------
    # CASE 4: NORMAL CHAT
    # -----------------------------
    else:
        reply_response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=400,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": req.message}
            ]
        )

        reply_text = re.sub(
            r'```json.*?```', '',
            reply_response.choices[0].message.content,
            flags=re.DOTALL
        ).strip()

        reason_response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=60,
            messages=[{
                "role": "user",
                "content":
                    f"The user asked: {req.message}\n"
                    f"The advisor replied: {reply_text}\n"
                    f"Profile: income ₹{req.user_profile.get('income')}, "
                    f"goal: {req.user_profile.get('goal')}, "
                    f"risk: {req.user_profile.get('risk_appetite')}\n\n"
                    f"Write ONE sentence (max 12 words) starting with 'Based on' explaining why."
            }]
        )

        return {
            "type": "chat",
            "reply": reply_text,
            "reason": reason_response.choices[0].message.content.strip()
        }