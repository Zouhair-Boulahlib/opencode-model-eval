"""JSON importer for the exchange format used by the mobile app:
{"currency": "USD", "items": [{"date": "2024-03-01", "description": "...", "amount": "12.34", "category": "...", "tags": "a,b"}]}"""
import json
from decimal import Decimal
from pathlib import Path

from ..config import CATEGORY_FALLBACK
from ..currency import to_minor_units
from ..models import Transaction
from ..parsing import parse_date, parse_tags
from ..utils import stable_id


def import_json(path: Path, currency: str | None = None) -> list[Transaction]:
    with open(path, encoding="utf-8") as f:
        payload = json.load(f)
    ccy = (currency or payload.get("currency") or "USD").upper()
    out: list[Transaction] = []
    for item in payload.get("items", []):
        posted_on = parse_date(item["date"])
        amount = Decimal(str(item["amount"]))
        out.append(Transaction(
            id=stable_id(posted_on, item["description"], amount, ccy),
            posted_on=posted_on,
            description=item["description"].strip(),
            amount_minor=to_minor_units(amount, ccy),
            currency=ccy,
            category=(item.get("category") or CATEGORY_FALLBACK).strip().lower(),
            tags=parse_tags(item.get("tags")),
        ))
    return out
