import pytest

from scheduler import find_free_slots, max_concurrent, merge_intervals


def test_merge_touching_and_overlapping():
    assert merge_intervals([(1, 3), (3, 5)]) == [(1, 5)]
    assert merge_intervals([(1, 4), (2, 3)]) == [(1, 4)]


def test_merge_unsorted_new_list_no_mutation():
    original = [(5, 8), (1, 3), (2, 4)]
    snapshot = list(original)
    result = merge_intervals(original)
    assert result == [(1, 4), (5, 8)]
    assert original == snapshot
    assert result is not original


def test_merge_empty():
    assert merge_intervals([]) == []


def test_merge_invalid():
    with pytest.raises(ValueError):
        merge_intervals([(3, 3)])
    with pytest.raises(ValueError):
        merge_intervals([(5, 2)])


def test_free_slots_basic_and_filter():
    assert find_free_slots([(10, 20), (30, 40)], 0, 60, 5) == [(0, 10), (20, 30), (40, 60)]
    assert find_free_slots([(0, 50)], 0, 60, 15) == []


def test_free_slots_unsorted_overlapping_clipped():
    busy = [(35, 45), (15, 25), (20, 30), (-10, 10), (55, 100)]
    assert find_free_slots(busy, 0, 60, 1) == [(10, 15), (30, 35), (45, 55)]


def test_free_slots_outside_day_ignored_and_empty_busy():
    assert find_free_slots([(-50, -10), (70, 80)], 0, 60, 1) == [(0, 60)]
    assert find_free_slots([], 0, 60, 60) == [(0, 60)]
    assert find_free_slots([], 0, 60, 61) == []


def test_max_concurrent():
    assert max_concurrent([]) == 0
    assert max_concurrent([(1, 3), (3, 5)]) == 1
    assert max_concurrent([(1, 5), (2, 6), (5, 8)]) == 2
    assert max_concurrent([(0, 10), (1, 2), (2, 3)]) == 2
