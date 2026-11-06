import pytest
from inventory import Inventory


def make():
    inv = Inventory(low_stock_threshold=5)
    inv.add("B2", "Bolt", 10, 0.5, ["hardware", "steel"])
    inv.add("A1", "Apple", 5, 1.25, ["food"])
    inv.add("C3", "Cable", 2, 7.0)
    return inv


def test_add_validates_positive_qty():
    with pytest.raises(ValueError):
        Inventory().add("X", "x", 0, 1.0)


def test_add_unknown_returns_item_and_existing_only_qty():
    inv = make()
    inv.add("A1", "Different", 3, 99.0)
    item = inv.get("A1")
    assert item.qty == 8
    assert item.price == 1.25
    assert item.name == "Apple"


def test_tags_independent_without_tags():
    inv = Inventory()
    a = inv.add("X", "x", 1, 1.0)
    b = inv.add("Y", "y", 1, 1.0)
    a.tags.append("only-x")
    assert b.tags == []
    assert inv.add("Z", "z", 1, 1.0, ["t"]).tags == ["t"]


def test_remove_unknown_raises_keyerror():
    with pytest.raises(KeyError):
        make().remove("NOPE", 1)


def test_remove_insufficient_raises_valueerror():
    with pytest.raises(ValueError):
        make().remove("C3", 3)


def test_remove_to_zero_keeps_item_and_can_restock():
    inv = make()
    inv.remove("C3", 2)
    assert inv.get("C3") is not None
    assert inv.get("C3").qty == 0
    inv.add("C3", "Cable", 4, 7.0)
    assert inv.get("C3").qty == 4


def test_get_missing_returns_none():
    assert Inventory().get("missing") is None


def test_low_stock_includes_threshold_and_sorted():
    inv = make()
    assert inv.low_stock() == ["A1", "C3"]
    inv2 = Inventory(low_stock_threshold=0)
    inv2.add("A", "a", 1, 1.0)
    inv2.remove("A", 1)
    assert inv2.low_stock() == ["A"]


def test_total_value_rounded():
    assert make().total_value() == round(10 * 0.5 + 5 * 1.25 + 2 * 7.0, 2)


def test_search_name_and_tags_case_insensitive_sorted():
    inv = make()
    assert [i.sku for i in inv.search("apple")] == ["A1"]
    assert [i.sku for i in inv.search("STEEL")] == ["B2"]
    assert [i.sku for i in inv.search("a")] == ["A1", "B2", "C3"]


def test_page_one_indexed_and_past_end():
    inv = make()
    assert [i.sku for i in inv.page(1, 2)] == ["A1", "B2"]
    assert [i.sku for i in inv.page(2, 2)] == ["C3"]
    assert inv.page(3, 2) == []
