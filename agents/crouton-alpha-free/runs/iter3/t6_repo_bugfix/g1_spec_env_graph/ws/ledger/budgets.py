"""Monthly budgets per category and how much of them is used."""
from dataclasses import dataclass
from decimal import Decimal

from .currency import to_minor_units
from .models import Transaction
from .utils import month_key, percent


@dataclass
class Budget:
    category: str
    limit_major: Decimal
    currency: str

    @property
    def limit_minor(self) -> int:
        return to_minor_units(self.limit_major, self.currency)


def budget_usage(transactions: list[Transaction], budgets: list[Budget], month: str) -> dict[str, float]:
    """Percent (0-100+) of each budget consumed in the given 'YYYY-MM' month."""
    spent: dict[str, int] = {}
    for t in transactions:
        if t.is_expense and month_key(t.posted_on) == month:
            spent[t.category] = spent.get(t.category, 0) - t.amount_minor
    return {b.category: percent(spent.get(b.category, 0), b.limit_minor) for b in budgets}


def over_budget(usage: dict[str, float], threshold: float = 100.0) -> list[str]:
    return sorted(c for c, p in usage.items() if p > threshold)
