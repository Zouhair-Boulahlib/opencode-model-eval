"""Minimal QIF importer (Quicken Interchange Format). Records are separated by '^' lines;
'D' = date, 'T' = amount in major units, 'P' = payee, 'L' = category."""
from pathlib import Path

from ..config import CATEGORY_FALLBACK
from ..currency import to_minor_units
from ..models import Transaction
from ..parsing import parse_amount, parse_date
from ..utils import stable_id


def import_qif(path: Path, currency: str) -> list[Transaction]:
    out: list[Transaction] = []
    record: dict[str, str] = {}
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("!"):
            continue
        if line == "^":
            if record:
                out.append(_build(record, currency))
            record = {}
            continue
        record[line[0]] = line[1:].strip()
    if record:
        out.append(_build(record, currency))
    return out


def _build(record: dict[str, str], currency: str) -> Transaction:
    posted_on = parse_date(record["D"])
    amount = parse_amount(record["T"])
    return Transaction(
        id=stable_id(posted_on, record.get("P", ""), amount, currency),
        posted_on=posted_on,
        description=record.get("P", "").strip(),
        amount_minor=to_minor_units(amount, currency),
        currency=currency.upper(),
        category=(record.get("L") or CATEGORY_FALLBACK).strip().lower(),
    )
