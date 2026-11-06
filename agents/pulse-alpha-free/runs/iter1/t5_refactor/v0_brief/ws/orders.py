"""Order processing (legacy module)."""

from typing import Any

Order = dict[str, Any]
Inventory = dict[str, dict[str, Any]]
Discounts = dict[str, int]
Result = dict[str, Any]


def _copy_inventory(inventory: Inventory) -> Inventory:
    return {k: {"price": v["price"], "stock": v["stock"]} for k, v in inventory.items()}


def _validate_items(order: Order, inv: Inventory) -> str | None:
    for it in order["items"]:
        if it["sku"] not in inv:
            return "unknown sku " + it["sku"]
        if it["qty"] <= 0:
            return "bad qty"
        if inv[it["sku"]]["stock"] < it["qty"]:
            return "out of stock " + it["sku"]
    return None


def _items_total(order: Order, inv: Inventory) -> float:
    total = 0.0
    for it in order["items"]:
        total = total + inv[it["sku"]]["price"] * it["qty"]
    return total


def _apply_coupon(total: float, order: Order, discounts: Discounts) -> tuple[float, str | None]:
    coupon = order.get("coupon")
    if not coupon:
        return total, None
    if coupon in discounts:
        return total - total * discounts[coupon] / 100.0, None
    return total, "bad coupon"


def _deduct_stock(order: Order, inv: Inventory) -> None:
    for it in order["items"]:
        inv[it["sku"]]["stock"] = inv[it["sku"]]["stock"] - it["qty"]


def _process_one(order: Order, inv: Inventory, discounts: Discounts) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    reason = _validate_items(order, inv)
    total = 0.0
    if reason is None:
        total = _items_total(order, inv)
        total, reason = _apply_coupon(total, order, discounts)
    if reason is not None:
        return None, {"id": order["id"], "reason": reason}
    _deduct_stock(order, inv)
    total = round(total, 2)
    return {"id": order["id"], "customer": order["customer"], "total": total}, None


def process_orders(orders: list[Order], inventory: Inventory, discounts: Discounts) -> Result:
    """Process orders in sequence against inventory.

    orders:    list of dicts {"id": int, "customer": str, "items": [{"sku": str, "qty": int}], "coupon": str (optional)}
    inventory: dict sku -> {"price": float, "stock": int}; it is NOT mutated
    discounts: dict coupon code -> percent off (int)
    returns:   {"fulfilled": [{"id", "customer", "total"}], "rejected": [{"id", "reason"}],
                "revenue": float, "inventory": updated copy of inventory}
    """
    results: Result = {"fulfilled": [], "rejected": [], "revenue": 0.0}
    inv = _copy_inventory(inventory)
    for o in orders:
        fulfilled, rejected = _process_one(o, inv, discounts)
        if fulfilled is not None:
            results["fulfilled"].append(fulfilled)
            results["revenue"] = round(results["revenue"] + fulfilled["total"], 2)
        else:
            results["rejected"].append(rejected)
    results["inventory"] = inv
    return results
