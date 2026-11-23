from flask import Flask, render_template, jsonify, request
from services.cftc_service import get_market_history, get_market_list, get_latest_market_data
from services.cot_calculator import enrich_history

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'service': 'AI Trading Desk', 'data_source': 'CFTC Socrata'})

@app.route('/api/markets')
def markets():
    try:
        return jsonify(get_market_list())
    except Exception as e:
        return jsonify({'error': str(e)}), 502

@app.route('/api/market/<code>')
def market(code):
    weeks = min(max(int(request.args.get('weeks', 156)), 10), 520)
    report = request.args.get('report', 'disaggregated')
    try:
        history = get_market_history(code, weeks=weeks, report=report)
        return jsonify(enrich_history(history))
    except Exception as e:
        return jsonify({'error': str(e)}), 502

@app.route('/api/latest')
def latest():
    try:
        return jsonify(get_latest_market_data())
    except Exception as e:
        return jsonify({'error': str(e)}), 502

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
