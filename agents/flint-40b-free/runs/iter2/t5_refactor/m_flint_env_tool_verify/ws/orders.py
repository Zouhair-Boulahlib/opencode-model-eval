"""Order processing (legacy module)."""

from typing import Any


def process_orders(
    orders: list[dict[str, Any]],
    inventory: dict[str, dict[str, Any]],
    discounts: dict[str, float],
) -> dict[str, Any]:
    """Process orders in sequence against inventory."""
    results: dict[str, Any] = {"fulfilled": [], "rejected": [], "revenue": 0.0}
    inv = _copy_inventory(inventory)
    for order in orders:
        outcome = _evaluate_order(order, inv, discounts)
        if outcome["ok"]:
            _apply_stock(inv, order)
            total = round(outcome["total"], 2)
            results["fulfilled"].append({"id": order["id"], "customer": order["customer"], "total": total})
            results["revenue"] = round(results["revenue"] + total, 2)
        else:
            results["rejected"].append({"id": order["id"], "reason": outcome["reason"]})
    results["inventory"] = inv
    return results


def _copy_inventory(inventory: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Return a copy of the inventory."""
    return {sku: {"price": item["price"], "stock": item["stock"]} for sku, item in inventory.items()}


def _evaluate_order(order: dict[str, Any], inv: dict[str, dict[str, Any]], discounts: dict[str, float]) -> dict[str, Any]:
    """Validate an order and compute its total."""
    outcome = _check_items(order, inv)
    if outcome["ok"] and order.get("coupon"):
        if order["coupon"] in discounts:
            outcome["total"] = outcome["total"] - outcome["total"] * discounts[order["coupon"]] / 100.0
        else:
            outcome["ok"] = False
            outcome["reason"] = "bad coupon"
    return outcome


def _check_items(order: dict[str, Any], inv: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Check each order item against inventory."""
    ok = True
    reason = ""
    total = 0.0
    for item in order["items"]:
        if item["sku"] not in inv:
            ok, reason = False, "unknown sku " + item["sku"]
        elif item["qty"] <= 0:
            ok, reason = False, "bad qty"
        elif inv[item["sku"]]["stock"] < item["qty"]:
            ok, reason = False, "out of stock " + item["sku"]
        else:
            total = total + inv[item["sku"]]["price"] * item["qty"]
        if not ok:
            break
    return {"ok": ok, "reason": reason, "total": total}


def _apply_stock(inv: dict[str, dict[str, Any]], order: dict[str, Any]) -> None:
    """Reduce stock for a validated order."""
    for item in order["items"]:
        inv[item["sku"]]["stock"] = inv[item["sku"]]["stock"] - item["qty"]
