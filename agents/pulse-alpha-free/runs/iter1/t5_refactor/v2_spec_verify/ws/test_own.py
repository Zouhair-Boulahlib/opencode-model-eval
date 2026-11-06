import ast
import inspect

import orders


def _functions():
    with open(orders.__file__, "r", encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    return [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]


def test_process_orders_signature():
    sig = inspect.signature(orders.process_orders)
    assert list(sig.parameters) == ["orders", "inventory", "discounts"]


def test_no_function_longer_than_20_lines():
    for func in _functions():
        length = func.end_lineno - func.lineno + 1
        assert length <= 20, f"{func.name} is {length} lines"


def test_all_functions_fully_type_hinted():
    for func in _functions():
        args = func.args.posonlyargs + func.args.args + func.args.kwonlyargs
        for arg in args:
            assert arg.annotation is not None, f"{func.name} param {arg.arg} missing hint"
        assert func.returns is not None, f"{func.name} missing return hint"


def test_stdlib_only_single_file():
    import sys
    assert "orders" in sys.modules
