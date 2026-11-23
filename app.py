from flask import Flask, render_template, jsonify, request, redirect
from dotenv import load_dotenv
import os
import requests
from functools import wraps
from services.cftc_service import get_market_history, get_market_list, get_latest_market_data
from services.cot_calculator import enrich_history

load_dotenv()  # Load local .env; Render uses environment variables.

app = Flask(__name__)
SUPABASE_URL = os.getenv('SUPABASE_URL', '').rstrip('/')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_PUBLISHABLE_KEY') or os.getenv('SUPABASE_ANON_KEY', '')

def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '', 1).strip()
        if not token or not SUPABASE_URL or not SUPABASE_ANON_KEY:
            return jsonify({'error': 'Authentication required'}), 401
        try:
            response = requests.get(
                f'{SUPABASE_URL}/auth/v1/user',
                headers={'apikey': SUPABASE_ANON_KEY, 'Authorization': f'Bearer {token}'},
                timeout=10
            )
            if response.status_code != 200:
                return jsonify({'error': 'Invalid or expired session'}), 401
        except requests.RequestException:
            return jsonify({'error': 'Authentication service unavailable'}), 503
        return fn(*args, **kwargs)
    return wrapper

@app.context_processor
def inject_supabase_config():
    return {'supabase_url': SUPABASE_URL, 'supabase_anon_key': SUPABASE_ANON_KEY}

@app.route('/')
def index():
    return render_template('public.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('index.html')

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'service': 'AI Trading Desk', 'data_source': 'CFTC Socrata'})

@app.route('/api/markets')
@require_auth
def markets():
    try:
        return jsonify(get_market_list())
    except Exception as e:
        return jsonify({'error': str(e)}), 502

@app.route('/api/market/<code>')
@require_auth
def market(code):
    weeks = min(max(int(request.args.get('weeks', 156)), 10), 520)
    report = request.args.get('report', 'disaggregated')
    try:
        history = get_market_history(code, weeks=weeks, report=report)
        return jsonify(enrich_history(history))
    except Exception as e:
        return jsonify({'error': str(e)}), 502

@app.route('/api/latest')
@require_auth
def latest():
    try:
        return jsonify(get_latest_market_data())
    except Exception as e:
        return jsonify({'error': str(e)}), 502

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
