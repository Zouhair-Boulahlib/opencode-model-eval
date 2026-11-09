"""Runtime configuration resolved from environment variables."""
import os
from pathlib import Path

DEFAULT_CURRENCY = os.environ.get("LEDGER_CURRENCY", "USD")
DEFAULT_DATA_FILE = Path(os.environ.get("LEDGER_DATA", "ledger.json"))
MAX_DESCRIPTION_LENGTH = 120
CATEGORY_FALLBACK = "uncategorized"


def data_file(path: str | None = None) -> Path:
    """Resolve the data file: explicit argument wins, then LEDGER_DATA, then ./ledger.json."""
    return Path(path) if path else DEFAULT_DATA_FILE
