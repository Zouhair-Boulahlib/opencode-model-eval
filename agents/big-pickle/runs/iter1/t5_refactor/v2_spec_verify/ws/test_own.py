"""Self-checks for the refactoring rules (does not replace test_orders.py)."""

import ast
import inspect
import sys

import orders
from orders import process_orders


def _functions():
    return [
        obj for name, obj in vars(orders).items()
        if inspect.isfunction(obj) and obj.__module__ == orders.__name__
    ]


def test_functions_at_most_20_lines():
    for func in _functions():
        source = inspect.getsource(func)
        assert len(source.splitlines()) <= 20, (func.__name__, len(source.splitlines()))


def test_every_function_fully_annotated():
    for func in _functions():
        sig = inspect.signature(func)
        assert sig.return_annotation is not inspect.Signature.empty, func.__name__
        for param in sig.parameters.values():
            assert param.annotation is not inspect.Parameter.empty, (func.__name__, param.name)


def test_process_orders_signature_and_behavior():
    sig = inspect.signature(process_orders)
    assert list(sig.parameters) == ["orders", "inventory", "discounts"]
    inv = {"A": {"price": 10.0, "stock": 5}}
    res = process_orders(
        [{"id": 1, "customer": "x", "items": [{"sku": "A", "qty": 2}]}],
        inv,
        {"SAVE10": 10},
    )
    assert res["fulfilled"] == [{"id": 1, "customer": "x", "total": 20.0}]
    assert res["inventory"] == {"A": {"price": 10.0, "stock": 3}}
    assert inv["A"]["stock"] == 5


def test_only_stdlib_imports():
    with open(orders.__file__, encoding="utf-8") as handle:
        tree = ast.parse(handle.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] in sys.stdlib_module_names
        elif isinstance(node, ast.ImportFrom):
            assert node.module.split(".")[0] in sys.stdlib_module_names
