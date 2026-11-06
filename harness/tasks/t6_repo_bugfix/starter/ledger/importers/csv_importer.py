"""CSV importer. Expected columns: date, description, amount, category (optional), tags (optional).
Amounts in the file are in major units ("12.34"), as exported by most banks."""
import csv
from pathlib import Path

from ..config import CATEGORY_FALLBACK
from ..models import Transaction
from ..parsing import parse_amount, parse_date, parse_tags
from ..utils import stable_id

REQUIRED_COLUMNS = {"date", "description", "amount"}


def _row_to_transaction(row: dict[str, str], currency: str) -> Transaction:
    posted_on = parse_date(row["date"])
    amount = parse_amount(row["amount"])
    # bank exports use two decimals, so shift by 100 to get minor units
    amount_minor = int(amount * 100)
    return Transaction(
        id=stable_id(posted_on, row["description"], amount, currency),
        posted_on=posted_on,
        description=row["description"].strip(),
        amount_minor=amount_minor,
        currency=currency.upper(),
        category=(row.get("category") or CATEGORY_FALLBACK).strip().lower(),
        tags=parse_tags(row.get("tags")),
    )


def import_csv(path: Path, currency: str) -> list[Transaction]:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"CSV is missing columns: {sorted(missing)}")
        return [_row_to_transaction(row, currency) for row in reader if row.get("amount")]
