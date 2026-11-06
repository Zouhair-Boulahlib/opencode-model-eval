import pytest
from inventory import Inventory


def test_qty_zero_or_negative_raises():
    inv = Inventory()
    with pytest.raises(ValueError):
        inv.add("A", "a", 0, 1.0)
    with pytest.raises(ValueError):
        inv.add("A", "a", -1, 1.0)


def test_add_existing_only_increases_qty_keeps_fields():
    inv = Inventory()
    inv.add("A", "Apple", 2, 1.5, ["food"])
    inv.add("A", "Other", 3, 9.99, ["x"])
    item = inv.get("A")
    assert item.qty == 5
    assert item.name == "Apple"
    assert item.price == 1.5
    assert item.tags == ["food"]


def test_tags_independent_default_lists():
    inv = Inventory()
    a = inv.add("A", "a", 1, 1.0)
    b = inv.add("B", "b", 1, 1.0)
    assert a.tags is not b.tags
    a.tags.append("x")
    assert b.tags == []


def test_passed_tags_list_not_aliased():
    inv = Inventory()
    tags = ["one"]
    item = inv.add("A", "a", 1, 1.0, tags)
    tags.append("two")
    assert item.tags == ["one"]


def test_remove_unknown_sku_raises_keyerror():
    with pytest.raises(KeyError):
        Inventory().remove("NOPE", 1)


def test_remove_more_than_available_raises():
    inv = Inventory()
    inv.add("A", "a", 2, 1.0)
    with pytest.raises(ValueError):
        inv.remove("A", 3)


def test_remove_to_zero_keeps_item_restockable():
    inv = Inventory()
    inv.add("A", "a", 2, 1.0)
    inv.remove("A", 2)
    assert inv.get("A") is not None
    assert inv.get("A").qty == 0
    inv.add("A", "a", 4, 1.0)
    assert inv.get("A").qty == 4


def test_get_unknown_returns_none():
    assert Inventory().get("NOPE") is None


def test_low_stock_threshold_inclusive_sorted():
    inv = Inventory(low_stock_threshold=5)
    inv.add("B", "b", 5, 1.0)
    inv.add("A", "a", 5, 1.0)
    inv.add("C", "c", 6, 1.0)
    assert inv.low_stock() == ["A", "B"]


def test_total_value_rounded():
    inv = Inventory()
    inv.add("A", "a", 3, 0.1)
    assert inv.total_value() == 0.3
    assert isinstance(inv.total_value(), float)


def test_search_matches_tags_case_insensitive_sorted_by_sku():
    inv = Inventory()
    inv.add("B", "Banana", 1, 1.0, ["Fruit"])
    inv.add("A", "Apple", 1, 1.0, ["FRUIT"])
    inv.add("C", "Carrot", 1, 1.0, ["vegetable"])
    assert [i.sku for i in inv.search("fruit")] == ["A", "B"]
    assert [i.sku for i in inv.search("CARROT")] == ["C"]
    assert inv.search("zzz") == []


def test_page_one_indexed_and_past_end():
    inv = Inventory()
    for sku in ["C", "A", "B", "D", "E"]:
        inv.add(sku, sku, 1, 1.0)
    assert [i.sku for i in inv.page(1, 2)] == ["A", "B"]
    assert [i.sku for i in inv.page(2, 2)] == ["C", "D"]
    assert [i.sku for i in inv.page(3, 2)] == ["E"]
    assert inv.page(4, 2) == []
