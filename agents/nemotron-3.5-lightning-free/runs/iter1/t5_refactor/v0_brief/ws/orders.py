"""Order processing (legacy module)."""


from typing import Any


def _copy_inventory(inventory: dict[str, dict[str, float]]) -> dict[str, dict[str, float]]:
    """Create a copy of inventory without mutating the original."""
    return {sku: {"price": data["price"], "stock": data["stock"]} for sku, data in inventory.items()}


def _validate_items(
    items: list[dict[str, Any]], inv: dict[str, dict[str, float]]
) -> tuple[bool, str | None, float]:
    """Validate order items against inventory.

    Returns (ok, reason, total).
    If ok is False, reason is set; otherwise reason is None.
    Total is calculated only if all items are valid.
    """
    total = 0.0
    for item in items:
        sku = item["sku"]
        qty = item["qty"]
        if sku not in inv:
            return False, f"unknown sku {sku}", 0.0
        if qty <= 0:
            return False, "bad qty", 0.0
        if inv[sku]["stock"] < qty:
            return False, f"out of stock {sku}", 0.0
        total += inv[sku]["price"] * qty
    return True, None, total


def _try_apply_coupon(
    total: float, coupon: str, discounts: dict[str, int]
) -> tuple[float, bool | None]:
    """Attempt to apply a coupon discount.

    Returns (new_total, coupon_was_valid).
    - If coupon is empty/None: (total, None) - no change, no rejection.
    - If coupon is valid: (discounted_total, True).
    - If coupon is invalid (present but not in discounts): (total, False).
    """
    if not coupon:
        return total, None
    if coupon in discounts:
        return total - total * discounts[coupon] / 100.0, True
    return total, False


def _deduct_inventory(items: list[dict[str, Any]], inv: dict[str, dict[str, float]]) -> None:
    """Deduct item quantities from inventory."""
    for item in items:
        inv[item["sku"]]["stock"] -= item["qty"]


def process_orders(
    orders: list[dict[str, Any]],
    inventory: dict[str, dict[str, float]],
    discounts: dict[str, int],
) -> dict[str, list[dict[str, Any]] | float]:
    """Process orders in sequence against inventory.

    Returns dict with 'fulfilled', 'rejected', 'revenue', and 'inventory' keys.
    """
    results = {"fulfilled": [], "rejected": [], "revenue": 0.0}
    inv = _copy_inventory(inventory)

    for order in orders:
        ok, reason, total = _validate_items(order["items"], inv)

        if ok:
            total, coupon_ok = _try_apply_coupon(total, order.get("coupon", ""), discounts)
            if coupon_ok is False:
                ok = False
                reason = "bad coupon"

        if ok:
            _deduct_inventory(order["items"], inv)
            total = round(total, 2)
            results["fulfilled"].append({"id": order["id"], "customer": order["customer"], "total": total})
            results["revenue"] = round(results["revenue"] + total, 2)
        else:
            results["rejected"].append({"id": order["id"], "reason": reason})

    results["inventory"] = inv
    return results