import pytest
from inventory import Inventory


def test_add_qty_zero_or_negative_raises():
    inv = Inventory()
    with pytest.raises(ValueError):
        inv.add("X", "x", 0, 1.0)
    with pytest.raises(ValueError):
        inv.add("X", "x", -1, 1.0)


def test_add_existing_updates_qty_only():
    inv = Inventory()
    inv.add("X", "x", 1, 1.0, ["a"])
    inv.add("X", "new-name", 2, 9.9, ["b"])
    item = inv.get("X")
    assert item.qty == 3
    assert item.name == "x"
    assert item.price == 1.0
    assert item.tags == ["a"]


def test_tags_independent():
    inv = Inventory()
    inv.add("X", "x", 1, 1.0)
    inv.add("Y", "y", 1, 1.0)
    assert inv.get("X").tags is not inv.get("Y").tags
    inv.get("X").tags.append("t")
    assert inv.get("Y").tags == []
    inv.add("Z", "z", 1, 1.0, ["t2"])
    assert inv.get("Z").tags == ["t2"]


def test_remove_unknown_sku_raises():
    with pytest.raises(KeyError):
        Inventory().remove("nope", 1)


def test_remove_more_than_available_raises():
    inv = Inventory()
    inv.add("X", "x", 3, 1.0)
    with pytest.raises(ValueError):
        inv.remove("X", 4)
    assert inv.get("X").qty == 3


def test_remove_to_zero_stays():
    inv = Inventory()
    inv.add("X", "x", 2, 1.0)
    inv.remove("X", 2)
    assert inv.get("X") is not None
    assert inv.get("X").qty == 0
    inv.add("X", "x", 5, 1.0)
    assert inv.get("X").qty == 5


def test_get_returns_none_for_unknown():
    assert Inventory().get("nope") is None


def test_low_stock_strictly_below_and_equal():
    inv = Inventory(low_stock_threshold=2)
    inv.add("A", "a", 2, 1.0)
    inv.add("B", "b", 3, 1.0)
    assert inv.low_stock() == ["A"]


def test_total_value_rounds():
    inv = Inventory()
    inv.add("A", "a", 3, 0.333333)
    assert inv.total_value() == round(3 * 0.333333, 2)


def test_search_name_and_tags_case_insensitive():
    inv = Inventory()
    inv.add("B", "Bolt", 1, 1.0, ["Steel"])
    inv.add("A", "apple", 1, 1.0)
    inv.add("C", "cat", 1, 1.0, ["food"])
    result = inv.search("OO")
    assert [i.sku for i in result] == ["C"]
    result = inv.search("OOD")
    assert [i.sku for i in result] == ["C"]


def test_page():
    inv = Inventory()
    for sku in ["A", "B", "C", "D", "E"]:
        inv.add(sku, sku, 1, 1.0)
    assert [i.sku for i in inv.page(1, 2)] == ["A", "B"]
    assert [i.sku for i in inv.page(2, 2)] == ["C", "D"]
    assert [i.sku for i in inv.page(3, 2)] == ["E"]
    assert inv.page(4, 2) == []
    assert [i.sku for i in inv.page(1, 2)] == ["A", "B"]  # re-check first page still fine
