"""Order processing (legacy module)."""

from typing import Any, Dict, Optional, Tuple

Inventory = Dict[str, Dict[str, Any]]
Order = Dict[str, Any]
Result = Dict[str, Any]


def _copy_inventory(inventory: Inventory) -> Inventory:
    """Return a copy of inventory with each sku's price and stock."""
    return {
        sku: {"price": data["price"], "stock": data["stock"]}
        for sku, data in inventory.items()
    }


def _price_order(order: Order, inv: Inventory) -> Tuple[bool, Optional[str], float]:
    """Validate items and compute an order's pre-coupon total."""
    total = 0.0
    for item in order["items"]:
        sku = item["sku"]
        qty = item["qty"]
        if sku not in inv:
            return False, "unknown sku " + sku, 0.0
        if qty <= 0:
            return False, "bad qty", 0.0
        if inv[sku]["stock"] < qty:
            return False, "out of stock " + sku, 0.0
        total = total + inv[sku]["price"] * qty
    return True, None, total


def _apply_coupon(
    order: Order, total: float, discounts: Dict[str, int]
) -> Tuple[bool, Optional[str], float]:
    """Apply the order's coupon, if any, to the given total."""
    if "coupon" in order and order["coupon"]:
        coupon = order["coupon"]
        if coupon in discounts:
            total = total - total * discounts[coupon] / 100.0
        else:
            return False, "bad coupon", total
    return True, None, total


def _process_one(
    order: Order, inv: Inventory, discounts: Dict[str, int]
) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """Process one order, mutating inv; return (fulfilled, rejected)."""
    ok, reason, total = _price_order(order, inv)
    if ok:
        ok, reason, total = _apply_coupon(order, total, discounts)
    if not ok:
        return None, {"id": order["id"], "reason": reason}
    for item in order["items"]:
        inv[item["sku"]]["stock"] = inv[item["sku"]]["stock"] - item["qty"]
    total = round(total, 2)
    entry = {"id": order["id"], "customer": order["customer"], "total": total}
    return entry, None


def process_orders(
    orders: Any, inventory: Inventory, discounts: Dict[str, int]
) -> Result:
    """Process orders in sequence against a copy of inventory.

    Returns {"fulfilled": [...], "rejected": [...], "revenue": float,
    "inventory": updated copy}.
    """
    results = {"fulfilled": [], "rejected": [], "revenue": 0.0}
    inv = _copy_inventory(inventory)
    for order in orders:
        fulfilled, rejected = _process_one(order, inv, discounts)
        if fulfilled is not None:
            results["fulfilled"].append(fulfilled)
            results["revenue"] = round(results["revenue"] + fulfilled["total"], 2)
        else:
            results["rejected"].append(rejected)
    results["inventory"] = inv
    return results
