from scheduler import find_free_slots, max_concurrent, merge_intervals


def test_merge_intervals_empty():
    assert merge_intervals([]) == []


def test_merge_intervals_overlapping_and_touching():
    assert merge_intervals([(30, 60), (0, 15), (10, 30), (60, 75)]) == [(0, 75)]


def test_merge_intervals_disjoint_and_unsorted():
    assert merge_intervals([(90, 120), (0, 30), (45, 60)]) == [
        (0, 30),
        (45, 60),
        (90, 120),
    ]


def test_merge_intervals_nested():
    assert merge_intervals([(0, 100), (10, 20), (30, 40)]) == [(0, 100)]


def test_find_free_slots_basic():
    busy = [(10, 20), (30, 40)]
    assert find_free_slots(busy, 0, 60, 5) == [(0, 10), (20, 30), (40, 60)]


def test_find_free_slots_filters_short_gaps_and_clamps_day():
    busy = [(0, 10), (15, 20)]
    assert find_free_slots(busy, 5, 40, 10) == [(20, 40)]


def test_find_free_slots_busy_outside_day():
    busy = [(-20, -10), (100, 120), (50, 60)]
    assert find_free_slots(busy, 0, 100, 1) == [(0, 50), (60, 100)]


def test_find_free_slots_no_busy():
    assert find_free_slots([], 0, 30, 30) == [(0, 30)]


def test_find_free_slots_minutes_too_large():
    assert find_free_slots([(0, 20)], 0, 60, 50) == []


def test_max_concurrent_empty():
    assert max_concurrent([]) == 0


def test_max_concurrent_basic():
    assert max_concurrent([(0, 30), (10, 20), (15, 40)]) == 3


def test_max_concurrent_touching_not_overlapping():
    assert max_concurrent([(0, 10), (10, 20), (20, 30)]) == 1


def test_max_concurrent_disjoint():
    assert max_concurrent([(0, 5), (10, 15), (20, 25)]) == 1
