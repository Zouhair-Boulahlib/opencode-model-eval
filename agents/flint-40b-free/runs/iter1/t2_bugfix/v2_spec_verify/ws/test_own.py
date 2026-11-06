import pytest
from inventory import Inventory


def test_add_increases_existing_qty():
    inv = Inventory(low_stock_threshold=5)
    inv.add("A1", "Apple", 5, 1.25, ["food"])
    inv.add("A1", "Apple", 3, 9.99)
    assert inv.get("A1").qty == 8
    assert inv.get("A1").price == 1.25


def test_add_zero_or_negative_qty_raises():
    inv = Inventory()
    with pytest.raises(ValueError):
        inv.add("A1", "Apple", 0, 1.25)
    with pytest.raises(ValueError):
        inv.add("A1", "Apple", -2, 1.25)


def test_tags_not_shared_between_items():
    inv = Inventory()
    a = inv.add("X", "x", 1, 1.0)
    b = inv.add("Y", "y", 1, 1.0)
    a.tags.append("only-x")
    assert b.tags == []


def test_add_tagged_item_gets_independent_list():
    inv = Inventory()
    a = inv.add("X", "x", 1, 1.0, ["t1"])
    b = inv.add("Y", "y", 1, 1.0, ["t2"])
    a.tags.append("t3")
    assert b.tags == ["t2"]


def test_remove_unknown_sku_raises_key_error():
    inv = Inventory()
    with pytest.raises(KeyError):
        inv.remove("NOPE", 1)


def test_remove_more_than_available_raises_value_error():
    inv = Inventory()
    inv.add("A1", "Apple", 2, 1.25)
    with pytest.raises(ValueError):
        inv.remove("A1", 3)


def test_remove_to_zero_keeps_item():
    inv = Inventory()
    inv.add("A1", "Apple", 2, 1.25)
    inv.remove("A1", 2)
    assert inv.get("A1") is not None
    assert inv.get("A1").qty == 0


def test_get_returns_none_for_unknown_sku():
    assert Inventory().get("NOPE") is None


def test_low_stock_sorted_inclusive_of_threshold():
    inv = Inventory(low_stock_threshold=5)
    inv.add("B2", "Bolt", 10, 0.5, ["hardware", "steel"])
    inv.add("A1", "Apple", 5, 1.25, ["food"])
    inv.add("C3", "Cable", 2, 7.0)
    assert inv.low_stock() == ["A1", "C3"]


def test_total_value_rounded_to_two_decimals():
    inv = Inventory()
    inv.add("A1", "Apple", 3, 1.333, ["food"])
    assert inv.total_value() == round(3 * 1.333, 2)


def test_search_name_and_tags_case_insensitive_sorted_by_sku():
    inv = Inventory()
    inv.add("B2", "Bolt", 10, 0.5, ["hardware", "steel"])
    inv.add("A1", "Apple", 5, 1.25, ["food"])
    inv.add("C3", "Cable", 2, 7.0)
    assert [i.sku for i in inv.search("apple")] == ["A1"]
    assert [i.sku for i in inv.search("STEEL")] == ["B2"]
    assert [i.sku for i in inv.search("food")] == ["A1"]
    assert inv.search("zzz") == []


def test_page_one_indexed_and_past_end():
    inv = Inventory()
    inv.add("B2", "Bolt", 10, 0.5)
    inv.add("A1", "Apple", 5, 1.25)
    inv.add("C3", "Cable", 2, 7.0)
    assert [i.sku for i in inv.page(1, 2)] == ["A1", "B2"]
    assert [i.sku for i in inv.page(2, 2)] == ["C3"]
    assert inv.page(3, 2) == []
