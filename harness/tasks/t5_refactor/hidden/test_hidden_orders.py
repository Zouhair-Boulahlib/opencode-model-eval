import ast
import inspect
import os

import orders
from orders import process_orders

INVENTORY = {"A": {"price": 10.0, "stock": 5}, "B": {"price": 2.5, "stock": 2}}
DISCOUNTS = {"SAVE10": 10}
ORDERS = [
    {"id": 1, "customer": "x", "items": [{"sku": "A", "qty": 2}]},
    {"id": 2, "customer": "y", "items": [{"sku": "B", "qty": 3}]},
    {"id": 3, "customer": "z", "items": [{"sku": "A", "qty": 1}, {"sku": "B", "qty": 2}], "coupon": "SAVE10"},
    {"id": 4, "customer": "w", "items": [{"sku": "C", "qty": 1}]},
    {"id": 5, "customer": "v", "items": [{"sku": "A", "qty": 1}], "coupon": "NOPE"},
    {"id": 6, "customer": "u", "items": [{"sku": "A", "qty": 0}]},
]


def _tree():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "orders.py")
    with open(path, encoding="utf-8") as f:
        return ast.parse(f.read())


def _functions():
    return [n for n in ast.walk(_tree()) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]


# ---- behaviour ----
def test_fulfilled_and_totals():
    res = process_orders(ORDERS, INVENTORY, DISCOUNTS)
    assert res["fulfilled"] == [
        {"id": 1, "customer": "x", "total": 20.0},
        {"id": 3, "customer": "z", "total": 13.5},
    ]


def test_rejected_reasons():
    res = process_orders(ORDERS, INVENTORY, DISCOUNTS)
    assert res["rejected"] == [
        {"id": 2, "reason": "out of stock B"},
        {"id": 4, "reason": "unknown sku C"},
        {"id": 5, "reason": "bad coupon"},
        {"id": 6, "reason": "bad qty"},
    ]


def test_revenue_and_inventory_copy():
    res = process_orders(ORDERS, INVENTORY, DISCOUNTS)
    assert res["revenue"] == 33.5
    assert res["inventory"] == {"A": {"price": 10.0, "stock": 2}, "B": {"price": 2.5, "stock": 0}}
    assert INVENTORY["A"]["stock"] == 5 and INVENTORY["B"]["stock"] == 2


def test_rounding():
    res = process_orders([{"id": 1, "customer": "c", "items": [{"sku": "P", "qty": 3}]}],
                         {"P": {"price": 0.1, "stock": 10}}, {})
    assert res["fulfilled"][0]["total"] == 0.3
    assert res["revenue"] == 0.3


def test_empty_coupon_ignored():
    res = process_orders([{"id": 1, "customer": "c", "items": [{"sku": "A", "qty": 1}], "coupon": ""}], INVENTORY, DISCOUNTS)
    assert res["fulfilled"] == [{"id": 1, "customer": "c", "total": 10.0}]


def test_sequential_stock_depletion():
    res = process_orders([
        {"id": 1, "customer": "a", "items": [{"sku": "A", "qty": 3}]},
        {"id": 2, "customer": "b", "items": [{"sku": "A", "qty": 3}]},
    ], INVENTORY, DISCOUNTS)
    assert [f["id"] for f in res["fulfilled"]] == [1]
    assert res["rejected"] == [{"id": 2, "reason": "out of stock A"}]


def test_rejected_order_does_not_touch_stock():
    res = process_orders([{"id": 1, "customer": "a", "items": [{"sku": "A", "qty": 1}, {"sku": "ZZ", "qty": 1}]}], INVENTORY, DISCOUNTS)
    assert res["fulfilled"] == []
    assert res["inventory"]["A"]["stock"] == 5


def test_no_orders():
    res = process_orders([], INVENTORY, DISCOUNTS)
    assert res == {"fulfilled": [], "rejected": [], "revenue": 0.0,
                   "inventory": {"A": {"price": 10.0, "stock": 5}, "B": {"price": 2.5, "stock": 2}}}


# ---- structural constraints ----
def test_no_function_longer_than_20_lines():
    too_long = [(f.name, f.end_lineno - f.lineno + 1) for f in _functions() if f.end_lineno - f.lineno + 1 > 20]
    assert too_long == [], f"functions over 20 lines: {too_long}"


def test_all_functions_fully_type_hinted():
    missing = []
    for f in _functions():
        if f.returns is None:
            missing.append(f"{f.name}: return")
        for a in f.args.posonlyargs + f.args.args + f.args.kwonlyargs:
            if a.arg in ("self", "cls"):
                continue
            if a.annotation is None:
                missing.append(f"{f.name}: {a.arg}")
        for va in (f.args.vararg, f.args.kwarg):
            if va is not None and va.annotation is None:
                missing.append(f"{f.name}: *{va.arg}")
    assert missing == [], f"missing type hints: {missing}"


def test_process_orders_signature_kept():
    assert list(inspect.signature(orders.process_orders).parameters) == ["orders", "inventory", "discounts"]


def test_actually_split_into_helpers():
    assert len(_functions()) >= 2, "process_orders should be split into helper functions"
