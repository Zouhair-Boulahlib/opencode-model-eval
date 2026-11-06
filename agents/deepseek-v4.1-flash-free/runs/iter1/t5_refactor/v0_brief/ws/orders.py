"""Order processing (legacy module)."""

from typing import Any, Dict, List, Optional, Tuple

Order = Dict[str, Any]
Inventory = Dict[str, Dict[str, Any]]
Discounts = Dict[str, int]
Results = Dict[str, Any]


def _copy_inventory(inventory: Inventory) -> Inventory:
    """Return a shallow copy of each inventory entry so the input is not mutated."""
    inv: Inventory = {}
    for sku in inventory:
        inv[sku] = {"price": inventory[sku]["price"], "stock": inventory[sku]["stock"]}
    return inv


def _price_items(
    items: List[Dict[str, Any]], inventory: Inventory
) -> Tuple[float, Optional[str]]:
    """Validate items and compute the undiscounted total.

    Returns (total, reason). ``reason`` is None when every item is valid.
    """
    total = 0.0
    for item in items:
        sku = item["sku"]
        if sku not in inventory:
            return 0.0, "unknown sku " + sku
        if item["qty"] <= 0:
            return 0.0, "bad qty"
        if inventory[sku]["stock"] < item["qty"]:
            return 0.0, "out of stock " + sku
        total = total + inventory[sku]["price"] * item["qty"]
    return total, None


def _apply_coupon(
    order: Order, total: float, discounts: Discounts
) -> Tuple[float, Optional[str]]:
    """Apply an optional coupon, returning (total, reason).

    An absent or empty coupon is ignored. An unknown coupon is rejected.
    """
    coupon = order.get("coupon")
    if not coupon:
        return total, None
    if coupon not in discounts:
        return total, "bad coupon"
    return total - total * discounts[coupon] / 100.0, None


def _reserve_stock(items: List[Dict[str, Any]], inventory: Inventory) -> None:
    """Decrement inventory stock for every item in a fulfilled order."""
    for item in items:
        sku = item["sku"]
        inventory[sku]["stock"] = inventory[sku]["stock"] - item["qty"]


def _process_order(
    order: Order, inventory: Inventory, discounts: Discounts
) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]], float]:
    """Process a single order against the mutable inventory copy.

    Returns (fulfilled_entry, rejected_entry, total) where exactly one of the
    first two entries is set. ``total`` is 0.0 for rejected orders.
    """
    total, reason = _price_items(order["items"], inventory)
    if reason is None:
        total, reason = _apply_coupon(order, total, discounts)

    if reason is not None:
        return None, {"id": order["id"], "reason": reason}, 0.0

    _reserve_stock(order["items"], inventory)
    total = round(total, 2)
    fulfilled = {"id": order["id"], "customer": order["customer"], "total": total}
    return fulfilled, None, total


def process_orders(
    orders: List[Order], inventory: Inventory, discounts: Discounts
) -> Results:
    """Process orders in sequence against inventory.

    orders:    list of dicts {"id": int, "customer": str, "items": [{"sku": str, "qty": int}], "coupon": str (optional)}
    inventory: dict sku -> {"price": float, "stock": int}; it is NOT mutated
    discounts: dict coupon code -> percent off (int)
    returns:   {"fulfilled": [{"id", "customer", "total"}], "rejected": [{"id", "reason"}],
                "revenue": float, "inventory": updated copy of inventory}
    """
    results: Results = {"fulfilled": [], "rejected": [], "revenue": 0.0}
    inv = _copy_inventory(inventory)

    for order in orders:
        fulfilled, rejected, total = _process_order(order, inv, discounts)
        if fulfilled is not None:
            results["fulfilled"].append(fulfilled)
            results["revenue"] = round(results["revenue"] + total, 2)
        else:
            results["rejected"].append(rejected)

    results["inventory"] = inv
    return results
