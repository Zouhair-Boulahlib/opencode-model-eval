"""Order processing (legacy module)."""

from typing import NotRequired, TypedDict


class Item(TypedDict):
    sku: str
    qty: int


class Order(TypedDict):
    id: int
    customer: str
    items: list[Item]
    coupon: NotRequired[str]


class SkuInfo(TypedDict):
    price: float
    stock: int


Inventory = dict[str, SkuInfo]
Discounts = dict[str, int]


class FulfilledOrder(TypedDict):
    id: int
    customer: str
    total: float


class RejectedOrder(TypedDict):
    id: int
    reason: str


class ProcessResult(TypedDict):
    fulfilled: list[FulfilledOrder]
    rejected: list[RejectedOrder]
    revenue: float
    inventory: Inventory


def copy_inventory(inventory: Inventory) -> Inventory:
    """Return a deep-enough copy of the stock levels (input is not mutated)."""
    return {
        sku: {"price": info["price"], "stock": info["stock"]}
        for sku, info in inventory.items()
    }


def check_item(item: Item, inventory: Inventory) -> str | None:
    """Return a rejection reason for a single item, or None if it is valid."""
    sku = item["sku"]
    if sku not in inventory:
        return "unknown sku " + sku
    if item["qty"] <= 0:
        return "bad qty"
    if inventory[sku]["stock"] < item["qty"]:
        return "out of stock " + sku
    return None


def compute_items_total(items: list[Item], inventory: Inventory) -> tuple[float | None, str | None]:
    """Sum the line-item costs, stopping at the first invalid item.

    Returns (total, None) when every item is valid, else (None, reason).
    """
    total = 0.0
    for item in items:
        reason = check_item(item, inventory)
        if reason is not None:
            return None, reason
        total = total + inventory[item["sku"]]["price"] * item["qty"]
    return total, None


def apply_coupon(total: float, coupon: str | None, discounts: Discounts) -> tuple[float | None, str | None]:
    """Apply a coupon discount to a total, or reject the order.

    Returns (discounted_total, None) on success, else (None, reason).
    """
    if not coupon:
        return total, None
    if coupon in discounts:
        return total - total * discounts[coupon] / 100.0, None
    return None, "bad coupon"


def reserve_stock(order: Order, inventory: Inventory) -> None:
    """Deduct the order's items from the working inventory copy."""
    for item in order["items"]:
        inventory[item["sku"]]["stock"] = inventory[item["sku"]]["stock"] - item["qty"]


def process_orders(
    orders: list[Order],
    inventory: Inventory,
    discounts: Discounts,
) -> ProcessResult:
    """Process orders in sequence against inventory.

    orders:    list of dicts {"id": int, "customer": str, "items": [{"sku": str, "qty": int}], "coupon": str (optional)}
    inventory: dict sku -> {"price": float, "stock": int}; it is NOT mutated
    discounts: dict coupon code -> percent off (int)
    returns:   {"fulfilled": [{"id", "customer", "total"}], "rejected": [{"id", "reason"}],
                "revenue": float, "inventory": updated copy of inventory}
    """
    results: ProcessResult = {
        "fulfilled": [],
        "rejected": [],
        "revenue": 0.0,
        "inventory": {},
    }
    inv = copy_inventory(inventory)

    for order in orders:
        total, reason = compute_items_total(order["items"], inv)
        if total is not None:
            total, reason = apply_coupon(total, order.get("coupon"), discounts)

        if total is None:
            assert reason is not None
            results["rejected"].append({"id": order["id"], "reason": reason})
            continue

        reserve_stock(order, inv)
        total = round(total, 2)
        results["fulfilled"].append(
            {"id": order["id"], "customer": order["customer"], "total": total}
        )
        results["revenue"] = round(results["revenue"] + total, 2)

    results["inventory"] = inv
    return results
