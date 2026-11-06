"""Order processing (legacy module)."""

from typing import Any


def _copy_inventory(
    inventory: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Return a shallow per-sku copy of the inventory."""
    return {
        sku: {"price": data["price"], "stock": data["stock"]}
        for sku, data in inventory.items()
    }


def _item_error(
    item: dict[str, Any], inv: dict[str, dict[str, Any]]
) -> str | None:
    """Return a rejection reason for one item, or None if it is orderable."""
    sku = item["sku"]
    if sku not in inv:
        return "unknown sku " + sku
    if item["qty"] <= 0:
        return "bad qty"
    if inv[sku]["stock"] < item["qty"]:
        return "out of stock " + sku
    return None


def _order_total(
    order: dict[str, Any], inv: dict[str, dict[str, Any]]
) -> tuple[float, str | None]:
    """Return the undiscounted total and any item-level rejection reason."""
    total = 0.0
    for item in order["items"]:
        reason = _item_error(item, inv)
        if reason is not None:
            return 0.0, reason
        total += inv[item["sku"]]["price"] * item["qty"]
    return total, None


def _apply_coupon(
    order: dict[str, Any],
    total: float,
    discounts: dict[str, int],
) -> tuple[float, str | None]:
    """Apply a coupon to the total, returning any rejection reason."""
    coupon = order.get("coupon")
    if not coupon:
        return total, None
    if coupon not in discounts:
        return total, "bad coupon"
    return total - total * discounts[coupon] / 100.0, None


def _evaluate(
    order: dict[str, Any],
    inv: dict[str, dict[str, Any]],
    discounts: dict[str, int],
) -> tuple[float, str | None]:
    """Return the discounted total and any rejection reason."""
    total, reason = _order_total(order, inv)
    if reason is not None:
        return total, reason
    return _apply_coupon(order, total, discounts)


def _reserve(
    order: dict[str, Any], inv: dict[str, dict[str, Any]]
) -> None:
    """Decrement stock for every item in a fulfilled order."""
    for item in order["items"]:
        inv[item["sku"]]["stock"] -= item["qty"]


def process_orders(
    orders: list[dict[str, Any]],
    inventory: dict[str, dict[str, Any]],
    discounts: dict[str, int],
) -> dict[str, Any]:
    """Process orders in sequence against a copy of the inventory."""
    results: dict[str, Any] = {"fulfilled": [], "rejected": [], "revenue": 0.0}
    inv = _copy_inventory(inventory)
    for order in orders:
        total, reason = _evaluate(order, inv, discounts)
        if reason is not None:
            results["rejected"].append({"id": order["id"], "reason": reason})
            continue
        _reserve(order, inv)
        total = round(total, 2)
        entry = {"id": order["id"], "customer": order["customer"], "total": total}
        results["fulfilled"].append(entry)
        results["revenue"] = round(results["revenue"] + total, 2)
    results["inventory"] = inv
    return results
