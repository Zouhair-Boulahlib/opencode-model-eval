"""Own verification tests for the orders refactor."""

import ast
import inspect
import sys

import orders
from orders import process_orders


def _module_functions() -> list:
    """Return all function definitions in the orders module."""
    tree = ast.parse(inspect.getsource(orders))
    return [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]


def test_process_orders_behaviour_unchanged():
    res = process_orders(
        [{"id": 1, "customer": "x", "items": [{"sku": "A", "qty": 2}]}],
        {"A": {"price": 10.0, "stock": 5}},
        {},
    )
    assert res == {
        "fulfilled": [{"id": 1, "customer": "x", "total": 20.0}],
        "rejected": [],
        "revenue": 20.0,
        "inventory": {"A": {"price": 10.0, "stock": 3}},
    }


def test_process_orders_signature_and_return_type():
    sig = inspect.signature(process_orders)
    assert list(sig.parameters) == ["orders", "inventory", "discounts"]
    assert sig.return_annotation is not inspect.Parameter.empty


def test_functions_not_longer_than_20_lines():
    for fn in _module_functions():
        length = fn.end_lineno - fn.lineno + 1
        assert length <= 20, f"{fn.name} is {length} lines"


def test_functions_have_type_hints():
    for fn in _module_functions():
        func = getattr(orders, fn.name, None)
        if not callable(func):
            continue
        sig = inspect.signature(func)
        assert sig.return_annotation is not inspect.Parameter.empty, f"{fn.name} return annotation missing"
        for param in sig.parameters.values():
            assert param.annotation is not inspect.Parameter.empty, f"{fn.name} parameter {param.name} missing annotation"


def test_module_uses_stdlib_only():
    tree = ast.parse(inspect.getsource(orders))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] in sys.stdlib_module_names
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            assert module.split(".")[0] in sys.stdlib_module_names
