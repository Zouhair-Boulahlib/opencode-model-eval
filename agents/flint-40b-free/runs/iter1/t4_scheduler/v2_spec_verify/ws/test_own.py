import pytest

from scheduler import find_free_slots, max_concurrent, merge_intervals


class TestMergeIntervals:
    def test_empty(self):
        assert merge_intervals([]) == []

    def test_merges_touching(self):
        assert merge_intervals([(1, 3), (3, 5)]) == [(1, 5)]

    def test_merges_overlapping(self):
        assert merge_intervals([(1, 4), (2, 3)]) == [(1, 4)]

    def test_unsorted(self):
        assert merge_intervals([(5, 7), (1, 3), (3, 5)]) == [(1, 7)]

    def test_no_mutation(self):
        intervals = [(3, 5), (1, 3)]
        merge_intervals(intervals)
        assert intervals == [(3, 5), (1, 3)]

    def test_empty_interval_raises(self):
        with pytest.raises(ValueError):
            merge_intervals([(3, 3)])

    def test_reversed_interval_raises(self):
        with pytest.raises(ValueError):
            merge_intervals([(5, 2)])


class TestFindFreeSlots:
    def test_empty_busy_whole_day(self):
        assert find_free_slots([], 540, 1020, 60) == [(540, 1020)]

    def test_day_too_short(self):
        assert find_free_slots([], 540, 600, 120) == []

    def test_min_minutes_filter(self):
        assert find_free_slots([(550, 570)], 540, 1020, 10) == [
            (540, 550),
            (570, 1020),
        ]

    def test_busy_removes_slot(self):
        assert find_free_slots([(550, 570)], 540, 1020, 30) == [(570, 1020)]

    def test_overlapping_busy(self):
        busy = [(550, 580), (560, 570)]
        assert find_free_slots(busy, 540, 1020, 30) == [(580, 1020)]

    def test_clipping(self):
        assert find_free_slots([(-10, 550)], 540, 1020, 30) == [(550, 1020)]

    def test_outside_day_ignored(self):
        assert find_free_slots([(1100, 1200)], 540, 1020, 30) == [(540, 1020)]

    def test_touching_busy_merged(self):
        busy = [(540, 550), (550, 560)]
        assert find_free_slots(busy, 540, 1020, 30) == [(560, 1020)]


class TestMaxConcurrent:
    def test_empty(self):
        assert max_concurrent([]) == 0

    def test_no_overlap(self):
        assert max_concurrent([(1, 3), (3, 5)]) == 1

    def test_three_overlap(self):
        assert max_concurrent([(1, 5), (2, 6), (3, 4)]) == 3

    def test_nested(self):
        assert max_concurrent([(0, 10), (1, 5), (2, 3)]) == 3
