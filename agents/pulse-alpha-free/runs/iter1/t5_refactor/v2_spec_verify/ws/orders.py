"""Order processing (legacy module)."""

from typing import Any, Dict, List, Optional, Tuple

Item = Dict[str, Any]
Order = Dict[str, Any]
Inventory = Dict[str, Dict[str, Any]]
Discounts = Dict[str, int]
Result = Dict[str, Any]


def _copy_inventory(inventory: Inventory) -> Inventory:
    return {sku: {"price": data["price"], "stock": data["stock"]} for sku, data in inventory.items()}


def _item_error(item: Item, inv: Inventory) -> Optional[str]:
    sku = item["sku"]
    if sku not in inv:
        return "unknown sku " + sku
    if item["qty"] <= 0:
        return "bad qty"
    if inv[sku]["stock"] < item["qty"]:
        return "out of stock " + sku
    return None


def _subtotal(items: List[Item], inv: Inventory) -> Tuple[float, Optional[str]]:
    total = 0.0
    for item in items:
        error = _item_error(item, inv)
        if error is not None:
            return 0.0, error
        total = total + inv[item["sku"]]["price"] * item["qty"]
    return total, None


def _apply_coupon(total: float, coupon: Optional[str], discounts: Discounts) -> Tuple[float, Optional[str]]:
    if not coupon:
        return total, None
    if coupon in discounts:
        return total - total * discounts[coupon] / 100.0, None
    return total, "bad coupon"


def _deduct_stock(items: List[Item], inv: Inventory) -> None:
    for item in items:
        inv[item["sku"]]["stock"] = inv[item["sku"]]["stock"] - item["qty"]


def _fulfill(results: Result, inv: Inventory, order: Order, total: float) -> None:
    _deduct_stock(order["items"], inv)
    total = round(total, 2)
    results["fulfilled"].append({"id": order["id"], "customer": order["customer"], "total": total})
    results["revenue"] = round(results["revenue"] + total, 2)


def process_orders(orders: List[Order], inventory: Inventory, discounts: Discounts) -> Result:
    """Process orders in sequence against inventory.

    inventory is NOT mutated; returns dict with fulfilled, rejected, revenue, inventory.
    """
    results: Result = {"fulfilled": [], "rejected": [], "revenue": 0.0}
    inv = _copy_inventory(inventory)
    for order in orders:
        total, reason = _subtotal(order["items"], inv)
        if reason is None:
            total, reason = _apply_coupon(total, order.get("coupon"), discounts)
        if reason is None:
            _fulfill(results, inv, order, total)
        else:
            results["rejected"].append({"id": order["id"], "reason": reason})
    results["inventory"] = inv
    return results
