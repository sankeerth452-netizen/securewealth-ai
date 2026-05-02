# PROJECT: SecureWealth Twin | v3.0-production
import os
import requests
from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder=".", static_folder=".")
app.secret_key = os.getenv("SECRET_KEY", "flask-secret-key-for-development")

FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, user_id, name, email, token):
        self.id = user_id
        self.name = name
        self.email = email
        self.token = token

@login_manager.user_loader
def load_user(user_id):
    if "user" in session and session["user"]["id"] == user_id:
        u = session["user"]
        return User(u["id"], u["name"], u["email"], u["token"])
    return None

def api(endpoint, method="GET", payload=None):
    token = session.get("user", {}).get("token", "")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        if method == "GET":
            r = requests.get(f"{FASTAPI_URL}{endpoint}", headers=headers, timeout=10)
        else:
            r = requests.post(f"{FASTAPI_URL}{endpoint}", json=payload, headers=headers, timeout=10)
        return r.json()
    except requests.exceptions.RequestException:
        return {"error": "AI agents offline or unreachable"}

@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return render_template("index.html")

@app.route("/dashboard")
@login_required
def dashboard():
    # Fetch real data from FastAPI
    data = api(f"/api/ai/user-summary?user_id={current_user.id}", method="GET")
    return render_template("index.html", user_data=data)

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    res = api("/api/auth/login", method="POST", payload=data)
    if "token" in res:
        user = User(res["user_id"], res["name"], res["email"], res["token"])
        session["user"] = {
            "id": res["user_id"],
            "name": res["name"],
            "email": res["email"],
            "token": res["token"]
        }
        login_user(user)
        return {"success": True}
    return {"error": res.get("detail", "Login failed")}, 401

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    res = api("/api/auth/register", method="POST", payload=data)
    if "token" in res:
        user = User(res["user_id"], res["name"], res["email"], res["token"])
        session["user"] = {
            "id": res["user_id"],
            "name": res["name"],
            "email": res["email"],
            "token": res["token"]
        }
        login_user(user)
        return {"success": True}
    return {"error": res.get("detail", "Signup failed")}, 400

@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.pop("user", None)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(port=5000, debug=True)
