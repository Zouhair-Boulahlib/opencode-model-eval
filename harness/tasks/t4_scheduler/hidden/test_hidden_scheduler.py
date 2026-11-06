import pytest
from scheduler import merge_intervals, find_free_slots, max_concurrent


def test_merge_basic():
    assert merge_intervals([(5, 8), (1, 3), (2, 4), (8, 10)]) == [(1, 4), (5, 10)]


def test_merge_touching():
    assert merge_intervals([(1, 3), (3, 5)]) == [(1, 5)]


def test_merge_contained():
    assert merge_intervals([(1, 10), (2, 3), (4, 5)]) == [(1, 10)]


def test_merge_empty():
    assert merge_intervals([]) == []


def test_merge_single():
    assert merge_intervals([(7, 9)]) == [(7, 9)]


def test_merge_does_not_mutate():
    data = [(5, 8), (1, 3)]
    copy = list(data)
    merge_intervals(data)
    assert data == copy


def test_merge_returns_tuples_sorted():
    out = merge_intervals([(10, 12), (1, 2)])
    assert out == [(1, 2), (10, 12)]
    assert all(isinstance(t, tuple) for t in out)


def test_merge_invalid_raises():
    with pytest.raises(ValueError):
        merge_intervals([(5, 5)])
    with pytest.raises(ValueError):
        merge_intervals([(1, 2), (6, 4)])


def test_free_basic():
    assert find_free_slots([(540, 600), (720, 780)], 480, 1020, 60) == [(480, 540), (600, 720), (780, 1020)]


def test_free_min_filter():
    assert find_free_slots([(540, 600)], 480, 1020, 90) == [(600, 1020)]


def test_free_empty_busy():
    assert find_free_slots([], 480, 1020, 30) == [(480, 1020)]


def test_free_empty_busy_day_too_short():
    assert find_free_slots([], 480, 500, 30) == []


def test_free_busy_outside_day_clipped():
    assert find_free_slots([(0, 500), (1000, 2000)], 480, 1020, 30) == [(500, 1000)]


def test_free_busy_entirely_outside_ignored():
    assert find_free_slots([(0, 100), (2000, 3000)], 480, 1020, 30) == [(480, 1020)]


def test_free_overlapping_unsorted_busy():
    assert find_free_slots([(700, 800), (500, 650), (600, 720)], 480, 900, 10) == [(480, 500), (800, 900)]


def test_free_fully_booked():
    assert find_free_slots([(480, 1020)], 480, 1020, 1) == []


def test_free_gap_exactly_min():
    assert find_free_slots([(500, 600)], 480, 700, 20) == [(480, 500), (600, 700)]
    assert find_free_slots([(500, 600)], 480, 700, 21) == [(600, 700)]


def test_concurrent_basic():
    assert max_concurrent([(0, 10), (5, 15), (10, 20)]) == 2


def test_concurrent_touching_not_overlap():
    assert max_concurrent([(1, 3), (3, 5)]) == 1


def test_concurrent_all_overlap():
    assert max_concurrent([(0, 10), (1, 9), (2, 8), (3, 7)]) == 4


def test_concurrent_empty():
    assert max_concurrent([]) == 0


def test_concurrent_many_start_same_instant():
    assert max_concurrent([(0, 1), (0, 1), (0, 1), (1, 2)]) == 3
