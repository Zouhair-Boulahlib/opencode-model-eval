import ast
from pathlib import Path

import orders
from orders import process_orders

import test_orders


def test_provided_tests_all_present():
    # run the provided tests directly (pytest collects them too)
    assert hasattr(test_orders, "test_fulfilled_and_totals")


def test_function_length_max_20_lines():
    src = Path("orders.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            length = (node.end_lineno or node.lineno) - node.lineno + 1
            assert length <= 20, f"{node.name} is {length} lines"


def test_all_functions_fully_annotated():
    tree = ast.parse(Path("orders.py").read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = list(node.args.args) + list(node.args.kwonlyargs)
            if node.args.vararg:
                args.append(node.args.vararg)
            if node.args.kwarg:
                args.append(node.args.kwarg)
            for a in args:
                assert a.annotation is not None, f"{node.name}.{a.arg} missing annotation"
            assert node.returns is not None, f"{node.name} missing return annotation"


def test_process_orders_signature_unchanged():
    import inspect

    params = list(inspect.signature(process_orders).parameters)
    assert params == ["orders", "inventory", "discounts"]


def test_single_source_file_no_third_party_imports():
    tree = ast.parse(Path("orders.py").read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] == "orders" or alias.name in __import__("sys").stdlib_module_names
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0:
                assert (node.module or "").split(".")[0] in __import__("sys").stdlib_module_names


def test_uses_only_orders_py():
    src = [p.name for p in Path(".").glob("*.py")]
    assert set(src) <= {"orders.py", "test_orders.py", "test_own.py"}


def test_returns_exact_structure():
    INVENTORY = {"A": {"price": 10.0, "stock": 5}}
    res = process_orders([{"id": 1, "customer": "c", "items": [{"sku": "A", "qty": 2}]}], INVENTORY, {})
    assert res == {"fulfilled": [{"id": 1, "customer": "c", "total": 20.0}], "rejected": [], "revenue": 20.0,
                   "inventory": {"A": {"price": 10.0, "stock": 3}}}


def test_rejected_helper_types():
    assert callable(orders._copy_inventory)
