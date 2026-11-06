import pytest

from inventory import Inventory


def test_qty_positive():
    inv = Inventory()
    with pytest.raises(ValueError):
        inv.add("X", "x", 0, 1.0)


def test_tags_independent():
    inv = Inventory()
    a = inv.add("X", "x", 1, 1.0)
    b = inv.add("Y", "y", 1, 1.0)
    a.tags.append("only-x")
    assert b.tags == []
    assert a.tags != b.tags


def test_remove_to_zero_keeps_item():
    inv = Inventory()
    inv.add("X", "x", 2, 1.0)
    inv.remove("X", 2)
    assert inv.get("X") is not None
    assert inv.get("X").qty == 0
    inv.add("X", "x", 3, 1.0)
    assert inv.get("X").qty == 3


def test_low_stock_threshold_inclusive():
    inv = Inventory(low_stock_threshold=5)
    inv.add("A", "a", 5, 1.0)
    inv.add("B", "b", 6, 1.0)
    inv.add("C", "c", 3, 1.0)
    assert inv.low_stock() == ["A", "C"]


def test_total_value_rounded():
    inv = Inventory()
    inv.add("A", "a", 1, 0.333, None)
    assert inv.total_value() == round(0.333, 2)


def test_search_tags_and_case():
    inv = Inventory()
    inv.add("B2", "Bolt", 1, 1.0, ["Steel"])
    assert [i.sku for i in inv.search("steel")] == ["B2"]
    assert [i.sku for i in inv.search("bolt")] == ["B2"]
    assert inv.search("zzz") == []


def test_page_past_end():
    inv = Inventory()
    inv.add("A", "a", 1, 1.0)
    assert inv.page(2, 1) == []
    assert [i.sku for i in inv.page(1, 1)] == ["A"]
