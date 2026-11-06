"""Order processing (legacy module)."""

from typing import Any, Dict, List, Optional, Tuple

Item = Dict[str, Any]
Order = Dict[str, Any]
Inventory = Dict[str, Dict[str, Any]]
Discounts = Dict[str, int]


def _copy_inventory(inventory: Inventory) -> Inventory:
    """Return a shallow-per-sku copy so the caller's inventory is untouched."""
    return {
        sku: {"price": data["price"], "stock": data["stock"]}
        for sku, data in inventory.items()
    }


def _price_items(
    order: Order, inventory: Inventory
) -> Tuple[bool, Optional[str], float]:
    """Validate an order's items and compute its pre-discount total.

    Returns (ok, rejection_reason, total). Checks each item in order:
    known sku, positive quantity, then sufficient stock.
    """
    total = 0.0
    for item in order["items"]:
        sku = item["sku"]
        if sku not in inventory:
            return False, "unknown sku " + sku, total
        if item["qty"] <= 0:
            return False, "bad qty", total
        if inventory[sku]["stock"] < item["qty"]:
            return False, "out of stock " + sku, total
        total += inventory[sku]["price"] * item["qty"]
    return True, None, total


def _apply_discount(
    order: Order, total: float, discounts: Discounts
) -> Tuple[bool, Optional[str], float]:
    """Apply an optional coupon to a total, rejecting unknown coupons."""
    coupon = order.get("coupon")
    if not coupon:
        return True, None, total
    if coupon not in discounts:
        return False, "bad coupon", total
    return True, None, total - total * discounts[coupon] / 100.0


def _commit_stock(order: Order, inventory: Inventory) -> None:
    """Deduct an order's item quantities from inventory."""
    for item in order["items"]:
        sku = item["sku"]
        inventory[sku]["stock"] -= item["qty"]


def _fulfil_order(
    order: Order,
    total: float,
    inventory: Inventory,
    results: Dict[str, Any],
) -> None:
    """Deduct stock and record a fulfilled order."""
    _commit_stock(order, inventory)
    total = round(total, 2)
    results["fulfilled"].append(
        {"id": order["id"], "customer": order["customer"], "total": total}
    )
    results["revenue"] = round(results["revenue"] + total, 2)


def _reject_order(
    order: Order, reason: Optional[str], results: Dict[str, Any]
) -> None:
    """Record a rejected order with its reason."""
    results["rejected"].append({"id": order["id"], "reason": reason})


def process_orders(
    orders: List[Order], inventory: Inventory, discounts: Discounts
) -> Dict[str, Any]:
    """Process orders in sequence against inventory.

    orders:    list of dicts {"id": int, "customer": str, "items": [{"sku": str, "qty": int}], "coupon": str (optional)}
    inventory: dict sku -> {"price": float, "stock": int}; it is NOT mutated
    discounts: dict coupon code -> percent off (int)
    returns:   {"fulfilled": [{"id", "customer", "total"}], "rejected": [{"id", "reason"}],
                "revenue": float, "inventory": updated copy of inventory}
    """
    results: Dict[str, Any] = {"fulfilled": [], "rejected": [], "revenue": 0.0}
    inv = _copy_inventory(inventory)

    for order in orders:
        ok, reason, total = _price_items(order, inv)
        if ok:
            ok, reason, total = _apply_discount(order, total, discounts)
        if ok:
            _fulfil_order(order, total, inv, results)
        else:
            _reject_order(order, reason, results)

    results["inventory"] = inv
    return results
