from inventory import Inventory


def test_add_new_item_tags_independent():
    inv = Inventory()
    a = inv.add("X", "x", 1, 1.0)
    b = inv.add("Y", "y", 1, 1.0)
    assert a.tags is not b.tags
    a.tags.append("t")
    assert b.tags == []


def test_add_existing_increases_qty_only():
    inv = Inventory()
    inv.add("X", "x", 1, 1.0, ["a"])
    inv.add("X", "x2", 2, 9.9, ["b"])
    item = inv.get("X")
    assert item.qty == 3
    assert item.name == "x"
    assert item.price == 1.0
    assert item.tags == ["a"]


def test_add_nonpositive_raises():
    inv = Inventory()
    for q in (0, -1):
        try:
            inv.add("X", "x", q, 1.0)
            raise AssertionError("expected ValueError")
        except ValueError:
            pass


def test_remove_unknown_raises_keyerror():
    inv = Inventory()
    try:
        inv.remove("nope", 1)
        raise AssertionError("expected KeyError")
    except KeyError:
        pass


def test_remove_insufficient_raises():
    inv = Inventory()
    inv.add("X", "x", 2, 1.0)
    try:
        inv.remove("X", 3)
        raise AssertionError("expected ValueError")
    except ValueError:
        pass


def test_remove_to_zero_keeps():
    inv = Inventory()
    inv.add("X", "x", 2, 1.0)
    inv.remove("X", 2)
    assert inv.get("X") is not None
    assert inv.get("X").qty == 0


def test_low_stock_inclusive():
    inv = Inventory(low_stock_threshold=5)
    inv.add("A", "a", 5, 1.0)
    inv.add("B", "b", 6, 1.0)
    assert inv.low_stock() == ["A"]


def test_total_value_rounded():
    inv = Inventory()
    inv.add("A", "a", 3, 1.111, [])
    assert inv.total_value() == round(3 * 1.111, 2)


def test_search_case_insensitive_name_and_tags():
    inv = Inventory()
    inv.add("A", "Apple", 1, 1.0, ["Fruit"])
    inv.add("B", "bolt", 1, 1.0, ["hardware"])
    assert [i.sku for i in inv.search("apple")] == ["A"]
    assert [i.sku for i in inv.search("FRUIT")] == ["A"]
    assert [i.sku for i in inv.search("HARD")] == ["B"]


def test_page_one_indexed():
    inv = Inventory()
    for i in range(5):
        inv.add(f"S{i}", f"n{i}", 1, 1.0)
    assert [x.sku for x in inv.page(1, 2)] == ["S0", "S1"]
    assert [x.sku for x in inv.page(2, 2)] == ["S2", "S3"]
    assert [x.sku for x in inv.page(3, 2)] == ["S4"]
    assert inv.page(10, 2) == []
