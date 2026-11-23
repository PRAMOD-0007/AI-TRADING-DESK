import os
import requests
from flask import Flask, render_template, jsonify, request, redirect, make_response
from services.cftc_service import get_market_history, get_market_list, get_latest_market_data
from services.cot_calculator import enrich_history

app = Flask(__name__)
SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY", os.getenv("SUPABASE_ANON_KEY", ""))
SESSION_COOKIE = "atd_session"

def get_token():
    return request.cookies.get(SESSION_COOKIE) or (request.headers.get("Authorization", "").replace("Bearer ", "", 1) if request.headers.get("Authorization", "").startswith("Bearer ") else None)

def verify_token(token):
    if not token or not SUPABASE_URL or not SUPABASE_KEY:
        return None
    try:
        r = requests.get(f"{SUPABASE_URL}/auth/v1/user", headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {token}"}, timeout=8)
        return r.json() if r.ok else None
    except requests.RequestException:
        return None

def require_member():
    return verify_token(get_token())

@app.route("/")
def index():
    if require_member():
        return redirect("/dashboard")
    return render_template("public.html", supabase_url=SUPABASE_URL, supabase_key=SUPABASE_KEY)

@app.route("/login")
def login():
    if require_member():
        return redirect("/dashboard")
    return render_template("login.html", supabase_url=SUPABASE_URL, supabase_key=SUPABASE_KEY)

@app.route("/signup")
def signup():
    if require_member():
        return redirect("/dashboard")
    return render_template("signup.html", supabase_url=SUPABASE_URL, supabase_key=SUPABASE_KEY)

@app.route("/auth/config")
def auth_config():
    return jsonify({"supabase_url": SUPABASE_URL, "supabase_key": SUPABASE_KEY})

@app.route("/auth/session", methods=["POST"])
def create_session():
    payload = request.get_json(silent=True) or {}
    token = payload.get("access_token")
    user = verify_token(token)
    if not user:
        return jsonify({"error": "Invalid or expired session"}), 401
    response = make_response(jsonify({"ok": True, "user": user.get("email")}))
    response.set_cookie(SESSION_COOKIE, token, httponly=True, secure=request.is_secure or os.getenv("RENDER") == "true", samesite="Lax", max_age=60*60*24*7, path="/")
    return response

@app.route("/auth/logout", methods=["POST"])
def logout():
    response = make_response(jsonify({"ok": True}))
    response.delete_cookie(SESSION_COOKIE, path="/")
    return response

@app.route("/dashboard")
def dashboard():
    if not require_member():
        return redirect("/login?next=/dashboard")
    return render_template("index.html")

@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "service": "AI Trading Desk", "data_source": "CFTC Socrata"})

@app.route("/api/markets")
def markets():
    if not require_member():
        return jsonify({"error": "Authentication required"}), 401
    try:
        return jsonify(get_market_list())
    except Exception:
        app.logger.exception("Failed to load market list")
        return jsonify({"error": "Unable to load market list"}), 502

@app.route("/api/market/<code>")
def market(code):
    if not require_member():
        return jsonify({"error": "Authentication required"}), 401
    try:
        weeks = min(max(int(request.args.get("weeks", 156)), 10), 520)
    except (TypeError, ValueError):
        weeks = 156
    report = request.args.get("report", "disaggregated")
    try:
        history = get_market_history(code, weeks=weeks, report=report)
        return jsonify(enrich_history(history))
    except Exception:
        app.logger.exception("Failed to load market history")
        return jsonify({"error": "Unable to load market history"}), 502

@app.route("/api/latest")
def latest():
    if not require_member():
        return jsonify({"error": "Authentication required"}), 401
    try:
        return jsonify(get_latest_market_data())
    except Exception:
        app.logger.exception("Failed to load latest market data")
        return jsonify({"error": "Unable to load latest market data"}), 502

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
