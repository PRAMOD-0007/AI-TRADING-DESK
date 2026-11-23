# AI Trading Desk — COT Intelligence

A Flask dashboard for CFTC Commitments of Traders positioning.

## Run locally

1. Install Python 3.10+.
2. Open a terminal in this folder.
3. Create a virtual environment (recommended):
   - Windows: `py -m venv .venv` then `.venv\\Scripts\\activate`
   - macOS/Linux: `python3 -m venv .venv` then `source .venv/bin/activate`
4. Install: `pip install -r requirements.txt`
5. Run: `python app.py`
6. Open `http://127.0.0.1:5000`

## API
- `GET /api/health`
- `GET /api/markets`
- `GET /api/market/<CFTC contract code>?weeks=156&report=disaggregated|tff|legacy`
- `GET /api/latest`

## Data
CFTC Socrata public datasets: Disaggregated Futures Only (`72hh-3qpy`), Traders in Financial Futures Futures Only (`gpe5-46if`), and Legacy Futures Only (`6dca-aqww`).

The COT Index is calculated over a rolling 52-report window in this starter version. The report's Tuesday date is used as the data date; it is not the public release date.
