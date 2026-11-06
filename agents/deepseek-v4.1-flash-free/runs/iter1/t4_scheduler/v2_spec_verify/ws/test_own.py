import pytest

from scheduler import find_free_slots, max_concurrent, merge_intervals


def test_merge_touching_and_overlapping():
    assert merge_intervals([(1, 3), (3, 5)]) == [(1, 5)]
    assert merge_intervals([(1, 4), (2, 3)]) == [(1, 4)]


def test_merge_unsorted_new_list_no_mutation():
    data = [(5, 7), (1, 3), (2, 4)]
    result = merge_intervals(data)
    assert result == [(1, 4), (5, 7)]
    assert data == [(5, 7), (1, 3), (2, 4)]
    assert result is not data


def test_merge_empty():
    assert merge_intervals([]) == []


def test_merge_invalid():
    with pytest.raises(ValueError):
        merge_intervals([(3, 3)])
    with pytest.raises(ValueError):
        merge_intervals([(5, 2)])


def test_free_empty_busy():
    assert find_free_slots([], 0, 60, 10) == [(0, 60)]
    assert find_free_slots([], 0, 60, 61) == []


def test_free_gaps_and_min_minutes():
    assert find_free_slots([(10, 20), (30, 40)], 0, 60, 10) == [(0, 10), (20, 30), (40, 60)]
    assert find_free_slots([(10, 20), (30, 40)], 0, 60, 11) == [(40, 60)]


def test_free_overlap_unsorted_clipping_outside():
    busy = [(50, 70), (15, 25), (20, 30), (-10, 5), (80, 90)]
    assert find_free_slots(busy, 0, 60, 1) == [(5, 15), (30, 50)]


def test_max_concurrent():
    assert max_concurrent([]) == 0
    assert max_concurrent([(1, 3), (3, 5)]) == 1
    assert max_concurrent([(1, 5), (2, 6), (3, 4)]) == 3
    assert max_concurrent([(1, 2), (5, 6)]) == 1
    assert max_concurrent([(5, 10), (1, 4), (2, 3)]) == 2
