import pytest
from inventory import Inventory


def test_add_rejects_nonpositive_qty():
    inv = Inventory()
    with pytest.raises(ValueError):
        inv.add("A", "a", 0, 1.0)
    with pytest.raises(ValueError):
        inv.add("A", "a", -1, 1.0)


def test_get_unknown_returns_none():
    assert Inventory().get("missing") is None


def test_remove_unknown_raises_keyerror():
    with pytest.raises(KeyError):
        Inventory().remove("missing", 1)


def test_tags_independent_from_argument():
    inv = Inventory()
    shared = ["x"]
    a = inv.add("A", "a", 1, 1.0, shared)
    b = inv.add("B", "b", 1, 1.0, shared)
    a.tags.append("only-a")
    assert b.tags == ["x"]
    assert shared == ["x"]


def test_low_stock_sorted_and_includes_threshold():
    inv = Inventory(low_stock_threshold=3)
    inv.add("C", "c", 3, 1.0)
    inv.add("A", "a", 1, 1.0)
    inv.add("B", "b", 4, 1.0)
    assert inv.low_stock() == ["A", "C"]


def test_total_value_rounded():
    inv = Inventory()
    inv.add("A", "a", 3, 0.1)
    assert inv.total_value() == 0.3


def test_search_name_or_tag_case_insensitive():
    inv = Inventory()
    inv.add("B", "Bolt", 1, 1.0, ["Steel"])
    inv.add("A", "Apple", 1, 1.0, ["food"])
    assert [i.sku for i in inv.search("bolt")] == ["B"]
    assert [i.sku for i in inv.search("steel")] == ["B"]
    assert [i.sku for i in inv.search("foo")] == ["A"]


def test_page_past_end_empty_and_sorted():
    inv = Inventory()
    inv.add("B", "b", 1, 1.0)
    inv.add("A", "a", 1, 1.0)
    inv.add("C", "c", 1, 1.0)
    assert [i.sku for i in inv.page(1, 2)] == ["A", "B"]
    assert [i.sku for i in inv.page(2, 2)] == ["C"]
    assert inv.page(3, 2) == []
