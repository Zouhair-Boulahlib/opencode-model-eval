"""Reports over stored transactions. All money values returned as Decimal major units."""
from collections import defaultdict
from decimal import Decimal

from .currency import to_major_units
from .models import Transaction
from .utils import month_key, percent


def _only(transactions: list[Transaction], currency: str) -> list[Transaction]:
    ccy = currency.upper()
    return [t for t in transactions if t.currency == ccy]


def monthly_totals(transactions: list[Transaction], currency: str) -> dict[str, Decimal]:
    """Net total per month ('YYYY-MM'), in major units of `currency`."""
    sums: dict[str, int] = defaultdict(int)
    for t in _only(transactions, currency):
        sums[month_key(t.posted_on)] += t.amount_minor
    return {m: to_major_units(v, currency) for m, v in sorted(sums.items())}


def monthly_expenses(transactions: list[Transaction], currency: str) -> dict[str, Decimal]:
    sums: dict[str, int] = defaultdict(int)
    for t in _only(transactions, currency):
        if t.is_expense:
            sums[month_key(t.posted_on)] += -t.amount_minor
    return {m: to_major_units(v, currency) for m, v in sorted(sums.items())}


def category_breakdown(transactions: list[Transaction], currency: str) -> list[tuple[str, Decimal, float]]:
    """(category, spent, percent of all spending) for expenses, largest first."""
    spent: dict[str, int] = defaultdict(int)
    for t in _only(transactions, currency):
        if t.is_expense:
            spent[t.category] += -t.amount_minor
    total = sum(spent.values())
    rows = [(c, to_major_units(v, currency), percent(v, total)) for c, v in spent.items()]
    return sorted(rows, key=lambda r: (-r[1], r[0]))


def top_merchants(transactions: list[Transaction], currency: str, n: int = 5) -> list[tuple[str, Decimal]]:
    spent: dict[str, int] = defaultdict(int)
    for t in _only(transactions, currency):
        if t.is_expense:
            spent[t.description] += -t.amount_minor
    ranked = sorted(spent.items(), key=lambda kv: (-kv[1], kv[0]))[:n]
    return [(d, to_major_units(v, currency)) for d, v in ranked]
