import ast
import inspect
import sys
from pathlib import Path

from orders import process_orders

SRC = Path(__file__).with_name("orders.py")


def _funcs():
    tree = ast.parse(SRC.read_text())
    return [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]


def test_function_lengths_le_20():
    for fn in _funcs():
        length = fn.end_lineno - fn.lineno + 1
        assert length <= 20, f"{fn.name} is {length} lines"


def test_all_functions_fully_typed():
    for fn in _funcs():
        args = [*fn.args.posonlyargs, *fn.args.args, *fn.args.kwonlyargs]
        if fn.args.vararg:
            args.append(fn.args.vararg)
        if fn.args.kwarg:
            args.append(fn.args.kwarg)
        for a in args:
            assert a.annotation is not None, f"{fn.name}.{a.arg} missing hint"
        assert fn.returns is not None, f"{fn.name} missing return hint"


def test_process_orders_signature():
    params = list(inspect.signature(process_orders).parameters)
    assert params == ["orders", "inventory", "discounts"]


def test_only_stdlib_imports():
    tree = ast.parse(SRC.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                assert a.name.split(".")[0] in sys.stdlib_module_names
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                assert node.module.split(".")[0] in sys.stdlib_module_names


def test_behaviour_preserved():
    inv = {"A": {"price": 10.0, "stock": 5}, "B": {"price": 2.5, "stock": 2}}
    res = process_orders(
        [{"id": 1, "customer": "c", "items": [{"sku": "A", "qty": 1}], "coupon": ""}],
        inv, {"SAVE10": 10},
    )
    assert res["fulfilled"] == [{"id": 1, "customer": "c", "total": 10.0}]
    assert inv["A"]["stock"] == 5


def test_duplicate_sku_and_empty_items():
    inv = {"A": {"price": 10.0, "stock": 5}}
    res = process_orders(
        [
            {"id": 1, "customer": "c", "items": [{"sku": "A", "qty": 3}, {"sku": "A", "qty": 3}]},
            {"id": 2, "customer": "d", "items": []},
        ],
        inv, {},
    )
    assert res["fulfilled"][0]["total"] == 60.0
    assert res["inventory"]["A"]["stock"] == -1
    assert res["fulfilled"][1] == {"id": 2, "customer": "d", "total": 0.0}
