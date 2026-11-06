"""Order processing (legacy module)."""

from typing import Any


def copy_inventory(inventory: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {sku: {"price": inventory[sku]["price"], "stock": inventory[sku]["stock"]} for sku in inventory}


def compute_order_total(items: list[dict[str, Any]], inv: dict[str, dict[str, Any]]) -> tuple[bool, str | None, float]:
    total = 0.0
    for item in items:
        sku = item["sku"]
        if sku not in inv:
            return False, "unknown sku " + sku, 0.0
        if item["qty"] <= 0:
            return False, "bad qty", 0.0
        if inv[sku]["stock"] < item["qty"]:
            return False, "out of stock " + sku, 0.0
        total = total + inv[sku]["price"] * item["qty"]
    return True, None, total


def apply_coupon(total: float, order: dict[str, Any], discounts: dict[str, int]) -> tuple[float, bool, str | None]:
    if "coupon" in order and order["coupon"]:
        if order["coupon"] in discounts:
            total = total - total * discounts[order["coupon"]] / 100.0
            return total, True, None
        return total, False, "bad coupon"
    return total, True, None


def process_orders(orders: list[dict[str, Any]], inventory: dict[str, dict[str, Any]], discounts: dict[str, int]) -> dict[str, Any]:
    """Process orders in sequence against inventory.

    orders:    list of dicts {"id": int, "customer": str, "items": [{"sku": str, "qty": int}], "coupon": str (optional)}
    inventory: dict sku -> {"price": float, "stock": int}; it is NOT mutated
    discounts: dict coupon code -> percent off (int)
    returns:   {"fulfilled": [{"id", "customer", "total"}], "rejected": [{"id", "reason"}],
                "revenue": float, "inventory": updated copy of inventory}
    """
    results: dict[str, Any] = {"fulfilled": [], "rejected": [], "revenue": 0.0}
    inv = copy_inventory(inventory)
    for order in orders:
        ok, reason, total = compute_order_total(order["items"], inv)
        if ok:
            total, ok, reason = apply_coupon(total, order, discounts)
        if ok:
            for item in order["items"]:
                inv[item["sku"]]["stock"] = inv[item["sku"]]["stock"] - item["qty"]
            total = round(total, 2)
            results["fulfilled"].append({"id": order["id"], "customer": order["customer"], "total": total})
            results["revenue"] = round(results["revenue"] + total, 2)
        else:
            results["rejected"].append({"id": order["id"], "reason": reason})
    results["inventory"] = inv
    return results