"""Order processing (refactored module)."""

from typing import Dict, List, Tuple

Item = Dict[str, object]
Order = Dict[str, object]
Inventory = Dict[str, Dict[str, object]]
Discounts = Dict[str, int]
Results = Dict[str, object]


def _copy_inventory(inventory: Inventory) -> Inventory:
    """Return a copy of inventory that processing may mutate."""
    return {sku: {"price": entry["price"], "stock": entry["stock"]} for sku, entry in inventory.items()}


def _validate_items(items: List[Item], inventory: Inventory) -> Tuple[bool, str, float]:
    """Check every item against inventory; return (ok, reason, subtotal)."""
    total = 0.0
    for item in items:
        sku = item["sku"]
        qty = item["qty"]
        if sku not in inventory:
            return False, "unknown sku " + sku, 0.0
        if qty <= 0:
            return False, "bad qty", 0.0
        if inventory[sku]["stock"] < qty:
            return False, "out of stock " + sku, 0.0
        total = total + inventory[sku]["price"] * qty
    return True, "", total


def _apply_discount(total: float, order: Order, discounts: Discounts) -> Tuple[bool, str, float]:
    """Apply the order's coupon discount, if any; return (ok, reason, total)."""
    coupon = order.get("coupon")
    if coupon:
        if coupon in discounts:
            total = total - total * discounts[coupon] / 100.0
            return True, "", total
        return False, "bad coupon", total
    return True, "", total


def _deduct_stock(items: List[Item], inventory: Inventory) -> None:
    """Reduce stock for each item (caller must have validated availability)."""
    for item in items:
        sku = item["sku"]
        inventory[sku]["stock"] = inventory[sku]["stock"] - item["qty"]


def _fulfill(order: Order, total: float, results: Results, inventory: Inventory) -> None:
    """Record a fulfilled order, deduct stock, and update revenue."""
    total = round(total, 2)
    results["fulfilled"].append({"id": order["id"], "customer": order["customer"], "total": total})
    results["revenue"] = round(results["revenue"] + total, 2)
    _deduct_stock(order["items"], inventory)


def _reject(order: Order, reason: str, results: Results) -> None:
    """Record a rejected order with the given reason."""
    results["rejected"].append({"id": order["id"], "reason": reason})


def process_orders(orders: List[Order], inventory: Inventory, discounts: Discounts) -> Results:
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
        ok, reason, total = _validate_items(order["items"], inv)
        if ok:
            ok, reason, total = _apply_discount(total, order, discounts)
        if ok:
            _fulfill(order, total, results, inv)
        else:
            _reject(order, reason, results)
    results["inventory"] = inv
    return results
