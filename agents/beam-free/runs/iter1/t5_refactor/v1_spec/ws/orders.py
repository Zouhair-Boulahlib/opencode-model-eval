"""Order processing (legacy module)."""

from typing import Any


def _copy_inventory(inventory: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    inv: dict[str, dict[str, Any]] = {}
    for k in inventory:
        inv[k] = {"price": inventory[k]["price"], "stock": inventory[k]["stock"]}
    return inv


def _validate_items(items: list[dict[str, Any]], inv: dict[str, dict[str, Any]]) -> tuple[bool, str | None, float]:
    total = 0.0
    for it in items:
        sku = it["sku"]
        if sku not in inv:
            return False, "unknown sku " + sku, 0.0
        if it["qty"] <= 0:
            return False, "bad qty", 0.0
        if inv[sku]["stock"] < it["qty"]:
            return False, "out of stock " + sku, 0.0
        total = total + inv[sku]["price"] * it["qty"]
    return True, None, total


def _apply_coupon(total: float, order: dict[str, Any], discounts: dict[str, int]) -> tuple[bool, str | None, float]:
    coupon = order.get("coupon")
    if coupon:
        if coupon in discounts:
            return True, None, total - total * discounts[coupon] / 100.0
        return False, "bad coupon", total
    return True, None, total


def process_orders(orders: list[dict[str, Any]], inventory: dict[str, dict[str, Any]], discounts: dict[str, int]) -> dict[str, Any]:
    results = {"fulfilled": [], "rejected": [], "revenue": 0.0}
    inv = _copy_inventory(inventory)
    for o in orders:
        ok, reason, total = _validate_items(o["items"], inv)
        if ok:
            ok, reason, total = _apply_coupon(total, o, discounts)
        if ok:
            for it in o["items"]:
                inv[it["sku"]]["stock"] = inv[it["sku"]]["stock"] - it["qty"]
            total = round(total, 2)
            results["fulfilled"].append({"id": o["id"], "customer": o["customer"], "total": total})
            results["revenue"] = round(results["revenue"] + total, 2)
        else:
            results["rejected"].append({"id": o["id"], "reason": reason})
    results["inventory"] = inv
    return results