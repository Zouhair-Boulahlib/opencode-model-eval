"""Order processing (legacy module)."""

from typing import Any, Dict, List, Optional, Tuple

Item = Dict[str, Any]
Order = Dict[str, Any]
Inventory = Dict[str, Dict[str, Any]]
Discounts = Dict[str, int]
Results = Dict[str, Any]


def copy_inventory(inventory: Inventory) -> Inventory:
    """Return a fresh copy holding only price and stock per sku."""
    inv: Inventory = {}
    for sku in inventory:
        inv[sku] = {"price": inventory[sku]["price"], "stock": inventory[sku]["stock"]}
    return inv


def check_item(item: Item, inv: Inventory) -> Optional[str]:
    """Return a rejection reason for one item, or None when it is valid."""
    sku = item["sku"]
    if sku not in inv:
        return "unknown sku " + sku
    if item["qty"] <= 0:
        return "bad qty"
    if inv[sku]["stock"] < item["qty"]:
        return "out of stock " + sku
    return None


def price_items(items: List[Item], inv: Inventory) -> Tuple[bool, float, Optional[str]]:
    """Sum item prices, stopping at the first invalid item."""
    total = 0.0
    for item in items:
        reason = check_item(item, inv)
        if reason is not None:
            return False, 0.0, reason
        total += inv[item["sku"]]["price"] * item["qty"]
    return True, total, None


def apply_coupon(total: float, coupon: Optional[str],
                 discounts: Discounts) -> Tuple[bool, float, Optional[str]]:
    """Apply a coupon discount, or report a bad coupon."""
    if not coupon:
        return True, total, None
    if coupon not in discounts:
        return False, 0.0, "bad coupon"
    return True, total - total * discounts[coupon] / 100.0, None


def price_order(order: Order, inv: Inventory,
                discounts: Discounts) -> Tuple[bool, float, Optional[str]]:
    """Price one order's items and apply its coupon, if any."""
    ok, total, reason = price_items(order["items"], inv)
    if not ok:
        return False, 0.0, reason
    return apply_coupon(total, order.get("coupon"), discounts)


def fulfil(order: Order, total: float, inv: Inventory, results: Results) -> None:
    """Deduct stock and record a fulfilled order with its rounded total."""
    for item in order["items"]:
        inv[item["sku"]]["stock"] -= item["qty"]
    total = round(total, 2)
    results["fulfilled"].append({"id": order["id"], "customer": order["customer"], "total": total})
    results["revenue"] = round(results["revenue"] + total, 2)


def reject(order: Order, reason: Optional[str], results: Results) -> None:
    """Record a rejected order together with its reason."""
    results["rejected"].append({"id": order["id"], "reason": reason})


def process_orders(orders: List[Order], inventory: Inventory, discounts: Discounts) -> Results:
    """Process orders in sequence against inventory.

    orders:    list of dicts {"id": int, "customer": str, "items": [{"sku": str, "qty": int}], "coupon": str (optional)}
    inventory: dict sku -> {"price": float, "stock": int}; it is NOT mutated
    discounts: dict coupon code -> percent off (int)
    returns:   {"fulfilled": [...], "rejected": [...], "revenue": float, "inventory": updated copy}
    """
    results: Results = {"fulfilled": [], "rejected": [], "revenue": 0.0}
    inv = copy_inventory(inventory)
    for order in orders:
        ok, total, reason = price_order(order, inv, discounts)
        if ok:
            fulfil(order, total, inv, results)
        else:
            reject(order, reason, results)
    results["inventory"] = inv
    return results
