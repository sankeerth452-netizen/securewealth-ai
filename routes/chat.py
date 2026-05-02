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
# CALL EXECUTION ENGINE
# -----------------------------
def call_execution_engine(amount: float, user_profile: dict):
    try:
        from routes.execution import execute_action, ExecuteRequest

        req = ExecuteRequest(
            action_type="invest",
            amount=amount,
            avg_amount=USER_HISTORY.get("avg_transaction", 5000),
            is_new_device=False,
            seconds_since_login=60,
            is_first_investment_type=False,
            otp_retry_count=0,
            hour_of_day=datetime.datetime.now().hour,
            first_time_count=0,
            monthly_amount=amount / 10,
            years=10
        )
        return execute_action(req)
    except Exception as e:
        return {"error": str(e), "status": "failed"}


# -----------------------------
# MAIN CHAT ENDPOINT
# -----------------------------
@router.post("/chat")
def wealth_chat(req: ChatRequest):
    try:
        init_login_time()
        intent = detect_intent(req.message)
        system_prompt = build_system_prompt(req.user_profile)

        if not client:
            raise ValueError("AI Client not initialized")

        # -----------------------------
        # CASE 1: INVESTMENT INTENT
        # -----------------------------
        if intent["type"] == "investment":
            amount = intent["amount"]
            exec_result = call_execution_engine(amount, req.user_profile)

            decision = exec_result.get("risk", {}).get("decision", "UNKNOWN")
            reason   = exec_result.get("risk", {}).get("reason", "")
            status   = exec_result.get("status", "")

            try:
                explanation_prompt = f"A user wants to invest ₹{amount:,.0f}. Decision: {decision}. Reason: {reason}. Write 2 calm, friendly sentences explaining this."
                explanation_res = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    max_tokens=100,
                    messages=[{"role": "user", "content": explanation_prompt}]
                )
                explanation = explanation_res.choices[0].message.content.strip()
            except Exception:
                explanation = f"Your investment of ₹{amount:,.0f} has been processed with status: {status}."

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
            years_match = re.search(r'(\d+)\s*(years|year)', req.message.lower())
            years = int(years_match.group(1)) if years_match else 10
            amount_match = re.search(r'₹?\s*([\d,]+)', req.message)
            monthly = float(amount_match.group(1).replace(",", "")) if amount_match else (
                req.user_profile.get("income", 50000) * 0.15
            )

            from routes.simulate import calculate_sip
            months = years * 12
            projection = calculate_sip(monthly, months, 12.0)
            final_value = projection[-1]["value"] if projection else 0
            
            try:
                sim_prompt = f"Explain in 2 sentences that investing ₹{monthly:,.0f}/month for {years} years can grow to ₹{final_value:,.0f}."
                sim_response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    max_tokens=120,
                    messages=[{"role": "user", "content": sim_prompt}]
                )
                reply = sim_response.choices[0].message.content.strip()
            except Exception:
                reply = f"Based on your inputs, you could accumulate ₹{final_value:,.0f} in {years} years."

            return {
                "type": "simulation_advice",
                "reply": reply,
                "projection": projection,
                "summary": {"monthly_investment": monthly, "years": years, "final_value": final_value}
            }

        # -----------------------------
        # CASE 3: NET WORTH INTENT
        # -----------------------------
        elif intent["type"] == "networth":
            profile = req.user_profile
            savings = profile.get("current_savings", 0)
            investments = profile.get("investments_value", 0)

            try:
                nw_prompt = f"User asked about net worth. Savings: ₹{savings}, Investments: ₹{investments}. Give a 2-sentence snapshot."
                nw_response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    max_tokens=120,
                    messages=[{"role": "user", "content": nw_prompt}]
                )
                reply = nw_response.choices[0].message.content.strip()
            except Exception:
                reply = f"Your current tracked net worth consists of ₹{savings:,.0f} in savings and ₹{investments:,.0f} in investments."

            return {
                "type": "networth_snapshot",
                "reply": reply,
                "known_data": {"savings": savings, "investments": investments}
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
            reply_text = re.sub(r'```json.*?```', '', reply_response.choices[0].message.content, flags=re.DOTALL).strip()
            return {
                "type": "chat",
                "reply": reply_text,
                "reason": f"Based on your profile as a {req.user_profile.get('risk_appetite')} investor."
            }

    except Exception as e:
        print(f"[Chat] Error: {e}")
        return {
            "type": "chat",
            "reply": "I'm having a bit of trouble processing that right now. Could you please try again in a moment?",
            "reason": "AI service temporarily unavailable"
        }