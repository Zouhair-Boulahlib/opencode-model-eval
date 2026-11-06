import pytest
from scheduler import merge_intervals, find_free_slots, max_concurrent


def test_merge_empty():
    assert merge_intervals([]) == []


def test_merge_basic():
    assert merge_intervals([(1, 3), (3, 5)]) == [(1, 5)]
    assert merge_intervals([(1, 4), (2, 3)]) == [(1, 4)]


def test_merge_unsorted_no_mutate():
    inp = [(5, 7), (1, 3)]
    out = merge_intervals(inp)
    assert out == [(1, 3), (5, 7)]
    assert inp == [(5, 7), (1, 3)]


def test_merge_invalid():
    with pytest.raises(ValueError):
        merge_intervals([(2, 2)])
    with pytest.raises(ValueError):
        merge_intervals([(3, 1)])


def test_free_basic():
    assert find_free_slots([], 0, 10, 1) == [(0, 10)]


def test_free_min():
    assert find_free_slots([], 0, 10, 15) == []


def test_free_clip():
    assert find_free_slots([( -5, 3), (7, 20)], 0, 10, 1) == [(3, 7)]


def test_free_overlap():
    assert find_free_slots([(1, 4), (2, 5)], 0, 10, 2) == [(5, 10)]


def test_free_outside():
    assert find_free_slots([(20, 30)], 0, 10, 1) == [(0, 10)]


def test_max_concurrent():
    assert max_concurrent([]) == 0
    assert max_concurrent([(1, 3), (3, 5)]) == 1
    assert max_concurrent([(1, 4), (2, 3), (2, 5)]) == 3


def test_max_invalid():
    with pytest.raises(ValueError):
        max_concurrent([(1, 1)])
