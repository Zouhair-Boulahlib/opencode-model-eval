from scheduler import merge_intervals, find_free_slots, max_concurrent


def test_merge_empty():
    assert merge_intervals([]) == []


def test_merge_overlapping_unsorted():
    assert merge_intervals([(5, 7), (1, 3), (2, 6)]) == [(1, 7)]


def test_merge_touching_and_disjoint():
    assert merge_intervals([(1, 3), (3, 5), (10, 12)]) == [(1, 5), (10, 12)]


def test_merge_nested():
    assert merge_intervals([(1, 10), (2, 3), (4, 5)]) == [(1, 10)]


def test_free_empty_busy():
    assert find_free_slots([], 0, 60, 30) == [(0, 60)]


def test_free_gaps_and_min_minutes():
    busy = [(10, 20), (30, 40)]
    assert find_free_slots(busy, 0, 50, 10) == [(0, 10), (20, 30), (40, 50)]
    assert find_free_slots(busy, 0, 50, 11) == []


def test_free_clips_busy_to_day():
    assert find_free_slots([(-10, 5), (55, 100)], 0, 50, 1) == [(5, 50)]


def test_free_unsorted_busy():
    assert find_free_slots([(30, 40), (10, 20)], 0, 50, 10) == [(0, 10), (20, 30), (40, 50)]


def test_max_concurrent_empty_and_single():
    assert max_concurrent([]) == 0
    assert max_concurrent([(1, 5)]) == 1


def test_max_concurrent_overlap():
    assert max_concurrent([(1, 5), (2, 6), (3, 7)]) == 3


def test_max_concurrent_touching_not_overlap():
    assert max_concurrent([(1, 5), (5, 10), (2, 3)]) == 2


def test_max_concurrent_disjoint():
    assert max_concurrent([(1, 2), (3, 4), (5, 6)]) == 1
