"""Order processing (legacy module)."""
from typing import Any


def _copy_inventory(inventory: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    inv: dict[str, dict[str, Any]] = {}
    for k in inventory:
        inv[k] = {"price": inventory[k]["price"], "stock": inventory[k]["stock"]}
    return inv


def _item_reason(item: dict[str, Any], inv: dict[str, dict[str, Any]]) -> str | None:
    if item["sku"] not in inv:
        return "unknown sku " + item["sku"]
    if item["qty"] <= 0:
        return "bad qty"
    if inv[item["sku"]]["stock"] < item["qty"]:
        return "out of stock " + item["sku"]
    return None


def _validate_items(order: dict[str, Any], inv: dict[str, dict[str, Any]]) -> tuple[bool, str | None, float]:
    total = 0.0
    for it in order["items"]:
        reason = _item_reason(it, inv)
        if reason is not None:
            return False, reason, total
        total = total + inv[it["sku"]]["price"] * it["qty"]
    return True, None, total


def _apply_coupon(order: dict[str, Any], discounts: dict[str, int], total: float) -> tuple[bool, str | None, float]:
    if "coupon" in order and order["coupon"]:
        if order["coupon"] in discounts:
            return True, None, total - total * discounts[order["coupon"]] / 100.0
        return False, "bad coupon", total
    return True, None, total


def _deduct(order: dict[str, Any], inv: dict[str, dict[str, Any]]) -> None:
    for it in order["items"]:
        inv[it["sku"]]["stock"] = inv[it["sku"]]["stock"] - it["qty"]


def _record_fulfilled(results: dict[str, Any], order: dict[str, Any], total: float) -> None:
    rounded = round(total, 2)
    results["fulfilled"].append({"id": order["id"], "customer": order["customer"], "total": rounded})
    results["revenue"] = round(results["revenue"] + rounded, 2)


def _process_one(order: dict[str, Any], inv: dict[str, dict[str, Any]], discounts: dict[str, int], results: dict[str, Any]) -> None:
    ok, reason, total = _validate_items(order, inv)
    if ok:
        ok, reason, total = _apply_coupon(order, discounts, total)
    if ok:
        _deduct(order, inv)
        _record_fulfilled(results, order, total)
    else:
        results["rejected"].append({"id": order["id"], "reason": reason})


def process_orders(orders: list[dict[str, Any]], inventory: dict[str, dict[str, Any]], discounts: dict[str, int]) -> dict[str, Any]:
    """Process orders in sequence against inventory."""
    results: dict[str, Any] = {"fulfilled": [], "rejected": [], "revenue": 0.0}
    inv = _copy_inventory(inventory)
    for o in orders:
        _process_one(o, inv, discounts, results)
    results["inventory"] = inv
    return results
