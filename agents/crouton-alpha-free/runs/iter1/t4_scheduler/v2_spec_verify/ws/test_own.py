import pytest
from scheduler import merge_intervals, find_free_slots, max_concurrent


def test_merge_empty():
    assert merge_intervals([]) == []


def test_merge_touching():
    assert merge_intervals([(1, 3), (3, 5)]) == [(1, 5)]


def test_merge_overlap_nested():
    assert merge_intervals([(1, 4), (2, 3)]) == [(1, 4)]


def test_merge_unsorted_and_no_mutation():
    data = [(5, 7), (1, 3), (2, 4)]
    orig = list(data)
    assert merge_intervals(data) == [(1, 4), (5, 7)]
    assert data == orig


def test_merge_invalid():
    with pytest.raises(ValueError):
        merge_intervals([(3, 3)])
    with pytest.raises(ValueError):
        merge_intervals([(5, 1)])
    with pytest.raises(ValueError):
        merge_intervals([(1, 2), (4, 4)])


def test_merge_disjoint_sorted():
    assert merge_intervals([(10, 12), (1, 2)]) == [(1, 2), (10, 12)]


def test_free_empty_busy():
    assert find_free_slots([], 0, 60, 30) == [(0, 60)]
    assert find_free_slots([], 0, 20, 30) == []


def test_free_basic():
    assert find_free_slots([(10, 20), (30, 40)], 0, 60, 10) == [
        (0, 10),
        (20, 30),
        (40, 60),
    ]


def test_free_min_filter():
    assert find_free_slots([(10, 20)], 0, 30, 15) == []
    assert find_free_slots([(10, 20)], 0, 30, 10) == [(0, 10), (20, 30)]


def test_free_clip_and_outside():
    assert find_free_slots([(-10, 5), (55, 100), (200, 300)], 0, 60, 1) == [
        (5, 55)
    ]


def test_free_overlap_unsorted_busy():
    assert find_free_slots([(20, 40), (10, 30)], 0, 50, 5) == [(0, 10), (40, 50)]


def test_free_touching_busy():
    assert find_free_slots([(0, 10), (10, 20)], 0, 30, 1) == [(20, 30)]


def test_max_empty():
    assert max_concurrent([]) == 0


def test_max_touching_not_overlap():
    assert max_concurrent([(1, 3), (3, 5)]) == 1


def test_max_overlap():
    assert max_concurrent([(1, 4), (2, 3), (2, 5)]) == 3


def test_max_disjoint_and_nested():
    assert max_concurrent([(1, 10), (2, 3), (4, 5)]) == 2
    assert max_concurrent([(1, 2), (3, 4)]) == 1
