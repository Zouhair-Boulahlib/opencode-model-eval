"""JSON file persistence. Amounts are stored as integers (minor units); dates as ISO strings."""
import json
from datetime import date
from pathlib import Path

from .models import Transaction


def _to_record(tx: Transaction) -> dict:
    return {
        "id": tx.id,
        "posted_on": tx.posted_on.isoformat(),
        "description": tx.description,
        "amount_minor": int(tx.amount_minor),
        "currency": tx.currency.upper(),
        "category": tx.category,
        "tags": list(tx.tags),
    }


def _from_record(rec: dict) -> Transaction:
    return Transaction(
        id=rec["id"],
        posted_on=date.fromisoformat(rec["posted_on"]),
        description=rec["description"],
        amount_minor=int(rec["amount_minor"]),
        currency=rec["currency"],
        category=rec.get("category", "uncategorized"),
        tags=list(rec.get("tags", [])),
    )


def load(path: Path) -> list[Transaction]:
    if not Path(path).exists():
        return []
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return [_from_record(r) for r in data.get("transactions", [])]


def save(path: Path, transactions: list[Transaction]) -> None:
    payload = {"version": 2, "transactions": [_to_record(t) for t in transactions]}
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)


def upsert(path: Path, new: list[Transaction]) -> int:
    """Merge by id; returns how many were added."""
    existing = {t.id: t for t in load(path)}
    added = 0
    for tx in new:
        if tx.id not in existing:
            added += 1
        existing[tx.id] = tx
    save(path, sorted(existing.values(), key=lambda t: (t.posted_on, t.id)))
    return added
