import pytest
from inventory import Inventory


def make():
    inv = Inventory(low_stock_threshold=5)
    inv.add("B2", "Bolt", 10, 0.5, ["hardware", "steel"])
    inv.add("A1", "Apple", 5, 1.25, ["food"])
    inv.add("C3", "Cable", 2, 7.0)
    return inv


def test_add_increases_qty():
    inv = make()
    inv.add("A1", "Apple", 3, 9.99)
    assert inv.get("A1").qty == 8
    assert inv.get("A1").price == 1.25


def test_total_value():
    assert make().total_value() == round(10 * 0.5 + 5 * 1.25 + 2 * 7.0, 2)


def test_remove_insufficient_raises():
    with pytest.raises(ValueError):
        make().remove("C3", 3)


def test_tags_not_shared_between_items():
    inv = Inventory()
    a = inv.add("X", "x", 1, 1.0)
    b = inv.add("Y", "y", 1, 1.0)
    a.tags.append("only-x")
    assert b.tags == []


def test_remove_to_zero_keeps_item():
    inv = make()
    inv.remove("C3", 2)
    assert inv.get("C3") is not None
    assert inv.get("C3").qty == 0


def test_low_stock_includes_threshold():
    inv = make()
    assert inv.low_stock() == ["A1", "C3"]


def test_search_case_insensitive_and_tags():
    inv = make()
    assert [i.sku for i in inv.search("apple")] == ["A1"]
    assert [i.sku for i in inv.search("STEEL")] == ["B2"]


def test_page_is_one_indexed():
    inv = make()
    assert [i.sku for i in inv.page(1, 2)] == ["A1", "B2"]
    assert [i.sku for i in inv.page(2, 2)] == ["C3"]
