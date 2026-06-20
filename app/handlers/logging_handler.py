import logging
from pathlib import Path

_logs_dir = Path("logs")
_logs_dir.mkdir(exist_ok=True)

_logger = logging.getLogger("requests")
_logger.setLevel(logging.INFO)

_file_handler = logging.FileHandler(_logs_dir / "requests.log", encoding="utf-8")
_file_handler.setFormatter(
    logging.Formatter("%(asctime)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
)
_logger.addHandler(_file_handler)


def log_request(ip: str, email: str, status: str) -> None:
    _logger.info("IP=%-15s | email=%-40s | status=%s", ip, email, status)
