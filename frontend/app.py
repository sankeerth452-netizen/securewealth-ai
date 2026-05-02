# PROJECT: SecureWealth Twin | v3.2
import os, requests
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, session

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-change-me')
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours

FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000").rstrip('/')

# ── API HELPER ────────────────────────────────────────────────────────────────
def api(endpoint, method="POST", payload=None):
    token = session.get("jwt_token", "")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        url = f"{FASTAPI_URL}{endpoint}"
        r = (requests.get(url, headers=headers, timeout=15) if method == "GET"
             else requests.post(url, json=payload or {}, headers=headers, timeout=15))
        if r.status_code == 401:
            return {"error": "session_expired"}
        return r.json()
    except requests.exceptions.ConnectionError:
        return {"error": "offline", "message": "AI agents are offline"}
    except requests.exceptions.Timeout:
        return {"error": "timeout", "message": "Request timed out"}
    except Exception as e:
        return {"error": "unknown", "message": str(e)}

# ── AUTH DECORATOR ────────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("jwt_token"):
            flash("Please log in to continue", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

# ── CONTEXT PROCESSOR — makes current_user available in ALL templates ─────────
@app.context_processor
def inject_globals():
    return {
        "current_user": type("User", (), {
            "is_authenticated": bool(session.get("jwt_token")),
            "name":  session.get("user_name", ""),
            "email": session.get("user_email", ""),
            "id":    session.get("user_id", ""),
        })(),
        "now_hour": datetime.now().hour,
    }

# ── AUTH ROUTES ───────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return redirect(url_for("dashboard") if session.get("jwt_token") else url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("jwt_token"):
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        result = api("/api/auth/login", payload={
            "email":    request.form.get("email"),
            "password": request.form.get("password"),
        })
        if result.get("error") or not result.get("token"):
            flash(result.get("message", "Invalid email or password"), "error")
            return render_template("login.html")
        session.permanent = True
        session["jwt_token"]      = result["token"]
        session["user_id"]        = result.get("user_id", "")
        session["user_name"]      = result.get("name", "")
        session["user_email"]     = result.get("email", "")
        session["account_number"] = result.get("account_number", "")
        session["balance"]        = result.get("balance", 0)
        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if session.get("jwt_token"):
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        result = api("/api/auth/register", payload={
            "name":     request.form.get("name"),
            "email":    request.form.get("email"),
            "password": request.form.get("password"),
        })
        if result.get("error") or not result.get("token"):
            flash(result.get("message", "Registration failed"), "error")
            return render_template("signup.html")
        session.permanent = True
        session["jwt_token"]      = result["token"]
        session["user_id"]        = result.get("user_id", "")
        session["user_name"]      = result.get("name", "")
        session["user_email"]     = result.get("email", "")
        session["account_number"] = result.get("account_number", "")
        session["balance"]        = result.get("balance", 100000)
        flash("Account created! Set up your financial profile.", "success")
        return redirect(url_for("onboarding"))
    return render_template("signup.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ── PAGES (all other routes stay the same — just add @login_required) ─────────
# dashboard, transfer, transactions, simulate, networth, insights, settings, onboarding
# Use the api() helper instead of call_agent() everywhere

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("index.html")

# ── API PROXY ROUTES ──────────────────────────────────────────────────────────
@app.route("/api/chat", methods=["POST"])
@login_required
def api_chat():
    data = request.get_json(silent=True) or {}
    profile = session.get("user_profile", {
        "name": session.get("user_name", "User"),
        "income": 50000, "goal": "wealth building",
        "risk_appetite": "medium", "current_savings": 0,
        "investments": "none", "age": 30,
    })
    return jsonify(api("/api/ai/chat", payload={
        "message": data.get("message", ""),
        "user_profile": profile,
    }))

@app.route("/api/simulate", methods=["POST"])
@login_required
def api_simulate():
    return jsonify(api("/api/ai/simulate", payload=request.get_json(silent=True) or {}))

@app.route("/api/networth", methods=["POST"])
@login_required
def api_networth():
    return jsonify(api("/api/ai/networth", payload=request.get_json(silent=True) or {}))

@app.route("/api/aggregate", methods=["POST"])
@login_required
def api_aggregate():
    profile = session.get("user_profile", {"income": 50000, "goal": "wealth building"})
    return jsonify(api("/api/ai/aggregate", payload={
        "user_profile": profile,
        "external_accounts": (request.get_json(silent=True) or {}).get("accounts", []),
    }))

@app.route("/api/risk-audit")
@login_required
def api_risk_audit():
    return jsonify(api("/api/execute/audit", method="GET"))

@app.route("/api/account-balance")
@login_required
def api_account_balance():
    result = api(f"/api/auth/me", method="GET")
    if result.get("error"):
        return jsonify({"balance": session.get("balance", 0),
                        "account_number": session.get("account_number", ""),
                        "total_sent": 0})
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=False, port=5000)
