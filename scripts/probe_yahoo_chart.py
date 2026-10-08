"""Single public chart endpoint diagnostic using standard requests, not cookies.

No automatic retries, proxy rotation, or challenge solving. A 429 stops this path.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.probe_sources import fetch

if __name__ == '__main__':
    fetch('yahoo_chart_aapl', 'https://query1.finance.yahoo.com/v8/finance/chart/AAPL?period1=1514764800&period2=1791417600&interval=1d&events=div%2Csplits')
