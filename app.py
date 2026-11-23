from flask import Flask, render_template, jsonify, request, redirect
from services.cftc_service import get_market_history, get_market_list, get_latest_market_data
from services.cot_calculator import enrich_history

app = Flask(__name__)

@app.route('/')
def index():
    # The dashboard template is present in the repository.
    return render_template('index.html')

@app.route('/login')
def login():
    # Login page has not yet been added; keep this route from returning 500.
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    return render_template('index.html')

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'service': 'AI Trading Desk', 'data_source': 'CFTC Socrata'})

@app.route('/api/markets')
def markets():
    try:
        return jsonify(get_market_list())
    except Exception as e:
        app.logger.exception('Failed to load market list')
        return jsonify({'error': 'Unable to load market list'}), 502

@app.route('/api/market/<code>')
def market(code):
    try:
        weeks = min(max(int(request.args.get('weeks', 156)), 10), 520)
    except (TypeError, ValueError):
        weeks = 156
    report = request.args.get('report', 'disaggregated')
    try:
        history = get_market_history(code, weeks=weeks, report=report)
        return jsonify(enrich_history(history))
    except Exception as e:
        app.logger.exception('Failed to load market history')
        return jsonify({'error': 'Unable to load market history'}), 502

@app.route('/api/latest')
def latest():
    try:
        return jsonify(get_latest_market_data())
    except Exception as e:
        app.logger.exception('Failed to load latest market data')
        return jsonify({'error': 'Unable to load latest market data'}), 502

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
