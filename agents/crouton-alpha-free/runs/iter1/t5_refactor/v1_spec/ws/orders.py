"""Order processing (legacy module)."""

from typing import Any


def _copy_inventory(inventory: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {sku: {"price": entry["price"], "stock": entry["stock"]} for sku, entry in inventory.items()}


def _item_error(item: dict[str, Any], inv: dict[str, dict[str, Any]]) -> str | None:
    if item["sku"] not in inv:
        return "unknown sku " + item["sku"]
    if item["qty"] <= 0:
        return "bad qty"
    if inv[item["sku"]]["stock"] < item["qty"]:
        return "out of stock " + item["sku"]
    return None


def _validate_items(items: list[dict[str, Any]], inv: dict[str, dict[str, Any]]) -> tuple[bool, str | None, float]:
    total = 0.0
    for item in items:
        error = _item_error(item, inv)
        if error is not None:
            return False, error, total
        total = total + inv[item["sku"]]["price"] * item["qty"]
    return True, None, total


def _apply_coupon(order: dict[str, Any], discounts: dict[str, Any], total: float) -> tuple[bool, str | None, float]:
    coupon = order.get("coupon")
    if not coupon:
        return True, None, total
    if coupon not in discounts:
        return False, "bad coupon", total
    discounted = total - total * discounts[coupon] / 100.0
    return True, None, discounted


def _deduct_stock(items: list[dict[str, Any]], inv: dict[str, dict[str, Any]]) -> None:
    for item in items:
        inv[item["sku"]]["stock"] = inv[item["sku"]]["stock"] - item["qty"]


def _record_fulfilled(order: dict[str, Any], inv: dict[str, dict[str, Any]], total: float, results: dict[str, Any]) -> None:
    _deduct_stock(order["items"], inv)
    rounded = round(total, 2)
    results["fulfilled"].append({"id": order["id"], "customer": order["customer"], "total": rounded})
    results["revenue"] = round(results["revenue"] + rounded, 2)


def _process_order(order: dict[str, Any], inv: dict[str, dict[str, Any]], discounts: dict[str, Any], results: dict[str, Any]) -> None:
    ok, reason, total = _validate_items(order["items"], inv)
    if ok:
        ok, reason, total = _apply_coupon(order, discounts, total)
    if ok:
        _record_fulfilled(order, inv, total, results)
    else:
        results["rejected"].append({"id": order["id"], "reason": reason})


def process_orders(orders: list[dict[str, Any]], inventory: dict[str, dict[str, Any]], discounts: dict[str, Any]) -> dict[str, Any]:
    inv = _copy_inventory(inventory)
    results: dict[str, Any] = {"fulfilled": [], "rejected": [], "revenue": 0.0}
    for order in orders:
        _process_order(order, inv, discounts, results)
    results["inventory"] = inv
    return results
