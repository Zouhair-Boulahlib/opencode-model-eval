"""Order processing (legacy module)."""

from typing import Any, Optional

Item = dict[str, Any]
Order = dict[str, Any]
Inventory = dict[str, dict[str, Any]]
Discounts = dict[str, int]
Results = dict[str, Any]


def copy_inventory(inventory: Inventory) -> Inventory:
    """Return a fresh copy holding only price and stock for each SKU."""
    return {sku: {"price": e["price"], "stock": e["stock"]} for sku, e in inventory.items()}


def check_items(items: list[Item], inv: Inventory) -> tuple[float, Optional[str]]:
    """Sum item costs; return (total, None) when valid, else (0.0, reason)."""
    total = 0.0
    for it in items:
        sku, qty = it["sku"], it["qty"]
        if sku not in inv:
            return 0.0, "unknown sku " + sku
        if qty <= 0:
            return 0.0, "bad qty"
        if inv[sku]["stock"] < qty:
            return 0.0, "out of stock " + sku
        total = total + inv[sku]["price"] * qty
    return total, None


def apply_discount(total: float, coupon: Optional[str], discounts: Discounts) -> tuple[float, Optional[str]]:
    """Apply a percent-off coupon; return (total, None) or (total, 'bad coupon')."""
    if not coupon:
        return total, None
    if coupon in discounts:
        return total - total * discounts[coupon] / 100.0, None
    return total, "bad coupon"


def deduct_stock(inv: Inventory, items: list[Item]) -> None:
    """Remove ordered quantities from the working inventory copy."""
    for it in items:
        inv[it["sku"]]["stock"] = inv[it["sku"]]["stock"] - it["qty"]


def process_one(order: Order, inv: Inventory, discounts: Discounts) -> tuple[bool, Optional[str], float]:
    """Validate, discount and stock one order; return (ok, reason, total)."""
    total, reason = check_items(order["items"], inv)
    if reason is not None:
        return False, reason, 0.0
    total, reason = apply_discount(total, order.get("coupon"), discounts)
    if reason is not None:
        return False, reason, 0.0
    deduct_stock(inv, order["items"])
    return True, None, round(total, 2)


def process_orders(orders: list[Order], inventory: Inventory, discounts: Discounts) -> Results:
    """Process orders in sequence against inventory (inventory is not mutated).

    Returns {"fulfilled": [{"id", "customer", "total"}],
             "rejected": [{"id", "reason"}], "revenue": float,
             "inventory": updated copy of inventory}.
    """
    results: Results = {"fulfilled": [], "rejected": [], "revenue": 0.0}
    inv = copy_inventory(inventory)
    for o in orders:
        ok, reason, total = process_one(o, inv, discounts)
        if ok:
            results["fulfilled"].append({"id": o["id"], "customer": o["customer"], "total": total})
            results["revenue"] = round(results["revenue"] + total, 2)
        else:
            results["rejected"].append({"id": o["id"], "reason": reason})
    results["inventory"] = inv
    return results
