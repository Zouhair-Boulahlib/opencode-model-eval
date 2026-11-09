from scheduler import merge_intervals, find_free_slots, max_concurrent


# --- merge_intervals -------------------------------------------------
def test_merge_empty():
    assert merge_intervals([]) == []


def test_merge_single():
    assert merge_intervals([(1, 5)]) == [(1, 5)]


def test_merge_unsorted_overlapping():
    assert merge_intervals([(5, 8), (1, 6)]) == [(1, 8)]


def test_merge_nested():
    assert merge_intervals([(1, 10), (2, 3), (4, 9)]) == [(1, 10)]


def test_merge_adjacent():
    assert merge_intervals([(0, 5), (5, 10)]) == [(0, 10)]


def test_merge_disjoint():
    assert merge_intervals([(10, 20), (0, 5)]) == [(0, 5), (10, 20)]


def test_merge_touching_chain():
    assert merge_intervals([(0, 3), (3, 6), (6, 9), (5, 7)]) == [(0, 9)]


def test_merge_zero_length_ignored():
    assert merge_intervals([(5, 5), (0, 3)]) == [(0, 3)]


# --- find_free_slots --------------------------------------------------
def test_free_whole_day_when_idle():
    assert find_free_slots([], 0, 60, 30) == [(0, 60)]


def test_free_gap_between_busy_blocks():
    busy = [(0, 30), (40, 60)]
    assert find_free_slots(busy, 0, 60, 5) == [(30, 40)]


def test_free_filters_small_gaps():
    busy = [(0, 30), (35, 60)]
    assert find_free_slots(busy, 0, 60, 10) == []


def test_free_after_busy_to_day_end():
    busy = [(0, 20)]
    assert find_free_slots(busy, 0, 60, 30) == [(20, 60)]


def test_free_busy_outside_day_is_clamped():
    busy = [(-50, -10), (100, 200)]
    assert find_free_slots(busy, 0, 60, 10) == [(0, 60)]


def test_free_busy_overlaps_day_edges():
    busy = [(-10, 15), (50, 70)]
    assert find_free_slots(busy, 0, 60, 10) == [(15, 50)]


def test_free_no_gap_if_fully_booked():
    busy = [(0, 60)]
    assert find_free_slots(busy, 0, 60, 1) == []


def test_free_unsorted_overlapping_busy_input():
    busy = [(40, 90), (0, 25), (20, 45)]
    assert find_free_slots(busy, 0, 100, 5) == [(90, 100)]


def test_free_min_minutes_exact_boundary():
    busy = [(0, 30), (40, 60)]
    assert find_free_slots(busy, 0, 60, 10) == [(30, 40)]


def test_free_invalid_day_range():
    assert find_free_slots([(0, 30)], 50, 50, 1) == []
    assert find_free_slots([(0, 30)], 60, 10, 1) == []


# --- max_concurrent ---------------------------------------------------
def test_concurrent_empty():
    assert max_concurrent([]) == 0


def test_concurrent_single():
    assert max_concurrent([(0, 10)]) == 1


def test_concurrent_disjoint():
    assert max_concurrent([(0, 5), (10, 20)]) == 1


def test_concurrent_double_overlap():
    assert max_concurrent([(0, 10), (5, 15)]) == 2


def test_concurrent_triple_burst():
    assert max_concurrent([(0, 10), (2, 4), (3, 8)]) == 3


def test_concurrent_touching_not_overlapping():
    assert max_concurrent([(0, 5), (5, 10)]) == 1


def test_concurrent_nested():
    assert max_concurrent([(0, 100), (10, 20), (10, 30)]) == 3


def test_concurrent_repeated_starts():
    assert max_concurrent([(5, 9), (5, 6), (5, 8)]) == 3
