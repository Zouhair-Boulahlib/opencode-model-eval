"""Order processing."""

from typing import Any, Dict, List, Optional, Tuple


def _copy_inventory(inventory: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Return a copy of the inventory."""
    return {sku: {"price": item["price"], "stock": item["stock"]} for sku, item in inventory.items()}


def _order_total(
    order: Dict[str, Any], inventory: Dict[str, Dict[str, Any]]
) -> Tuple[bool, Optional[str], float]:
    """Return (ok, reason, total) for an order against the inventory."""
    ok = True
    reason: Optional[str] = None
    total = 0.0
    for item in order["items"]:
        if item["sku"] not in inventory:
            ok, reason = False, "unknown sku " + item["sku"]
            break
        if item["qty"] <= 0:
            ok, reason = False, "bad qty"
            break
        if inventory[item["sku"]]["stock"] < item["qty"]:
            ok, reason = False, "out of stock " + item["sku"]
            break
        total = total + inventory[item["sku"]]["price"] * item["qty"]
    return ok, reason, total


def _apply_discount(
    order: Dict[str, Any], discounts: Dict[str, Any], total: float
) -> Tuple[bool, Optional[str], float]:
    """Apply the order's coupon to the total."""
    ok = True
    reason: Optional[str] = None
    if order.get("coupon"):
        if order["coupon"] in discounts:
            total = total - total * discounts[order["coupon"]] / 100.0
        else:
            ok = False
            reason = "bad coupon"
    return ok, reason, total


def _process_one(
    order: Dict[str, Any],
    inventory: Dict[str, Dict[str, Any]],
    discounts: Dict[str, Any],
) -> Tuple[bool, Optional[Dict[str, Any]], Optional[float]]:
    """Process one order and update the working inventory stock."""
    ok, reason, total = _order_total(order, inventory)
    if ok:
        ok, reason, total = _apply_discount(order, discounts, total)
    if not ok:
        return False, {"id": order["id"], "reason": reason}, None
    for item in order["items"]:
        inventory[item["sku"]]["stock"] = inventory[item["sku"]]["stock"] - item["qty"]
    total = round(total, 2)
    return True, {"id": order["id"], "customer": order["customer"], "total": total}, total


def process_orders(
    orders: List[Dict[str, Any]],
    inventory: Dict[str, Dict[str, Any]],
    discounts: Dict[str, Any],
) -> Dict[str, Any]:
    """Process orders in sequence against inventory."""
    results: Dict[str, Any] = {"fulfilled": [], "rejected": [], "revenue": 0.0}
    inv = _copy_inventory(inventory)
    for order in orders:
        ok, entry, total = _process_one(order, inv, discounts)
        if ok:
            results["fulfilled"].append(entry)
            results["revenue"] = round(results["revenue"] + total, 2)
        else:
            results["rejected"].append(entry)
    results["inventory"] = inv
    return results
