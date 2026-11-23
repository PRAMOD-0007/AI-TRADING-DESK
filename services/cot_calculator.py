from datetime import datetime


def number(value):
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def enrich_history(payload):
    report = payload.get('report', 'disaggregated')
    rows = payload.get('rows', [])
    enriched = []
    for row in rows:
        if report == 'disaggregated':
            long = number(row.get('m_money_positions_long_all'))
            short = number(row.get('m_money_positions_short_all'))
            trader = 'Managed Money'
        elif report == 'tff':
            long = number(row.get('lev_money_positions_long_all'))
            short = number(row.get('lev_money_positions_short_all'))
            trader = 'Leveraged Funds'
        else:
            long = number(row.get('noncomm_positions_long_all'))
            short = number(row.get('noncomm_positions_short_all'))
            trader = 'Non-Commercial'
        row['selected_long'] = long
        row['selected_short'] = short
        row['net_position'] = long - short
        row['selected_trader_group'] = trader
        row['open_interest'] = number(row.get('open_interest_all'))
        enriched.append(row)

    nets = [r['net_position'] for r in enriched]
    for i, row in enumerate(enriched):
        previous = enriched[i-1]['net_position'] if i else None
        row['weekly_change'] = row['net_position'] - previous if previous is not None else None
        lookback = nets[max(0, i-51):i+1]
        lo, hi = (min(lookback), max(lookback)) if lookback else (row['net_position'], row['net_position'])
        row['cot_index_52w'] = round((row['net_position'] - lo) / (hi - lo) * 100, 2) if hi != lo else 50.0
        row['report_date'] = row.get('report_date_as_yyyy_mm_dd', '')[:10]
    latest = enriched[-1] if enriched else None
    return {'report': report, 'market_code': payload.get('market_code'), 'trader_group': latest.get('selected_trader_group') if latest else None, 'rows': enriched, 'summary': {
        'latest': latest,
        'previous': enriched[-2] if len(enriched) > 1 else None,
        'count': len(enriched)
    }}
