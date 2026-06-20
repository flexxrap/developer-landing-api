import json
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path("data")
METRICS_FILE = DATA_DIR / "metrics.json"

_EMPTY = {"total": 0, "successful": 0, "rate_limited": 0, "by_day": {}}


def _load() -> dict:
    if not METRICS_FILE.exists():
        return dict(_EMPTY)
    try:
        return json.loads(METRICS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, IOError):
        return dict(_EMPTY)


def _save(data: dict) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    METRICS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def record(status: str) -> None:
    data = _load()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    data["total"] += 1
    if status == "success":
        data["successful"] += 1
    elif status == "rate_limited":
        data["rate_limited"] += 1

    day = data["by_day"].setdefault(today, {"total": 0, "successful": 0, "rate_limited": 0})
    day["total"] += 1
    if status == "success":
        day["successful"] += 1
    elif status == "rate_limited":
        day["rate_limited"] += 1

    _save(data)


def get_all() -> dict:
    return _load()
