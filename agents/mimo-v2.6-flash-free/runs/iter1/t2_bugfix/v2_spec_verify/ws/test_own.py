import pytest
from inventory import Inventory


def test_add_qty_nonpositive_raises():
    inv = Inventory()
    with pytest.raises(ValueError):
        inv.add("A", "a", 0, 1.0)
    with pytest.raises(ValueError):
        inv.add("A", "a", -1, 1.0)


def test_add_existing_sku_only_increases_qty():
    inv = Inventory()
    inv.add("A", "Apple", 2, 1.0)
    inv.add("A", "Different", 3, 9.9)
    item = inv.get("A")
    assert item.qty == 5
    assert item.name == "Apple"
    assert item.price == 1.0


def test_tags_independent_and_copied():
    inv = Inventory()
    shared = ["t1"]
    a = inv.add("A", "a", 1, 1.0, shared)
    b = inv.add("B", "b", 1, 1.0)
    c = inv.add("C", "c", 1, 1.0)
    assert a.tags is not shared
    a.tags.append("only-a")
    assert b.tags == []
    assert c.tags == []
    shared.append("mutated")
    assert "mutated" not in a.tags


def test_remove_unknown_sku():
    inv = Inventory()
    with pytest.raises(KeyError):
        inv.remove("NOPE", 1)


def test_remove_to_zero_keeps_item_and_restockable():
    inv = Inventory()
    inv.add("A", "a", 4, 2.0)
    inv.remove("A", 4)
    assert inv.get("A") is not None
    assert inv.get("A").qty == 0
    inv.add("A", "a", 7, 2.0)
    assert inv.get("A").qty == 7


def test_low_stock_includes_threshold():
    inv = Inventory(low_stock_threshold=3)
    inv.add("a", "a", 3, 1.0)
    inv.add("b", "b", 4, 1.0)
    inv.add("c", "c", 1, 1.0)
    inv.remove("c", 1)
    assert inv.low_stock() == ["a", "c"]


def test_total_value_rounding():
    inv = Inventory()
    inv.add("a", "a", 3, 1.005)
    assert inv.total_value() == round(3 * 1.005, 2)


def test_search_name_or_tags_case_insensitive_sorted():
    inv = Inventory()
    inv.add("z9", "Widget", 1, 1.0, ["Fragile", "Red"])
    inv.add("a1", "wIDGET case", 1, 1.0)
    inv.add("m5", "Gadget", 1, 1.0, ["red-blue"])
    assert [i.sku for i in inv.search("WiDg")] == ["a1", "z9"]
    assert [i.sku for i in inv.search("RED")] == ["m5", "z9"]
    assert inv.search("nothing") == []


def test_page_past_end_and_bounds():
    inv = Inventory()
    for n in ["a1", "b2", "c3"]:
        inv.add(n, n, 1, 1.0)
    assert [i.sku for i in inv.page(1, 3)] == ["a1", "b2", "c3"]
    assert inv.page(2, 3) == []
    assert inv.page(0, 3) == []
    assert inv.page(3, 2) == []
