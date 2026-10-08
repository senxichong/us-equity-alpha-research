"""Read-only host audit; never record environment variables or credentials."""
import json
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parents[1]
report = {
    'observed_at_utc': datetime.now(timezone.utc).isoformat(),
    'client_date': '2026-10-08',
    'python': sys.version,
    'executable': sys.executable,
    'platform': platform.platform(),
    'disk': {d: dict(zip(('total', 'used', 'free'), shutil.disk_usage(d))) for d in ['C:/', 'D:/']},
    'initial_state': 'Empty workspace; no Git repository; initialized during Phase 1.',
    'git_status': subprocess.run(['git', 'status', '--short', '--branch'], cwd=root, capture_output=True, text=True).stdout,
    'packages': json.loads(subprocess.check_output([sys.executable, '-m', 'pip', 'list', '--format=json'], text=True)),
}
(root / 'reports/environment.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps({k: v for k, v in report.items() if k not in ['packages', 'git_status']}, indent=2))
