"""Order processing (legacy module)."""

from typing import Any


def _copy_inventory(inventory: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Return a copy of the inventory."""
    return {sku: {"price": item["price"], "stock": item["stock"]} for sku, item in inventory.items()}


def _validate_items(items: list[dict[str, Any]], inv: dict[str, dict[str, Any]]) -> str | None:
    """Return first error reason for items, or None if all valid."""
    for item in items:
        if item["sku"] not in inv:
            return "unknown sku " + item["sku"]
        if item["qty"] <= 0:
            return "bad qty"
        if inv[item["sku"]]["stock"] < item["qty"]:
            return "out of stock " + item["sku"]
    return None


def _order_total(items: list[dict[str, Any]], inv: dict[str, dict[str, Any]]) -> float:
    """Sum price times quantity for each item."""
    total = 0.0
    for item in items:
        total = total + inv[item["sku"]]["price"] * item["qty"]
    return total


def _check_coupon(order: dict[str, Any], discounts: dict[str, float]) -> tuple[bool, str | None]:
    """Return (ok, reason) for the order coupon."""
    if not order.get("coupon"):
        return True, None
    if order["coupon"] in discounts:
        return True, None
    return False, "bad coupon"


def _apply_order(order: dict[str, Any], inv: dict[str, dict[str, Any]]) -> None:
    """Deduct stock for a validated order."""
    for item in order["items"]:
        inv[item["sku"]]["stock"] = inv[item["sku"]]["stock"] - item["qty"]


def _evaluate(order: dict[str, Any], inv: dict[str, dict[str, Any]], discounts: dict[str, float]) -> tuple[bool, str | None, float]:
    """Validate order and compute total, applying discount if valid."""
    reason = _validate_items(order["items"], inv)
    ok = reason is None
    total = 0.0
    if ok:
        coupon_ok, coupon_reason = _check_coupon(order, discounts)
        if not coupon_ok:
            ok = False
            reason = coupon_reason
    if ok:
        total = _order_total(order["items"], inv)
        if order.get("coupon"):
            total = total - total * discounts[order["coupon"]] / 100.0
    return ok, reason, total


def process_orders(orders: list[dict[str, Any]], inventory: dict[str, dict[str, Any]], discounts: dict[str, float]) -> dict[str, Any]:
    """Process orders in sequence against inventory."""
    results: dict[str, Any] = {"fulfilled": [], "rejected": [], "revenue": 0.0}
    inv = _copy_inventory(inventory)
    for order in orders:
        ok, reason, total = _evaluate(order, inv, discounts)
        if not ok:
            results["rejected"].append({"id": order["id"], "reason": reason})
            continue
        total = round(total, 2)
        _apply_order(order, inv)
        results["fulfilled"].append({"id": order["id"], "customer": order["customer"], "total": total})
        results["revenue"] = round(results["revenue"] + total, 2)
    results["inventory"] = inv
    return results
