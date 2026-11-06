import ast
from pathlib import Path

import orders


def test_function_line_limits():
    source = Path("orders.py").read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            span = node.end_lineno - node.lineno + 1
            assert span <= 20, f"{node.name} is {span} lines"


def test_function_type_hints():
    source = Path("orders.py").read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for arg in (
                node.args.posonlyargs
                + node.args.args
                + node.args.kwonlyargs
            ):
                assert arg.annotation is not None, f"{node.name} param {arg.arg} missing hint"
            if node.args.vararg is not None:
                assert node.args.vararg.annotation is not None, f"{node.name} *args missing hint"
            if node.args.kwarg is not None:
                assert node.args.kwarg.annotation is not None, f"{node.name} **kwargs missing hint"
            assert node.returns is not None, f"{node.name} missing return hint"


def test_process_orders_signature():
    import inspect

    sig = inspect.signature(orders.process_orders)
    assert list(sig.parameters) == ["orders", "inventory", "discounts"]
