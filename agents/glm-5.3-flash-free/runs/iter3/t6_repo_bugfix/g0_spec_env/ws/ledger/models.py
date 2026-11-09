"""Core data types."""
from dataclasses import dataclass, field
from datetime import date


@dataclass
class Transaction:
    """A single money movement. `amount_minor` is an integer in the currency's minor unit
    (e.g. cents). Negative values are expenses, positive values are income."""

    id: str
    posted_on: date
    description: str
    amount_minor: int
    currency: str
    category: str = "uncategorized"
    tags: list[str] = field(default_factory=list)

    @property
    def is_expense(self) -> bool:
        return self.amount_minor < 0

    def with_category(self, category: str) -> "Transaction":
        return Transaction(self.id, self.posted_on, self.description, self.amount_minor,
                           self.currency, category, list(self.tags))
