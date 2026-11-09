from scheduler import find_free_slots, max_concurrent, merge_intervals


def test_merge_overlapping():
    assert merge_intervals([(1, 3), (2, 5), (8, 10)]) == [(1, 5), (8, 10)]


def test_merge_touching():
    assert merge_intervals([(1, 4), (4, 6)]) == [(1, 6)]


def test_merge_unsorted_and_empty():
    assert merge_intervals([]) == []
    assert merge_intervals([(5, 7), (0, 2)]) == [(0, 2), (5, 7)]


def test_merge_contained():
    assert merge_intervals([(0, 100), (10, 20)]) == [(0, 100)]


def test_free_slots_basic():
    assert find_free_slots([(60, 120), (180, 240)], 0, 300, 30) == [
        (0, 60),
        (120, 180),
        (240, 300),
    ]


def test_free_slots_min_minutes_filters():
    assert find_free_slots([(60, 120), (180, 240)], 0, 300, 61) == []


def test_free_slots_clips_to_day():
    assert find_free_slots([(-50, 50), (250, 400)], 0, 300, 0) == [(50, 250)]


def test_free_slots_empty_busy():
    assert find_free_slots([], 10, 20, 5) == [(10, 20)]


def test_free_slots_fully_busy():
    assert find_free_slots([(0, 300)], 0, 300, 1) == []


def test_max_concurrent_overlap():
    assert max_concurrent([(0, 10), (5, 15), (12, 20)]) == 2


def test_max_concurrent_touching_not_overlap():
    assert max_concurrent([(0, 10), (10, 20)]) == 1


def test_max_concurrent_empty_and_single():
    assert max_concurrent([]) == 0
    assert max_concurrent([(3, 9)]) == 1


def test_max_concurrent_identical():
    assert max_concurrent([(0, 5), (0, 5), (0, 5)]) == 3
