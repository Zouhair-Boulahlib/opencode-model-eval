"""Order processing (legacy module)."""

from typing import Any, Dict, List, Tuple

Inventory = Dict[str, Dict[str, Any]]
Order = Dict[str, Any]
OrderItem = Dict[str, Any]
Result = Dict[str, Any]


def clone_inventory(inventory: Inventory) -> Inventory:
    inv: Inventory = {}
    for sku in inventory:
        inv[sku] = {"price": inventory[sku]["price"], "stock": inventory[sku]["stock"]}
    return inv


def compute_line_total(items: List[OrderItem], inv: Inventory) -> Tuple[bool, str, float]:
    total = 0.0
    for it in items:
        sku = it["sku"]
        if sku not in inv:
            return False, "unknown sku " + sku, 0.0
        qty = it["qty"]
        if qty <= 0:
            return False, "bad qty", 0.0
        if inv[sku]["stock"] < qty:
            return False, "out of stock " + sku, 0.0
        total = total + inv[sku]["price"] * qty
    return True, "", total


def apply_discount(order: Order, total: float, discounts: Dict[str, int]) -> Tuple[bool, str, float]:
    coupon = order.get("coupon")
    if coupon:
        if coupon in discounts:
            total = total - total * discounts[coupon] / 100.0
            return True, "", total
        return False, "bad coupon", total
    return True, "", total


def deduct_stock(items: List[OrderItem], inv: Inventory) -> None:
    for it in items:
        inv[it["sku"]]["stock"] = inv[it["sku"]]["stock"] - it["qty"]


def process_orders(orders: List[Order], inventory: Inventory, discounts: Dict[str, int]) -> Result:
    results: Result = {"fulfilled": [], "rejected": [], "revenue": 0.0}
    inv = clone_inventory(inventory)
    for o in orders:
        ok, reason, total = compute_line_total(o["items"], inv)
        if ok:
            ok, reason, total = apply_discount(o, total, discounts)
        if ok:
            deduct_stock(o["items"], inv)
            total = round(total, 2)
            results["fulfilled"].append({"id": o["id"], "customer": o["customer"], "total": total})
            results["revenue"] = round(results["revenue"] + total, 2)
        else:
            results["rejected"].append({"id": o["id"], "reason": reason})
    results["inventory"] = inv
    return results
