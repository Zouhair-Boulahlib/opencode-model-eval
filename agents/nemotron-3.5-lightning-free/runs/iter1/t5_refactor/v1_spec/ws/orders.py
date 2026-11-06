"""Order processing (legacy module)."""

from typing import Any, Dict, List, Tuple


def process_orders(orders: List[Dict[str, Any]], inventory: Dict[str, Dict[str, float]], discounts: Dict[str, int]) -> Dict[str, Any]:
    """Process orders in sequence against inventory."""
    inv = copy_inventory(inventory)
    results: Dict[str, Any] = {"fulfilled": [], "rejected": [], "revenue": 0.0}
    for o in orders:
        ok, reason, total = process_order(o, inv, discounts)
        if ok:
            results["fulfilled"].append({"id": o["id"], "customer": o["customer"], "total": total})
            results["revenue"] = round(results["revenue"] + total, 2)
        else:
            results["rejected"].append({"id": o["id"], "reason": reason})
    results["inventory"] = inv
    return results


def copy_inventory(inventory: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, float]]:
    inv: Dict[str, Dict[str, float]] = {}
    for k in inventory:
        inv[k] = {"price": inventory[k]["price"], "stock": inventory[k]["stock"]}
    return inv


def validate_order_items(order: Dict[str, Any], inventory: Dict[str, Dict[str, float]]) -> Tuple[bool, str]:
    for it in order["items"]:
        if it["sku"] not in inventory:
            return False, "unknown sku " + it["sku"]
        if it["qty"] <= 0:
            return False, "bad qty"
        if inventory[it["sku"]]["stock"] < it["qty"]:
            return False, "out of stock " + it["sku"]
    return True, None


def process_order(order: Dict[str, Any], inventory: Dict[str, Dict[str, float]], discounts: Dict[str, int]) -> Tuple[bool, str, float]:
    ok, reason = validate_order_items(order, inventory)
    total: float = 0.0

    if ok:
        total = calculate_total(order, inventory)
        coupon_ok, total = apply_coupon(order, total, discounts)
        if not coupon_ok:
            reason = "bad coupon"
            ok = False

    if ok:
        for it in order["items"]:
            inventory[it["sku"]]["stock"] -= it["qty"]
        total = round(total, 2)

    return ok, reason, total


def calculate_total(order: Dict[str, Any], inventory: Dict[str, Dict[str, float]]) -> float:
    total: float = 0.0
    for it in order["items"]:
        total += inventory[it["sku"]]["price"] * it["qty"]
    return total


def apply_coupon(order: Dict[str, Any], total: float, discounts: Dict[str, int]) -> Tuple[bool, float]:
    if "coupon" in order and order["coupon"]:
        if order["coupon"] in discounts:
            total = total - total * discounts[order["coupon"]] / 100.0
        else:
            return False, total
    return True, total