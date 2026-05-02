# PROJECT: SecureWealth Twin | v3.4
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
        
        # Log for debugging
        print(f"[API] {method} {url} -> {r.status_code}")
        
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
        return redirect(url_for("dashboard")) # Modified from onboarding to dashboard for simplicity
    return render_template("signup.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("index.html")

# ── TRANSFER ROUTES ───────────────────────────────────────────────────────────

@app.route('/transfer', methods=['GET', 'POST'])
@login_required
def transfer():
    account_number = session.get('account_number', '')
    balance        = session.get('balance', 0)

    if request.method == 'POST':
        recipient = request.form.get('recipient', '').strip()
        amount    = float(request.form.get('amount', 0))
        note      = request.form.get('note', '')

        # Step 1: AI risk check
        exec_payload = {
            "action_type":             "transfer",
            "amount":                  amount,
            "avg_amount":              float(balance) * 0.05,
            "is_new_device":           False,
            "seconds_since_login":     60,
            "is_first_investment_type": False,
            "otp_retry_count":         0,
            "hour_of_day":             datetime.now().hour,
            "first_time_count":        0,
            "monthly_amount":          amount,
            "years":                   5,
        }
        risk = api('/api/execute', payload=exec_payload)
        decision = risk.get('risk', {}).get('decision', 'ALLOW')

        if decision == 'BLOCK':
            reason = risk.get('risk', {}).get('reason', 'Risk detected.')
            flash(f'🛡️ Transfer blocked by AI Fraud Shield: {reason}', 'error')
            return render_template('transfer.html',
                                   balance=balance,
                                   account_number=account_number,
                                   risk_result=risk)

        if decision == 'WARN':
            session['pending_transfer'] = {
                'recipient': recipient,
                'amount':    amount,
                'note':      note,
                'risk':      risk,
            }
            return render_template('transfer.html',
                                   balance=balance,
                                   account_number=account_number,
                                   risk_result=risk,
                                   needs_confirm=True,
                                   amount=amount,
                                   recipient=recipient)

        # Step 2: Execute transfer in DB via FastAPI
        result = api('/api/auth/transfer', payload={
            "sender_account_number":    account_number,
            "recipient_account_number": recipient,
            "amount":                   amount,
            "note":                     note,
            "token":                    session.get('jwt_token', ''),
        })

        if result.get('error') or result.get('status') != 'success':
            msg = result.get('message', 'Transfer failed')
            flash(f'❌ {msg}', 'error')
            return render_template('transfer.html',
                                   balance=balance,
                                   account_number=account_number)

        # Update session balance
        session['balance'] = result.get('sender_balance', balance - amount)
        flash(f'✅ ₹{amount:,.2f} transferred successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('transfer.html',
                           balance=balance,
                           account_number=account_number)


@app.route('/transfer/confirm', methods=['POST'])
@login_required
def confirm_transfer():
    pending = session.pop('pending_transfer', None)
    if not pending:
        flash('No pending transfer', 'error')
        return redirect(url_for('transfer'))

    result = api('/api/auth/transfer', payload={
        "sender_account_number":    session.get('account_number', ''),
        "recipient_account_number": pending['recipient'],
        "amount":                   pending['amount'],
        "note":                     pending.get('note', ''),
        "token":                    session.get('jwt_token', ''),
    })

    if result.get('status') == 'success':
        session['balance'] = result.get('sender_balance', 0)
        flash(f'✅ ₹{pending["amount"]:,.2f} confirmed and sent!', 'success')
    else:
        flash(f'❌ {result.get("message", "Transfer failed")}', 'error')

    return redirect(url_for('dashboard'))

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
