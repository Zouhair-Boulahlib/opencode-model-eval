"""Order processing (legacy module)."""

from typing import Any

Order = dict[str, Any]
Inventory = dict[str, dict[str, Any]]
Discounts = dict[str, int]
Item = dict[str, Any]
Results = dict[str, Any]


def copy_inventory(inventory: Inventory) -> Inventory:
    """Return a shallow per-entry copy of the inventory."""
    return {sku: {"price": data["price"], "stock": data["stock"]}
            for sku, data in inventory.items()}


def line_total(item: Item, inventory: Inventory) -> tuple[float, str | None]:
    """Validate one item and return its cost, or an error reason."""
    sku = item["sku"]
    if sku not in inventory:
        return 0.0, "unknown sku " + sku
    if item["qty"] <= 0:
        return 0.0, "bad qty"
    if inventory[sku]["stock"] < item["qty"]:
        return 0.0, "out of stock " + sku
    return inventory[sku]["price"] * item["qty"], None


def order_total(order: Order, inventory: Inventory,
                discounts: Discounts) -> tuple[float, str | None]:
    """Compute an order total, or return the rejection reason."""
    total = 0.0
    for item in order["items"]:
        amount, reason = line_total(item, inventory)
        if reason is not None:
            return 0.0, reason
        total = total + amount
    coupon = order.get("coupon")
    if coupon:
        if coupon not in discounts:
            return 0.0, "bad coupon"
        total = total - total * discounts[coupon] / 100.0
    return total, None


def apply_items(order: Order, inventory: Inventory) -> None:
    """Deduct every item in a fulfilled order from inventory."""
    for item in order["items"]:
        inventory[item["sku"]]["stock"] = (
            inventory[item["sku"]]["stock"] - item["qty"]
        )


def process_order(order: Order, inventory: Inventory, discounts: Discounts,
                  results: Results) -> None:
    """Process a single order, updating results and inventory in place."""
    total, reason = order_total(order, inventory, discounts)
    if reason is not None:
        results["rejected"].append({"id": order["id"], "reason": reason})
        return
    apply_items(order, inventory)
    total = round(total, 2)
    results["fulfilled"].append(
        {"id": order["id"], "customer": order["customer"], "total": total}
    )
    results["revenue"] = round(results["revenue"] + total, 2)


def process_orders(orders: list[Order], inventory: Inventory,
                   discounts: Discounts) -> Results:
    """Process orders in sequence against inventory.

    orders:    list of dicts {"id": int, "customer": str,
               "items": [{"sku": str, "qty": int}], "coupon": str (optional)}
    inventory: dict sku -> {"price": float, "stock": int}; NOT mutated
    discounts: dict coupon code -> percent off (int)
    returns:   {"fulfilled": [...], "rejected": [...],
                "revenue": float, "inventory": updated copy of inventory}
    """
    results: Results = {"fulfilled": [], "rejected": [], "revenue": 0.0}
    inv = copy_inventory(inventory)
    for order in orders:
        process_order(order, inv, discounts, results)
    results["inventory"] = inv
    return results
