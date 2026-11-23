import requests
from datetime import datetime

BASE = 'https://publicreporting.cftc.gov/resource'
DATASETS = {
    'disaggregated': '72hh-3qpy',
    'tff': 'gpe5-46if',
    'legacy': '6dca-aqww'
}

MARKETS = [
    {'code': '088691', 'symbol': 'GC', 'name': 'Gold', 'exchange': 'COMEX', 'category': 'Metals', 'report': 'disaggregated'},
    {'code': '084691', 'symbol': 'SI', 'name': 'Silver', 'exchange': 'COMEX', 'category': 'Metals', 'report': 'disaggregated'},
    {'code': '067651', 'symbol': 'CL', 'name': 'Crude Oil', 'exchange': 'NYMEX', 'category': 'Energy', 'report': 'disaggregated'},
    {'code': '023651', 'symbol': 'NG', 'name': 'Natural Gas', 'exchange': 'NYMEX', 'category': 'Energy', 'report': 'disaggregated'},
    {'code': '099741', 'symbol': 'ES', 'name': 'E-mini S&P 500', 'exchange': 'CME', 'category': 'Indices', 'report': 'tff'},
    {'code': '097741', 'symbol': 'NQ', 'name': 'E-mini Nasdaq-100', 'exchange': 'CME', 'category': 'Indices', 'report': 'tff'},
    {'code': '099741', 'symbol': 'SP', 'name': 'S&P 500', 'exchange': 'CME', 'category': 'Indices', 'report': 'tff'},
    {'code': '099742', 'symbol': 'YM', 'name': 'Dow Jones', 'exchange': 'CBOT', 'category': 'Indices', 'report': 'tff'},
    {'code': '099742', 'symbol': '6E', 'name': 'Euro FX', 'exchange': 'CME', 'category': 'FX', 'report': 'tff'},
    {'code': '096742', 'symbol': '6B', 'name': 'British Pound', 'exchange': 'CME', 'category': 'FX', 'report': 'tff'},
    {'code': '097742', 'symbol': '6J', 'name': 'Japanese Yen', 'exchange': 'CME', 'category': 'FX', 'report': 'tff'},
]

FIELDS = {
    'disaggregated': [
        'report_date_as_yyyy_mm_dd','market_and_exchange_names','open_interest_all',
        'prod_merc_positions_long','prod_merc_positions_short',
        'swap_positions_long_all','swap__positions_short_all',
        'm_money_positions_long_all','m_money_positions_short_all','m_money_positions_spread_all',
        'other_rept_positions_long_all','other_rept_positions_short_all','other_rept_positions_spread_all',
        'nonrept_positions_long_all','nonrept_positions_short_all'
    ],
    'tff': [
        'report_date_as_yyyy_mm_dd','market_and_exchange_names','open_interest_all',
        'dealer_positions_long_all','dealer_positions_short_all','dealer_positions_spread_all',
        'asset_mgr_positions_long_all','asset_mgr_positions_short_all','asset_mgr_positions_spread_all',
        'lev_money_positions_long_all','lev_money_positions_short_all','lev_money_positions_spread_all',
        'other_rept_positions_long_all','other_rept_positions_short_all','other_rept_positions_spread_all',
        'nonrept_positions_long_all','nonrept_positions_short_all'
    ],
    'legacy': [
        'report_date_as_yyyy_mm_dd','market_and_exchange_names','open_interest_all',
        'noncomm_positions_long_all','noncomm_positions_short_all','noncomm_positions_spread_all',
        'comm_positions_long_all','comm_positions_short_all','comm_positions_spread_all',
        'nonrept_positions_long_all','nonrept_positions_short_all'
    ]
}


def _request(dataset, params):
    url = f'{BASE}/{dataset}.json'
    response = requests.get(url, params=params, timeout=30, headers={
        'User-Agent': 'AI-Trading-Desk/1.0',
        'Accept': 'application/json'
    })
    if not response.ok:
        detail = response.text[:500].replace('\n', ' ')
        raise RuntimeError(f'CFTC API HTTP {response.status_code}: {detail}')
    try:
        return response.json()
    except ValueError as exc:
        raise RuntimeError('CFTC API returned a non-JSON response') from exc


def get_market_list():
    return MARKETS


def get_market_history(code, weeks=156, report='disaggregated'):
    report = report if report in DATASETS else 'disaggregated'
    dataset = DATASETS[report]
    params = {
        '$where': f"cftc_contract_market_code='{code}'",
        '$order': 'report_date_as_yyyy_mm_dd DESC',
        '$limit': int(weeks)
    }
    # First attempt a compact projection. If the source schema changes, retry
    # without $select so we can still retrieve data and inspect the actual rows.
    params_with_select = dict(params)
    params_with_select['$select'] = ','.join(FIELDS[report])
    try:
        rows = _request(dataset, params_with_select)
    except RuntimeError as exc:
        if 'HTTP 400' not in str(exc):
            raise
        rows = _request(dataset, params)
    if not isinstance(rows, list):
        raise RuntimeError('CFTC API response was not a list of records')
    rows.reverse()
    return {'report': report, 'market_code': code, 'rows': rows}


def get_latest_market_data():
    result = []
    for market in MARKETS:
        try:
            history = get_market_history(market['code'], weeks=2, report=market['report'])
            rows = history['rows']
            if rows:
                result.append({'market': market, 'latest': rows[-1], 'previous': rows[-2] if len(rows) > 1 else None})
            else:
                result.append({'market': market, 'error': 'No records returned by CFTC'})
        except Exception as exc:
            result.append({'market': market, 'error': str(exc)})
    return result
