import pytest
from inventory import Inventory

def base():
    inv = Inventory(low_stock_threshold=5)
    inv.add("B2", "Bolt", 10, 0.5, ["hardware", "steel"])
    inv.add("A1", "Apple", 5, 1.25, ["Food"])
    inv.add("C3", "Cable", 2, 7.0)
    return inv

def test_add_qty_le_zero():
    inv = Inventory()
    with pytest.raises(ValueError):
        inv.add("X", "x", 0, 1.0)
    with pytest.raises(ValueError):
        inv.add("X", "x", -1, 1.0)

def test_add_existing_only_qty():
    inv = base()
    inv.add("A1", "NewName", 3, 9.99, ["new"])
    item = inv.get("A1")
    assert item.qty == 8
    assert item.price == 1.25
    assert item.name == "Apple"
    assert item.tags == ["Food"]

def test_tags_independent():
    inv = Inventory()
    a = inv.add("X", "x", 1, 1.0)
    b = inv.add("Y", "y", 1, 1.0)
    assert a.tags is not b.tags
    a.tags.append("only-x")
    assert b.tags == []
    c = inv.add("Z", "z", 1, 1.0, ["shared"])
    c.tags.append("extra")
    assert inv.get("Z").tags == ["shared", "extra"]
    # mutating original list passed in should not affect item
    src = ["a"]
    d = inv.add("W", "w", 1, 1.0, src)
    src.append("b")
    assert d.tags == ["a"]

def test_remove_errors_and_zero():
    inv = base()
    with pytest.raises(KeyError):
        inv.remove("NOPE", 1)
    with pytest.raises(ValueError):
        inv.remove("C3", 3)
    inv.remove("C3", 2)
    assert inv.get("C3") is not None
    assert inv.get("C3").qty == 0
    inv.add("C3", "Cable", 4, 7.0)
    assert inv.get("C3").qty == 4

def test_get_none():
    assert Inventory().get("missing") is None

def test_low_stock_le():
    assert base().low_stock() == ["A1", "C3"]

def test_total_value():
    assert base().total_value() == round(10*0.5 + 5*1.25 + 2*7.0, 2)
    assert Inventory().total_value() == 0

def test_search():
    inv = base()
    assert [i.sku for i in inv.search("apple")] == ["A1"]
    assert [i.sku for i in inv.search("APP")] == ["A1"]
    assert [i.sku for i in inv.search("STEEL")] == ["B2"]
    assert [i.sku for i in inv.search("food")] == ["A1"]
    assert [i.sku for i in inv.search("bolt")] == ["B2"]
    assert inv.search("nomatch") == []

def test_page():
    inv = base()
    assert [i.sku for i in inv.page(1, 2)] == ["A1", "B2"]
    assert [i.sku for i in inv.page(2, 2)] == ["C3"]
    assert inv.page(3, 2) == []
    assert [i.sku for i in inv.page(1, 10)] == ["A1", "B2", "C3"]
