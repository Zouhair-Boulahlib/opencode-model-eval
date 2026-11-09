import pytest

from scheduler import find_free_slots, max_concurrent, merge_intervals


# --- merge_intervals -------------------------------------------------------


def test_merge_empty():
    assert merge_intervals([]) == []


def test_merge_sorts_and_keeps_disjoint():
    assert merge_intervals([(5, 8), (1, 3)]) == [(1, 3), (5, 8)]


def test_merge_overlapping():
    assert merge_intervals([(1, 5), (3, 8), (6, 10)]) == [(1, 10)]


def test_merge_touching_intervals_form_one_block():
    assert merge_intervals([(0, 10), (10, 20)]) == [(0, 20)]
    assert merge_intervals([(1, 4), (4, 6)]) == [(1, 6)]


def test_merge_nested_intervals():
    assert merge_intervals([(1, 10), (2, 3)]) == [(1, 10)]


def test_merge_duplicates_and_gaps():
    assert merge_intervals([(1, 2), (1, 2), (4, 5)]) == [(1, 2), (4, 5)]


def test_merge_ignores_empty_intervals():
    assert merge_intervals([(2, 2), (1, 3)]) == [(1, 3)]


def test_merge_does_not_modify_input():
    data = [(5, 8), (1, 3)]
    merge_intervals(data)
    assert data == [(5, 8), (1, 3)]


def test_merge_rejects_inverted_interval():
    with pytest.raises(ValueError):
        merge_intervals([(5, 1)])


# --- find_free_slots -------------------------------------------------------


def test_free_slots_empty_busy_covers_whole_day():
    assert find_free_slots([], 540, 1020, 60) == [(540, 1020)]


def test_free_slots_splits_around_busy_block():
    assert find_free_slots([(600, 660)], 540, 780, 30) == [
        (540, 600),
        (660, 780),
    ]


def test_free_slots_filters_short_gaps():
    busy = [(600, 660), (665, 700)]
    assert find_free_slots(busy, 540, 780, 10) == [(540, 600), (700, 780)]


def test_free_slots_merges_unsorted_overlapping_busy():
    busy = [(660, 700), (600, 665)]
    assert find_free_slots(busy, 540, 780, 10) == [(540, 600), (700, 780)]


def test_free_slots_exact_minimum_length_qualifies():
    busy = [(0, 10), (40, 50)]
    assert find_free_slots(busy, 0, 50, 30) == [(10, 40)]
    assert find_free_slots(busy, 0, 50, 31) == []


def test_free_slots_busy_covers_entire_day():
    assert find_free_slots([(0, 100)], 0, 100, 1) == []


def test_free_slots_busy_outside_day_is_ignored():
    assert find_free_slots([(-100, -10), (200, 300)], 0, 100, 1) == [(0, 100)]


def test_free_slots_busy_spanning_day_leaves_nothing():
    assert find_free_slots([(-10, 1000)], 0, 100, 1) == []


def test_free_slots_busy_touching_day_edges():
    assert find_free_slots([(0, 30)], 0, 100, 10) == [(30, 100)]
    assert find_free_slots([(70, 100)], 0, 100, 10) == [(0, 70)]


def test_free_slots_zero_min_minutes_still_needs_positive_gap():
    assert find_free_slots([(0, 10)], 0, 10, 0) == []
    assert find_free_slots([(0, 5)], 0, 10, 0) == [(5, 10)]


def test_free_slots_empty_day():
    assert find_free_slots([], 100, 100, 0) == []


def test_free_slots_rejects_bad_arguments():
    with pytest.raises(ValueError):
        find_free_slots([], 100, 0, 10)
    with pytest.raises(ValueError):
        find_free_slots([], 0, 100, -1)
    with pytest.raises(ValueError):
        find_free_slots([(10, 5)], 0, 100, 1)


# --- max_concurrent --------------------------------------------------------


def test_max_concurrent_empty():
    assert max_concurrent([]) == 0


def test_max_concurrent_touching_intervals_do_not_overlap():
    assert max_concurrent([(0, 10), (10, 20)]) == 1


def test_max_concurrent_partial_overlap():
    assert max_concurrent([(0, 10), (5, 15)]) == 2


def test_max_concurrent_counts_peak_not_total():
    assert max_concurrent([(1, 5), (2, 6), (3, 4), (10, 12)]) == 3


def test_max_concurrent_nested_intervals():
    assert max_concurrent([(0, 100), (10, 20), (30, 40)]) == 2


def test_max_concurrent_shared_minute_counts_as_overlap():
    assert max_concurrent([(0, 10), (9, 20)]) == 2


def test_max_concurrent_unsorted_input():
    assert max_concurrent([(10, 12), (1, 5), (2, 6), (3, 4)]) == 3


def test_max_concurrent_ignores_empty_intervals():
    assert max_concurrent([(5, 5), (0, 10)]) == 1


def test_max_concurrent_rejects_inverted_interval():
    with pytest.raises(ValueError):
        max_concurrent([(10, 5)])
