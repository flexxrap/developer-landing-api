import json
import time
from pathlib import Path

DATA_DIR = Path("data")
RATE_LIMITS_FILE = DATA_DIR / "rate_limits.json"
MAX_REQUESTS = 5
WINDOW_SECONDS = 3600


def _load() -> dict:
    if not RATE_LIMITS_FILE.exists():
        return {}
    try:
        return json.loads(RATE_LIMITS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, IOError):
        return {}


def _save(data: dict) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    RATE_LIMITS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def check_rate_limit(ip: str) -> tuple[bool, int]:
    data = _load()
    now = time.time()

    if ip not in data:
        data[ip] = {"count": 1, "window_start": now}
        _save(data)
        return True, 0

    entry = data[ip]
    elapsed = now - entry["window_start"]

    if elapsed >= WINDOW_SECONDS:
        data[ip] = {"count": 1, "window_start": now}
        _save(data)
        return True, 0

    if entry["count"] >= MAX_REQUESTS:
        return False, int(WINDOW_SECONDS - elapsed)

    data[ip]["count"] += 1
    _save(data)
    return True, 0
