"""Order processing (legacy module).

Contract for process_orders(orders, inventory, discounts):
    orders:    list of dicts {"id": int, "customer": str, "items": [{"sku": str, "qty": int}], "coupon": str (optional)}
    inventory: dict sku -> {"price": float, "stock": int}; it is NOT mutated
    discounts: dict coupon code -> percent off (int)
    returns:   {"fulfilled": [{"id", "customer", "total"}], "rejected": [{"id", "reason"}],
                "revenue": float, "inventory": updated copy of inventory}
"""

from typing import Any

Item = dict[str, Any]
Order = dict[str, Any]
StockEntry = dict[str, Any]
ResultDict = dict[str, Any]


def _copy_inventory(inventory: dict[str, StockEntry]) -> dict[str, StockEntry]:
    """Return a deep-enough copy of the inventory so it is not mutated."""
    inv: dict[str, StockEntry] = {}
    for k in inventory:
        inv[k] = {"price": inventory[k]["price"], "stock": inventory[k]["stock"]}
    return inv


def _check_items(order: Order, inv: dict[str, StockEntry]) -> str | None:
    """Validate order items against inventory; return reason string if invalid."""
    total = 0.0
    for it in order["items"]:
        if it["sku"] not in inv:
            return "unknown sku " + it["sku"]
        if it["qty"] <= 0:
            return "bad qty"
        if inv[it["sku"]]["stock"] < it["qty"]:
            return "out of stock " + it["sku"]
        total = total + inv[it["sku"]]["price"] * it["qty"]
    return None


def _coupon_discount(
    order: Order,
    discounts: dict[str, int],
    total: float,
) -> tuple[str | None, float]:
    """Apply coupon discount if valid; return (reason, adjusted total)."""
    coupon = order.get("coupon")
    if not coupon:
        return None, total
    if coupon in discounts:
        return None, total - total * discounts[coupon] / 100.0
    return "bad coupon", total


def _process_one(
    order: Order,
    inv: dict[str, StockEntry],
    discounts: dict[str, int],
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    """Process a single order; return (fulfilled_record, rejected_record)."""
    reason = _check_items(order, inv)
    if reason is None:
        total = sum((inv[it["sku"]]["price"] * it["qty"] for it in order["items"]), 0.0)
        reason, total = _coupon_discount(order, discounts, total)
    if reason is not None:
        return None, {"id": order["id"], "reason": reason}
    for it in order["items"]:
        inv[it["sku"]]["stock"] = inv[it["sku"]]["stock"] - it["qty"]
    total = round(total, 2)
    fulfilled = {"id": order["id"], "customer": order["customer"], "total": total}
    return fulfilled, None


def process_orders(
    orders: list[Order],
    inventory: dict[str, StockEntry],
    discounts: dict[str, int],
) -> ResultDict:
    """Process orders in sequence against inventory (see module docstring)."""
    results: ResultDict = {"fulfilled": [], "rejected": [], "revenue": 0.0}
    inv = _copy_inventory(inventory)
    for o in orders:
        fulfilled, rejected = _process_one(o, inv, discounts)
        if fulfilled is not None:
            results["fulfilled"].append(fulfilled)
            results["revenue"] = round(results["revenue"] + fulfilled["total"], 2)
        else:
            results["rejected"].append(rejected)
    results["inventory"] = inv
    return results
