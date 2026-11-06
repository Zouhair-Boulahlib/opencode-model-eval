"""Order processing (legacy module)."""

from typing import Dict, List, Optional, TypedDict


class OrderItem(TypedDict):
    sku: str
    qty: int


class Order(TypedDict):
    id: int
    customer: str
    items: List[OrderItem]
    coupon: Optional[str]


class InventoryItem(TypedDict):
    price: float
    stock: int


class FulfilledOrder(TypedDict):
    id: int
    customer: str
    total: float


class RejectedOrder(TypedDict):
    id: int
    reason: str


class ProcessResult(TypedDict):
    fulfilled: List[FulfilledOrder]
    rejected: List[RejectedOrder]
    revenue: float
    inventory: Dict[str, InventoryItem]


def _copy_inventory(inventory: Dict[str, InventoryItem]) -> Dict[str, InventoryItem]:
    inv: Dict[str, InventoryItem] = {}
    for sku, item in inventory.items():
        inv[sku] = {"price": item["price"], "stock": item["stock"]}
    return inv


def _check_items(order: Order, inv: Dict[str, InventoryItem]) -> tuple[bool, Optional[str], float]:
    ok = True
    reason: Optional[str] = None
    total = 0.0
    for item in order["items"]:
        if item["sku"] not in inv:
            ok = False
            reason = f"unknown sku {item['sku']}"
            break
        if item["qty"] <= 0:
            ok = False
            reason = "bad qty"
            break
        if inv[item["sku"]]["stock"] < item["qty"]:
            ok = False
            reason = f"out of stock {item['sku']}"
            break
        total = total + inv[item["sku"]]["price"] * item["qty"]
    return ok, reason, total


def _apply_coupon(coupon: Optional[str], total: float, discounts: Dict[str, int]) -> tuple[bool, Optional[str], float]:
    ok = True
    reason: Optional[str] = None
    if coupon:
        if coupon in discounts:
            total = total - total * discounts[coupon] / 100.0
        else:
            ok = False
            reason = "bad coupon"
    return ok, reason, total


def process_orders(
    orders: List[Order],
    inventory: Dict[str, InventoryItem],
    discounts: Dict[str, int],
) -> ProcessResult:
    """Process orders in sequence against inventory.

    orders:    list of dicts {"id": int, "customer": str, "items": [{"sku": str, "qty": int}], "coupon": str (optional)}
    inventory: dict sku -> {"price": float, "stock": int}; it is NOT mutated
    discounts: dict coupon code -> percent off (int)
    returns:   {"fulfilled": [{"id", "customer", "total"}], "rejected": [{"id", "reason"}],
                "revenue": float, "inventory": updated copy of inventory}
    """
    inv = _copy_inventory(inventory)
    results: ProcessResult = {"fulfilled": [], "rejected": [], "revenue": 0.0, "inventory": inv}
    for order in orders:
        ok, reason, total = _check_items(order, inv)
        if ok:
            ok, reason, total = _apply_coupon(order.get("coupon"), total, discounts)
        if ok:
            for item in order["items"]:
                inv[item["sku"]]["stock"] = inv[item["sku"]]["stock"] - item["qty"]
            total = round(total, 2)
            results["fulfilled"].append({"id": order["id"], "customer": order["customer"], "total": total})
            results["revenue"] = round(results["revenue"] + total, 2)
        else:
            results["rejected"].append({"id": order["id"], "reason": reason})
    return results
