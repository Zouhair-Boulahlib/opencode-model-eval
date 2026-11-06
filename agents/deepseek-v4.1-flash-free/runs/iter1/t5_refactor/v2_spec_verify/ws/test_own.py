import ast
import inspect

import orders
from orders import process_orders


def _source_tree():
    return ast.parse(inspect.getsource(orders))


def test_all_functions_at_most_20_lines():
    for node in ast.walk(_source_tree()):
        if isinstance(node, ast.FunctionDef):
            assert node.end_lineno - node.lineno + 1 <= 20, node.name


def test_all_functions_fully_annotated():
    for node in ast.walk(_source_tree()):
        if isinstance(node, ast.FunctionDef):
            assert all(a.annotation is not None for a in node.args.args), node.name
            assert node.returns is not None, node.name


def test_signature_preserved():
    sig = inspect.signature(process_orders)
    assert list(sig.parameters) == ["orders", "inventory", "discounts"]
    assert sig.return_annotation is not inspect.Signature.empty


def test_behaviour_smoke():
    inventory = {"A": {"price": 10.0, "stock": 5}}
    orders_list = [
        {"id": 1, "customer": "x", "items": [{"sku": "A", "qty": 2}]},
        {"id": 2, "customer": "y", "items": [{"sku": "A", "qty": 9}]},
    ]
    res = process_orders(orders_list, inventory, {})
    assert res["fulfilled"] == [{"id": 1, "customer": "x", "total": 20.0}]
    assert res["rejected"] == [{"id": 2, "reason": "out of stock A"}]
    assert res["revenue"] == 20.0
    assert res["inventory"]["A"]["stock"] == 3
    assert inventory["A"]["stock"] == 5
