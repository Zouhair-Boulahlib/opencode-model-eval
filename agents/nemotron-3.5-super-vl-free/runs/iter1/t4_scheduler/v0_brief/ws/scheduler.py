"""Scheduler utilities for integer-minute time intervals.

Intervals are half-open tuples ``(start, end)`` in minutes: ``start`` is
inclusive and ``end`` is exclusive.
"""

from typing import Iterable, List, Tuple

Interval = Tuple[int, int]


def merge_intervals(intervals: Iterable[Interval]) -> List[Interval]:
    """Merge overlapping or touching intervals."""
    sorted_intervals = sorted(intervals, key=lambda iv: (iv[0], iv[1]))
    merged: List[Interval] = []
    for start, end in sorted_intervals:
        if merged and start <= merged[-1][1]:
            prev_start, prev_end = merged[-1]
            merged[-1] = (prev_start, max(prev_end, end))
        else:
            merged.append((start, end))
    return merged


def find_free_slots(
    busy: Iterable[Interval], day_start: int, day_end: int, min_minutes: int
) -> List[Interval]:
    """Return free slots within [day_start, day_end) not covered by busy.

    Only slots with duration >= min_minutes are returned.
    """
    merged = merge_intervals(busy)
    slots: List[Interval] = []
    cursor = day_start
    for start, end in merged:
        if start > cursor:
            slots.append((cursor, start))
        cursor = max(cursor, end)
    if cursor < day_end:
        slots.append((cursor, day_end))
    return [(s, e) for s, e in slots if e - s >= min_minutes]


def max_concurrent(intervals: Iterable[Interval]) -> int:
    """Return the maximum number of intervals overlapping at any point."""
    events: List[Tuple[int, int]] = []
    for start, end in intervals:
        events.append((start, 1))
        events.append((end, -1))
    # End events before start events at the same time so half-open intervals
    # [a, b) and [b, c) are not counted as overlapping.
    events.sort(key=lambda e: (e[0], e[1]))
    current = best = 0
    for _, delta in events:
        current += delta
        best = max(best, current)
    return best


if __name__ == "__main__":
    busy = [(9 * 60, 10 * 60), (10 * 60, 11 * 60), (13 * 60, 14 * 60)]
    print(merge_intervals(busy))
    print(find_free_slots(busy, 8 * 60, 17 * 60, 30))
    print(max_concurrent([(0, 5), (3, 10), (8, 12)]))
