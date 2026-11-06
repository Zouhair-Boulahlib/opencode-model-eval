"""Simple in-memory inventory manager."""
from dataclasses import dataclass, field


@dataclass
class Item:
    sku: str
    name: str
    qty: int
    price: float
    tags: list = field(default_factory=list)


class Inventory:
    def __init__(self, low_stock_threshold: int = 5):
        self.items: dict[str, Item] = {}
        self.low_stock_threshold = low_stock_threshold

    def add(self, sku, name, qty, price, tags=None):
        """Add stock. If the SKU exists, only its qty is increased.

        Each item owns its own tags list.
        """
        if qty <= 0:
            raise ValueError("qty must be positive")
        if sku in self.items:
            self.items[sku].qty += qty
        else:
            self.items[sku] = Item(sku, name, qty, price, list(tags) if tags is not None else [])
        return self.items[sku]

    def remove(self, sku, qty):
        """Remove stock. The item stays in the inventory (qty 0) when fully removed."""
        if sku not in self.items:
            raise KeyError(sku)
        item = self.items[sku]
        if qty > item.qty:
            raise ValueError("insufficient stock")
        item.qty -= qty
        return item

    def get(self, sku):
        return self.items.get(sku)

    def low_stock(self):
        """Sorted SKUs whose qty is at or below the threshold."""
        return sorted(s for s, i in self.items.items() if i.qty <= self.low_stock_threshold)

    def total_value(self):
        return round(sum(i.qty * i.price for i in self.items.values()), 2)

    def search(self, term):
        """Case-insensitive substring match on name or any tag, sorted by sku."""
        needle = term.lower()
        return sorted(
            (
                i
                for i in self.items.values()
                if needle in i.name.lower() or any(needle in tag.lower() for tag in i.tags)
            ),
            key=lambda i: i.sku,
        )

    def page(self, number, size):
        """1-indexed page of items sorted by sku."""
        ordered = sorted(self.items.values(), key=lambda i: i.sku)
        start = (number - 1) * size
        return ordered[start:start + size]
