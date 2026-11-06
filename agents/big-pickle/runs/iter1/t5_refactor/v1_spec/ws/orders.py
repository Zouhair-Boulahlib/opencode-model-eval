"""Order processing (legacy module)."""

from typing import Any, Dict, List, Optional, Tuple


def _copy_inventory(
    inventory: Dict[str, Dict[str, Any]]
) -> Dict[str, Dict[str, Any]]:
    """Return a copy of inventory containing only price and stock."""
    inv: Dict[str, Dict[str, Any]] = {}
    for k in inventory:
        inv[k] = {"price": inventory[k]["price"], "stock": inventory[k]["stock"]}
    return inv


def _check_item(
    item: Dict[str, Any], inv: Dict[str, Dict[str, Any]]
) -> Optional[str]:
    """Return the rejection reason for an item, or None if it is valid."""
    sku = item["sku"]
    if sku not in inv:
        return "unknown sku " + sku
    if item["qty"] <= 0:
        return "bad qty"
    if inv[sku]["stock"] < item["qty"]:
        return "out of stock " + sku
    return None


def _validate_order(
    order: Dict[str, Any], inv: Dict[str, Dict[str, Any]]
) -> Optional[str]:
    """Return the rejection reason for an order, or None if it is valid."""
    for item in order["items"]:
        reason = _check_item(item, inv)
        if reason is not None:
            return reason
    return None


def _order_total(
    order: Dict[str, Any], inv: Dict[str, Dict[str, Any]]
) -> float:
    """Return the undiscounted total for an order."""
    total = 0.0
    for item in order["items"]:
        total += inv[item["sku"]]["price"] * item["qty"]
    return total


def _apply_coupon(
    order: Dict[str, Any], total: float, discounts: Dict[str, int]
) -> Tuple[bool, Optional[str], float]:
    """Apply an order's coupon; return (ok, reason, total)."""
    if "coupon" in order and order["coupon"]:
        if order["coupon"] in discounts:
            total = total - total * discounts[order["coupon"]] / 100.0
        else:
            return False, "bad coupon", total
    return True, None, total


def _commit_order(
    order: Dict[str, Any], inv: Dict[str, Dict[str, Any]]
) -> None:
    """Decrement inventory stock for the items of a fulfilled order."""
    for item in order["items"]:
        inv[item["sku"]]["stock"] = inv[item["sku"]]["stock"] - item["qty"]


def _record_fulfilled(
    order: Dict[str, Any],
    inv: Dict[str, Dict[str, Any]],
    total: float,
    results: Dict[str, Any],
) -> None:
    """Commit an order and record it as fulfilled."""
    _commit_order(order, inv)
    total = round(total, 2)
    results["fulfilled"].append(
        {"id": order["id"], "customer": order["customer"], "total": total}
    )
    results["revenue"] = round(results["revenue"] + total, 2)


def _record_rejected(
    order: Dict[str, Any], reason: Optional[str], results: Dict[str, Any]
) -> None:
    """Record an order as rejected."""
    results["rejected"].append({"id": order["id"], "reason": reason})


def _process_one(
    order: Dict[str, Any],
    inv: Dict[str, Dict[str, Any]],
    discounts: Dict[str, int],
    results: Dict[str, Any],
) -> None:
    """Validate and either fulfil or reject a single order."""
    reason = _validate_order(order, inv)
    if reason is None:
        total = _order_total(order, inv)
        ok, reason, total = _apply_coupon(order, total, discounts)
        if ok:
            _record_fulfilled(order, inv, total, results)
            return
    _record_rejected(order, reason, results)


def process_orders(
    orders: List[Dict[str, Any]],
    inventory: Dict[str, Dict[str, Any]],
    discounts: Dict[str, int],
) -> Dict[str, Any]:
    """Process orders in sequence against inventory."""
    results: Dict[str, Any] = {"fulfilled": [], "rejected": [], "revenue": 0.0}
    inv = _copy_inventory(inventory)
    for order in orders:
        _process_one(order, inv, discounts, results)
    results["inventory"] = inv
    return results
