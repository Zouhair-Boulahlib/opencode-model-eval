"""Order processing (legacy module)."""


from typing import Any


def _copy_inventory(inventory: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    inv: dict[str, dict[str, Any]] = {}
    for sku, data in inventory.items():
        inv[sku] = {"price": data["price"], "stock": data["stock"]}
    return inv


def _compute_total(order: dict[str, Any], inv: dict[str, dict[str, Any]]) -> tuple[bool, str | None, float]:
    total = 0.0
    for item in order["items"]:
        sku = item["sku"]
        qty = item["qty"]
        if sku not in inv:
            return False, "unknown sku " + sku, total
        if qty <= 0:
            return False, "bad qty", total
        if inv[sku]["stock"] < qty:
            return False, "out of stock " + sku, total
        total += inv[sku]["price"] * qty
    return True, None, total


def _apply_coupon(total: float, order: dict[str, Any], discounts: dict[str, Any]) -> tuple[bool, str | None, float]:
    coupon = order.get("coupon")
    if not coupon:
        return True, None, total
    if coupon not in discounts:
        return False, "bad coupon", total
    return True, None, total - total * discounts[coupon] / 100.0


def _deduct_stock(inv: dict[str, dict[str, Any]], order: dict[str, Any]) -> None:
    for item in order["items"]:
        inv[item["sku"]]["stock"] -= item["qty"]


def _process_one(order: dict[str, Any], inv: dict[str, dict[str, Any]], discounts: dict[str, Any], results: dict[str, Any]) -> None:
    ok, reason, total = _compute_total(order, inv)
    if ok:
        ok, reason, total = _apply_coupon(total, order, discounts)
    if ok:
        _deduct_stock(inv, order)
        total = round(total, 2)
        results["fulfilled"].append({"id": order["id"], "customer": order["customer"], "total": total})
        results["revenue"] = round(results["revenue"] + total, 2)
    else:
        results["rejected"].append({"id": order["id"], "reason": reason})


def process_orders(orders: list[dict[str, Any]], inventory: dict[str, dict[str, Any]], discounts: dict[str, Any]) -> dict[str, Any]:
    results = {"fulfilled": [], "rejected": [], "revenue": 0.0}
    inv = _copy_inventory(inventory)
    for order in orders:
        _process_one(order, inv, discounts, results)
    results["inventory"] = inv
    return results