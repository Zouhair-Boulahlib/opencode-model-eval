import pytest
from inventory import Inventory


def test_add_tags_independent():
    """Items created without tags must never share the same list object."""
    inv = Inventory()
    a = inv.add("X", "x", 1, 1.0)
    b = inv.add("Y", "y", 1, 1.0)
    a.tags.append("only-x")
    assert b.tags == []


def test_add_negative_qty_raises():
    """qty <= 0 raises ValueError."""
    inv = Inventory()
    with pytest.raises(ValueError):
        inv.add("X", "x", 0, 1.0)
    with pytest.raises(ValueError):
        inv.add("X", "x", -1, 1.0)


def test_remove_unknown_sku_raises_keyerror():
    """Unknown SKU raises KeyError."""
    inv = Inventory()
    with pytest.raises(KeyError):
        inv.remove("X", 1)


def test_remove_more_than_available_raises_valueerror():
    """Removing more than available raises ValueError."""
    inv = Inventory()
    inv.add("X", "x", 5, 1.0)
    with pytest.raises(ValueError):
        inv.remove("X", 10)


def test_remove_to_zero_keeps_item():
    """Item stays in inventory with qty 0 when fully removed."""
    inv = Inventory()
    inv.add("X", "x", 5, 1.0)
    inv.remove("X", 5)
    assert inv.get("X") is not None
    assert inv.get("X").qty == 0


def test_low_stock_includes_threshold():
    """low_stock includes items at the threshold."""
    inv = Inventory(low_stock_threshold=5)
    inv.add("A", "Apple", 5, 1.0)
    inv.add("B", "Banana", 10, 2.0)
    assert inv.low_stock() == ["A"]


def test_low_stock_sorted():
    """low_stock returns sorted SKUs."""
    inv = Inventory()
    inv.add("C", "Cherry", 1, 1.0)
    inv.add("A", "Apple", 1, 1.0)
    inv.add("B", "Banana", 1, 1.0)
    assert inv.low_stock() == ["A", "B", "C"]


def test_total_value():
    """total_value is qty * price rounded to 2 decimals."""
    inv = Inventory()
    inv.add("A", "Apple", 3, 1.50)
    inv.add("B", "Banana", 2, 2.75)
    assert inv.total_value() == round(3 * 1.50 + 2 * 2.75, 2)


def test_search_case_insensitive_name():
    """Search is case-insensitive substring match on name."""
    inv = Inventory()
    inv.add("A1", "Apple", 1, 1.0)
    inv.add("A2", "applet", 1, 1.0)
    result = inv.search("apple")
    assert [i.sku for i in result] == ["A1", "A2"]


def test_search_case_insensitive_tags():
    """Search matches tags case-insensitively."""
    inv = Inventory()
    inv.add("A1", "Apple", 1, 1.0, ["hardware", "steel"])
    result = inv.search("STEEL")
    assert [i.sku for i in result] == ["A1"]


def test_page_one_indexed():
    """1-indexed pagination over items sorted by sku."""
    inv = Inventory()
    inv.add("A", "Apple", 1, 1.0)
    inv.add("B", "Banana", 1, 1.0)
    inv.add("C", "Cherry", 1, 1.0)
    assert [i.sku for i in inv.page(1, 2)] == ["A", "B"]
    assert [i.sku for i in inv.page(2, 2)] == ["C"]
    assert inv.page(3, 2) == []


def test_page_past_end_returns_empty():
    """Page past the end returns []."""
    inv = Inventory()
    inv.add("A", "Apple", 1, 1.0)
    assert inv.page(99, 1) == []
