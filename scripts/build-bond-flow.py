"""Build an observation-only snapshot from inspectable, dated source captures.
Usage: python3 scripts/build-bond-flow.py data/bond-flow-raw-20261006.json
No intraday yield, weekend quote, unverified futures RSI or daily OI inference.
"""
import json
import sys
from datetime import datetime
from pathlib import Path

root = Path(__file__).resolve().parents[1]
raw = json.loads((root / sys.argv[1]).read_text())
rows = []
excluded = []
for item in raw['yield']['rows']:
    day = datetime.strptime(item[0], '%b %d, %Y').date()
    if day.weekday() >= 5 or day.isoformat() >= raw['asof']:
        excluded.append(day.isoformat())
        continue
    rows.append({'date': day.isoformat(), 'close': float(item[1]), 'high': float(item[3]), 'low': float(item[4])})
rows.sort(key=lambda r: r['date'])
assert len({r['date'] for r in rows}) == len(rows), 'Duplicate session'
assert len(rows) >= 50, 'Insufficient Wilder warmup'
gains, losses = [], []
for previous, current in zip(rows, rows[1:]):
    delta = current['close'] - previous['close']
    gains.append(max(delta, 0))
    losses.append(max(-delta, 0))
ag, al = sum(gains[:14])/14, sum(losses[:14])/14
for i, row in enumerate(rows):
    if i < 14:
        row['rsi14'] = None
        continue
    if i > 14:
        ag, al = (ag*13+gains[i-1])/14, (al*13+losses[i-1])/14
    row['rsi14'] = 100-100/(1+ag/al) if al else (100 if ag else 50)

latest = rows[-1]
prior = max(rows[-21:-1], key=lambda r: r['close'])
candidate = latest['close'] > prior['close'] and latest['rsi14'] < prior['rsi14']
rsi_easing, yield_easing = 0, 0
for previous, current in reversed(list(zip(rows, rows[1:]))):
    if current['rsi14'] is not None and previous['rsi14'] is not None and current['rsi14'] < previous['rsi14']:
        rsi_easing += 1
    else:
        break
for previous, current in reversed(list(zip(rows, rows[1:]))):
    if current['close'] < previous['close']:
        yield_easing += 1
    else:
        break

c = raw['cftc']
def position(current, change):
    return {'previous': current-change, 'current': current, 'change': change}
positions = {
    'openInterest': position(c['openInterest'], c['openInterestChange']),
    'assetManagerNet': position(c['assetManagerLong']-c['assetManagerShort'], c['assetManagerLongChange']-c['assetManagerShortChange']),
    'leveragedGrossShort': position(c['leveragedShort'], c['leveragedShortChange']),
    'leveragedNet': position(c['leveragedLong']-c['leveragedShort'], c['leveragedLongChange']-c['leveragedShortChange'])
}
snapshot = {
    'schemaVersion': 1, 'asof': raw['asof'],
    'observationOnly': True, 'riskWeight': 0, 'affectsADD': False,
    'validation': '미검증 가설 · 전향적 관찰 중 · 적중률 미산출',
    'yield': {'url': raw['yield']['url'], 'retrievedAt': raw['yield']['retrievedAt'],
              'series': 'Investing.com UST 10Y yield daily weekday closes',
              'method': 'Wilder RSI(14): first 14 arithmetic-average changes, then (previous*13+change)/14; excludes current session and weekends.',
              'sessionCount': len(rows), 'excludedDates': excluded, 'latest': latest,
              'comparison': prior, 'chart': rows[-20:]},
    'patterns': {'momentumSlowdownCandidate': candidate, 'rsiEasingSessions': rsi_easing,
                 'yieldEasingSessions': yield_easing,
                 'rsiDifference': latest['rsi14']-prior['rsi14'],
                 'rule': 'Latest completed close exceeds prior 20-session maximum close while RSI is lower. Descriptive pair; no proven exhaustion threshold.'},
    'futures': {'url': raw['futures']['url'], 'sourceLabel': raw['futures']['sourceLabel'],
                'contractVerified': False, 'rsi14': None, 'dailyOpenInterest': None,
                'reason': 'Source title Dec 26 conflicts with TYU26. Contract/roll series and daily OI unverified.'},
    'cftc': {'url': c['url'], 'asof': c['asof'], 'previousAsOf': c['previousAsOf'],
              'marketCode': c['marketCode'], 'scope': c['scope'], 'positions': positions,
              'previousMethod': 'Current positions minus officially reported weekly changes; prior report not independently fetched.',
              'coversCandidateDate': c['asof'] >= prior['date']},
    'rawFile': sys.argv[1]
}
(root/'bond-flow.json').write_text(json.dumps(snapshot, ensure_ascii=False, indent=2)+'\n')
history_file = root/'bond-flow-history.json'
history = json.loads(history_file.read_text()) if history_file.exists() else {}
history[snapshot['asof']] = snapshot
history_file.write_text(json.dumps(history, ensure_ascii=False, indent=2)+'\n')
print(json.dumps({'sessions':len(rows), 'rsi':latest['rsi14'], 'priorRSI':prior['rsi14'], 'rsiEasing':rsi_easing, 'yieldEasing':yield_easing, 'candidate':candidate}))
