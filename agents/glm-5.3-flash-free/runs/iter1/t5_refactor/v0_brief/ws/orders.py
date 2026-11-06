"""Order processing (legacy module)."""
from typing import Any

Order = dict[str, Any]
Item = dict[str, Any]
StockEntry = dict[str, Any]
Inventory = dict[str, StockEntry]


def clone_inventory(inventory: Inventory) -> Inventory:
    """Return an independent copy of the inventory."""
    return {
        sku: {"price": entry["price"], "stock": entry["stock"]}
        for sku, entry in inventory.items()
    }


def price_items(items: list[Item], inv: Inventory) -> tuple[float, str | None]:
    """Sum the item prices, returning (total, error_reason).

    The reason is None when every item is valid (known sku, positive qty,
    enough stock).
    """
    total = 0.0
    for it in items:
        sku = it["sku"]
        if sku not in inv:
            return 0.0, "unknown sku " + sku
        if it["qty"] <= 0:
            return 0.0, "bad qty"
        if inv[sku]["stock"] < it["qty"]:
            return 0.0, "out of stock " + sku
        total = total + inv[sku]["price"] * it["qty"]
    return total, None


def apply_coupon(total: float, order: Order, discounts: dict[str, int]) -> tuple[float, str | None]:
    """Apply the order's coupon percent off, returning (total, error_reason)."""
    coupon = order.get("coupon")
    if not coupon:
        return total, None
    if coupon not in discounts:
        return 0.0, "bad coupon"
    return total - total * discounts[coupon] / 100.0, None


def deduct_stock(items: list[Item], inv: Inventory) -> None:
    """Remove ordered quantities from the inventory copy, in place."""
    for it in items:
        inv[it["sku"]]["stock"] = inv[it["sku"]]["stock"] - it["qty"]


def process_order(order: Order, inv: Inventory, discounts: dict[str, int]) -> dict[str, Any]:
    """Fulfil one order or explain why it is rejected."""
    total, error = price_items(order["items"], inv)
    if error is None:
        total, error = apply_coupon(total, order, discounts)
    if error is not None:
        return {"id": order["id"], "reason": error}
    deduct_stock(order["items"], inv)
    total = round(total, 2)
    return {"id": order["id"], "customer": order["customer"], "total": total}


def process_orders(orders: list[Order], inventory: Inventory, discounts: dict[str, int]) -> dict[str, Any]:
    """Process orders in sequence against inventory.

    orders:    list of dicts {"id": int, "customer": str, "items": [{"sku": str, "qty": int}], "coupon": str (optional)}
    inventory: dict sku -> {"price": float, "stock": int}; it is NOT mutated
    discounts: dict coupon code -> percent off (int)
    returns:   {"fulfilled": [{"id", "customer", "total"}], "rejected": [{"id", "reason"}],
                "revenue": float, "inventory": updated copy of inventory}
    """
    inv = clone_inventory(inventory)
    results: dict[str, Any] = {"fulfilled": [], "rejected": [], "revenue": 0.0}
    for o in orders:
        outcome = process_order(o, inv, discounts)
        if "reason" in outcome:
            results["rejected"].append(outcome)
        else:
            results["fulfilled"].append(outcome)
            results["revenue"] = round(results["revenue"] + outcome["total"], 2)
    results["inventory"] = inv
    return results
