"""Order processing (legacy module)."""

from __future__ import annotations

from typing import Dict, List, NotRequired, Optional, TypedDict, Tuple


class OrderItem(TypedDict):
    sku: str
    qty: int


class Order(TypedDict):
    id: int
    customer: str
    items: List[OrderItem]
    coupon: NotRequired[str]


class InventoryEntry(TypedDict):
    price: float
    stock: int


Inventory = Dict[str, InventoryEntry]
Discounts = Dict[str, int]


class Fulfilled(TypedDict):
    id: int
    customer: str
    total: float


class Rejected(TypedDict):
    id: int
    reason: str


class ProcessResult(TypedDict):
    fulfilled: List[Fulfilled]
    rejected: List[Rejected]
    revenue: float
    inventory: Inventory


def copy_inventory(inventory: Inventory) -> Inventory:
    return {
        sku: {"price": entry["price"], "stock": entry["stock"]}
        for sku, entry in inventory.items()
    }


def validate_items(
    items: List[OrderItem], inventory: Inventory
) -> Tuple[bool, Optional[str], float]:
    total = 0.0
    for item in items:
        sku = item["sku"]
        qty = item["qty"]
        if sku not in inventory:
            return False, f"unknown sku {sku}", total
        if qty <= 0:
            return False, "bad qty", total
        if inventory[sku]["stock"] < qty:
            return False, f"out of stock {sku}", total
        total += inventory[sku]["price"] * qty
    return True, None, total


def apply_coupon(
    total: float, coupon: Optional[str], discounts: Discounts
) -> Tuple[bool, Optional[str], float]:
    if not coupon:
        return True, None, total
    if coupon not in discounts:
        return False, "bad coupon", total
    discounted = total - total * discounts[coupon] / 100.0
    return True, None, discounted


def deduct_stock(items: List[OrderItem], inventory: Inventory) -> None:
    for item in items:
        inventory[item["sku"]]["stock"] -= item["qty"]


def process_orders(
    orders: List[Order], inventory: Inventory, discounts: Discounts
) -> ProcessResult:
    fulfilled: List[Fulfilled] = []
    rejected: List[Rejected] = []
    revenue = 0.0
    inv = copy_inventory(inventory)

    for order in orders:
        ok, reason, total = validate_items(order["items"], inv)
        if ok:
            ok, reason, total = apply_coupon(total, order.get("coupon"), discounts)
        if not ok:
            rejected.append({"id": order["id"], "reason": reason or ""})
            continue
        deduct_stock(order["items"], inv)
        total = round(total, 2)
        fulfilled.append({"id": order["id"], "customer": order["customer"], "total": total})
        revenue = round(revenue + total, 2)

    return {
        "fulfilled": fulfilled,
        "rejected": rejected,
        "revenue": revenue,
        "inventory": inv,
    }
