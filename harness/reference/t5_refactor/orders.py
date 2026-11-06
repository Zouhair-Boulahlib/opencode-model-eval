"""Order processing (refactored)."""
from typing import Any

Order = dict[str, Any]
Inventory = dict[str, dict[str, Any]]


def _copy_inventory(inventory: Inventory) -> Inventory:
    return {k: {"price": v["price"], "stock": v["stock"]} for k, v in inventory.items()}


def _check_item(item: dict[str, Any], inv: Inventory) -> str | None:
    sku, qty = item["sku"], item["qty"]
    if sku not in inv:
        return "unknown sku " + sku
    if qty <= 0:
        return "bad qty"
    if inv[sku]["stock"] < qty:
        return "out of stock " + sku
    return None


def _price_items(order: Order, inv: Inventory) -> tuple[float, str | None]:
    total = 0.0
    for item in order["items"]:
        reason = _check_item(item, inv)
        if reason:
            return total, reason
        total = total + inv[item["sku"]]["price"] * item["qty"]
    return total, None


def _apply_coupon(order: Order, total: float, discounts: dict[str, int]) -> tuple[float, str | None]:
    coupon = order.get("coupon")
    if not coupon:
        return total, None
    if coupon not in discounts:
        return total, "bad coupon"
    return total - total * discounts[coupon] / 100.0, None


def _deduct_stock(order: Order, inv: Inventory) -> None:
    for item in order["items"]:
        inv[item["sku"]]["stock"] = inv[item["sku"]]["stock"] - item["qty"]


def _evaluate(order: Order, inv: Inventory, discounts: dict[str, int]) -> tuple[float, str | None]:
    total, reason = _price_items(order, inv)
    if reason:
        return total, reason
    return _apply_coupon(order, total, discounts)


def process_orders(orders: list[Order], inventory: Inventory, discounts: dict[str, int]) -> dict[str, Any]:
    results: dict[str, Any] = {"fulfilled": [], "rejected": [], "revenue": 0.0}
    inv = _copy_inventory(inventory)
    for order in orders:
        total, reason = _evaluate(order, inv, discounts)
        if reason:
            results["rejected"].append({"id": order["id"], "reason": reason})
            continue
        _deduct_stock(order, inv)
        total = round(total, 2)
        results["fulfilled"].append({"id": order["id"], "customer": order["customer"], "total": total})
        results["revenue"] = round(results["revenue"] + total, 2)
    results["inventory"] = inv
    return results
