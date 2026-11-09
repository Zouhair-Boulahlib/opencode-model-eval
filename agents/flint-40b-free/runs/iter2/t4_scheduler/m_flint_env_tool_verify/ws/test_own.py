import pytest

from scheduler import merge_intervals, find_free_slots, max_concurrent


def test_merge_overlapping():
    assert merge_intervals([(1, 4), (2, 3)]) == [(1, 4)]


def test_merge_touching():
    assert merge_intervals([(1, 3), (3, 5)]) == [(1, 5)]


def test_merge_unsorted():
    assert merge_intervals([(3, 5), (1, 2)]) == [(1, 2), (3, 5)]
    assert merge_intervals([(3, 5), (2, 4), (1, 3)]) == [(1, 5)]


def test_merge_no_mutation_and_new_list():
    intervals = [(3, 5), (1, 3)]
    result = merge_intervals(intervals)
    assert result == [(1, 5)]
    assert intervals == [(3, 5), (1, 3)]
    result.append((9, 10))
    assert intervals == [(3, 5), (1, 3)]


def test_merge_empty():
    assert merge_intervals([]) == []


def test_merge_invalid():
    with pytest.raises(ValueError):
        merge_intervals([(3, 3)])


def test_free_slots_empty_busy():
    assert find_free_slots([], 540, 1020, 60) == [(540, 1020)]


def test_free_slots_short_day():
    assert find_free_slots([], 540, 599, 60) == []


def test_free_slots_with_busy():
    busy = [(540, 600), (580, 700)]
    assert find_free_slots(busy, 540, 1020, 30) == [(700, 1020)]


def test_free_slots_min_minutes_filter():
    busy = [(540, 600)]
    assert find_free_slots(busy, 540, 1020, 120) == [(600, 1020)]
    assert find_free_slots(busy, 540, 1020, 450) == []


def test_free_slots_clipped_and_outside():
    busy = [(0, 100), (1000, 1200), (1020, 1100)]
    assert find_free_slots(busy, 540, 1020, 30) == [(540, 1000)]


def test_free_slots_unsorted_busy():
    busy = [(700, 800), (540, 600)]
    assert find_free_slots(busy, 540, 1020, 30) == [(600, 700), (800, 1020)]


def test_max_concurrent_empty():
    assert max_concurrent([]) == 0


def test_max_concurrent_touching_not_overlap():
    assert max_concurrent([(1, 3), (3, 5), (5, 7)]) == 1


def test_max_concurrent_overlap():
    assert max_concurrent([(1, 5), (2, 6), (3, 4)]) == 3


def test_max_concurrent_disjoint():
    assert max_concurrent([(1, 2), (3, 4), (5, 6)]) == 1


def test_max_concurrent_single():
    assert max_concurrent([(1, 2)]) == 1
