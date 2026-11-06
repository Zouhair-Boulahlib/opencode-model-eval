"""Self-checks for the refactored orders.py (rules of the task)."""
import ast
import inspect
import os
import sys

import orders
from orders import process_orders

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "orders.py")


# ---------------------------------------------------------------- reference
def _reference_process_orders(orders_in, inventory, discounts):
    """Verbatim copy of the original legacy implementation."""
    results = {"fulfilled": [], "rejected": [], "revenue": 0.0}
    inv = {}
    for k in inventory:
        inv[k] = {"price": inventory[k]["price"], "stock": inventory[k]["stock"]}
    for o in orders_in:
        ok = True
        reason = None
        total = 0.0
        for it in o["items"]:
            if it["sku"] not in inv:
                ok = False
                reason = "unknown sku " + it["sku"]
                break
            if it["qty"] <= 0:
                ok = False
                reason = "bad qty"
                break
            if inv[it["sku"]]["stock"] < it["qty"]:
                ok = False
                reason = "out of stock " + it["sku"]
                break
            total = total + inv[it["sku"]]["price"] * it["qty"]
        if ok:
            if "coupon" in o and o["coupon"]:
                if o["coupon"] in discounts:
                    total = total - total * discounts[o["coupon"]] / 100.0
                else:
                    ok = False
                    reason = "bad coupon"
        if ok:
            for it in o["items"]:
                inv[it["sku"]]["stock"] = inv[it["sku"]]["stock"] - it["qty"]
            total = round(total, 2)
            results["fulfilled"].append({"id": o["id"], "customer": o["customer"], "total": total})
            results["revenue"] = round(results["revenue"] + total, 2)
        else:
            results["rejected"].append({"id": o["id"], "reason": reason})
    results["inventory"] = inv
    return results


CASES = [
    # (orders, inventory, discounts)
    ([], {}, {}),
    ([], {"A": {"price": 1.0, "stock": 1}}, {"X": 5}),
    ([{"id": 1, "customer": "c", "items": [{"sku": "P", "qty": 3}]}],
     {"P": {"price": 0.1, "stock": 10}}, {}),
    ([{"id": 1, "customer": "c", "items": [{"sku": "A", "qty": 1}], "coupon": ""}],
     {"A": {"price": 5.0, "stock": 2}}, {"D": 50}),
    ([{"id": 1, "customer": "c", "items": [{"sku": "A", "qty": 1}], "coupon": "D"}],
     {"A": {"price": 5.0, "stock": 2}}, {"D": 33}),
    ([{"id": 1, "customer": "c", "items": [{"sku": "A", "qty": 1}], "coupon": "NOPE"}],
     {"A": {"price": 5.0, "stock": 2}}, {"D": 50}),
    ([{"id": 1, "customer": "c", "items": [{"sku": "A", "qty": 1}],
      "coupon": None}],
     {"A": {"price": 5.0, "stock": 2}}, {}),
    ([{"id": 1, "customer": "c", "items": [{"sku": "A", "qty": 1}, {"sku": "B", "qty": 9}]}],
     {"A": {"price": 5.0, "stock": 2}, "B": {"price": 1.0, "stock": 1}}, {}),
    ([{"id": 1, "customer": "c", "items": [{"sku": "A", "qty": -1}]}],
     {"A": {"price": 5.0, "stock": 2}}, {}),
    ([{"id": 1, "customer": "c", "items": [{"sku": "A", "qty": 1}, {"sku": "Z", "qty": 1}]}],
     {"A": {"price": 5.0, "stock": 2}}, {}),
    ([{"id": 1, "customer": "c", "items": [{"sku": "A", "qty": 2}, {"sku": "B", "qty": 2}],
      "coupon": "D"}],
     {"A": {"price": 9.99, "stock": 5}, "B": {"price": 0.05, "stock": 5}}, {"D": 15}),
]


def test_signature_unchanged():
    sig = inspect.signature(process_orders)
    assert process_orders.__name__ == "process_orders"
    assert list(sig.parameters) == ["orders", "inventory", "discounts"]


def test_behaviour_matches_reference():
    for orders_in, inventory, discounts in CASES:
        inv_copy = {k: dict(v) for k, v in inventory.items()}
        got = process_orders(orders_in, inventory, discounts)
        want = _reference_process_orders(orders_in, inventory, discounts)
        assert got == want, (orders_in, got, want)
        assert inventory == inv_copy, "inventory input was mutated"


def test_no_function_longer_than_20_lines():
    tree = ast.parse(open(SRC, encoding="utf-8").read())
    bad = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            length = node.end_lineno - node.lineno + 1
            if length > 20:
                bad.append((node.name, length))
    assert not bad, f"functions over 20 lines: {bad}"


def test_every_function_has_full_type_hints():
    tree = ast.parse(open(SRC, encoding="utf-8").read())
    problems = []
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        args = node.args.posonlyargs + node.args.args + node.args.kwonlyargs
        if node.args.vararg:
            args.append(node.args.vararg)
        if node.args.kwarg:
            args.append(node.args.kwarg)
        for arg in args:
            if arg.annotation is None:
                problems.append(f"{node.name}: parameter {arg.arg} untyped")
        if node.returns is None:
            problems.append(f"{node.name}: return untyped")
    assert not problems, problems


def test_only_stdlib_imports_in_orders_module():
    tree = ast.parse(open(SRC, encoding="utf-8").read())
    stdlib = set(sys.stdlib_module_names)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [alias.name.split(".")[0] for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [node.module.split(".")[0]] if node.module else []
        else:
            continue
        for name in names:
            assert name in stdlib, f"non-stdlib import: {name}"


def test_orders_module_lives_in_single_file():
    assert os.path.samefile(orders.__file__, SRC)
    assert not getattr(orders, "__path__", None), "orders must stay a single module file"
