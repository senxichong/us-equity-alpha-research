"""Small, cached public endpoint probes; HTTP 200 alone is not data success."""
import hashlib
import io
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / 'data/raw/probes'
CACHE.mkdir(parents=True, exist_ok=True)
UA = 'us-equity-alpha-research/0.1 personal academic feasibility study'
SOURCES = {
    'stooq_aapl': 'https://stooq.com/q/d/l/?s=aapl.us&i=d&d1=20180101&d2=20261007',
    'alpha_vantage_demo': 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=IBM&apikey=demo',
    'alpha_vantage_full': 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=IBM&outputsize=full&apikey=demo',
    'alpha_vantage_aapl': 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=AAPL&apikey=demo',
    'sec_companyfacts': 'https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json',
    'sec_submissions': 'https://data.sec.gov/submissions/CIK0000320193.json',
    'nasdaq_directory': 'https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt',
    'sp500_current': 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies',
    'sp500_history_commit': 'https://api.github.com/repos/fja05680/sp500/commits/master',
}


def fetch(name, url):
    meta_path = CACHE / f'{name}.json'
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding='utf-8'))
        if meta.get('body') and hashlib.sha256((ROOT / meta['body']).read_bytes()).hexdigest() != meta['sha256']:
            raise ValueError(f'Cached response hash mismatch: {name}')
        # Reclassify the saved response without making another request.
        if name.startswith('stooq') and meta.get('body') and '<html' in (ROOT / meta['body']).read_text(encoding='utf-8').lower():
            meta.update(data_success=False, rows=0, message='HTTP 200 HTML browser challenge; no OHLCV observations')
        return meta
    meta = {'name': name, 'url': url, 'retrieved_at_utc': datetime.now(timezone.utc).isoformat()}
    started = time.monotonic()
    try:
        r = requests.get(url, headers={'User-Agent': UA}, timeout=30)
        body = CACHE / f'{name}.body'
        body.write_bytes(r.content)
        meta.update(status=r.status_code, bytes=len(r.content), sha256=hashlib.sha256(r.content).hexdigest(), content_type=r.headers.get('Content-Type'), body=str(body.relative_to(ROOT)))
        if r.status_code == 200:
            if name.startswith('stooq'):
                if '<html' in r.text.lower():
                    meta.update(data_success=False, message='HTML browser challenge, not OHLCV data', rows=0)
                else:
                    df = pd.read_csv(io.StringIO(r.text))
                    valid = {'Date', 'Open', 'High', 'Low', 'Close', 'Volume'}.issubset(df.columns)
                    meta.update(columns=list(df.columns), rows=len(df) if valid else 0, data_success=valid)
                    if valid:
                        meta.update(first_date=str(df.Date.min()), last_date=str(df.Date.max()))
            elif name.startswith('alpha_vantage'):
                j = r.json()
                meta.update(response_keys=list(j), observations=len(j.get('Time Series (Daily)', {})))
                meta['message'] = j.get('Information', j.get('Note', j.get('Error Message')))
            elif name.startswith('sec_'):
                j = r.json()
                meta['response_keys'] = list(j)
                meta['entity_name'] = j.get('entityName', j.get('name'))
                if 'facts' in j:
                    meta['taxonomy_tags'] = {k: len(v) for k, v in j['facts'].items()}
            elif name == 'nasdaq_directory':
                meta['line_count'] = len(r.text.splitlines())
                meta['header'] = r.text.splitlines()[0]
            elif name == 'sp500_current':
                df = next(t for t in pd.read_html(io.StringIO(r.text)) if 'Symbol' in t.columns and 'Security' in t.columns)
                df.to_parquet(CACHE / 'sp500_current.parquet', index=False)
                meta.update(rows=len(df), columns=list(df.columns))
            elif name == 'sp500_history_commit':
                meta['commit'] = r.json()['sha']
        else:
            meta['message'] = r.text[:240]
    except Exception as exc:
        meta['error'] = f'{type(exc).__name__}: {exc}'
    meta['elapsed_seconds'] = round(time.monotonic() - started, 3)
    meta_path.write_text(json.dumps(meta, indent=2), encoding='utf-8')
    print(name, meta.get('status'), meta.get('rows', meta.get('observations', meta.get('error', 'response saved'))), flush=True)
    return meta


def main():
    results = [fetch(name, url) for name, url in SOURCES.items()]
    commit = next(r for r in results if r['name'] == 'sp500_history_commit').get('commit')
    if commit:
        base = f'https://raw.githubusercontent.com/fja05680/sp500/{commit}/'
        for name, file in [('sp500_history', 'S%26P%20500%20Historical%20Components%20%26%20Changes%20%28Updated%29.csv'), ('history_readme', 'README.md'), ('history_license', 'LICENSE')]:
            results.append(fetch(name, base + file))
    (ROOT / 'reports/source_probes.json').write_text(json.dumps(results, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
