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
