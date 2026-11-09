"""Scheduling helpers for integer-minute, half-open time intervals.

Every interval is a ``(start, end)`` pair of integers where ``start < end``.
Intervals are treated as half-open: ``[start, end)``.  An interval ending at
``t`` and another starting at ``t`` therefore do not overlap.
"""

from typing import Iterable, List, Sequence, Tuple

Interval = Tuple[int, int]


def _clean(intervals: Iterable[Sequence[int]]) -> List[Interval]:
    """Return valid intervals as sorted ``(start, end)`` tuples."""
    cleaned = [(int(s), int(e)) for s, e in intervals if int(s) < int(e)]
    cleaned.sort()
    return cleaned


def merge_intervals(intervals: Iterable[Sequence[int]]) -> List[Interval]:
    """Merge overlapping or touching intervals.

    >>> merge_intervals([(1, 3), (2, 5), (8, 10)])
    [(1, 5), (8, 10)]
    >>> merge_intervals([(1, 4), (4, 6)])
    [(1, 6)]
    """
    merged: List[Interval] = []
    for start, end in _clean(intervals):
        if merged and start <= merged[-1][1]:
            prev_start, prev_end = merged[-1]
            merged[-1] = (prev_start, max(prev_end, end))
        else:
            merged.append((start, end))
    return merged


def find_free_slots(
    busy: Iterable[Sequence[int]],
    day_start: int,
    day_end: int,
    min_minutes: int,
) -> List[Interval]:
    """Return free gaps within ``[day_start, day_end)`` of at least ``min_minutes``.

    Busy intervals are clipped to the day window and merged first.

    >>> find_free_slots([(60, 120), (180, 240)], 0, 300, 30)
    [(0, 60), (120, 180), (240, 300)]
    """
    if day_start >= day_end:
        return []

    free: List[Interval] = []
    cursor = day_start
    for start, end in merge_intervals(busy):
        start = max(start, day_start)
        end = min(end, day_end)
        if start >= end:
            continue
        if start > cursor:
            free.append((cursor, start))
        cursor = max(cursor, end)

    if cursor < day_end:
        free.append((cursor, day_end))

    return [(s, e) for s, e in free if e - s >= min_minutes]


def max_concurrent(intervals: Iterable[Sequence[int]]) -> int:
    """Return the maximum number of intervals overlapping at any moment.

    Touching intervals do not overlap, so at equal timestamps ends are
    processed before starts.

    >>> max_concurrent([(0, 10), (5, 15), (12, 20)])
    2
    """
    events: List[Tuple[int, int]] = []
    for start, end in _clean(intervals):
        events.append((start, 1))
        events.append((end, -1))

    events.sort(key=lambda event: (event[0], event[1]))

    current = 0
    best = 0
    for _, delta in events:
        current += delta
        best = max(best, current)
    return best
