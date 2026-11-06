"""Utilities for integer-minute time intervals.

Intervals are represented as (start, end) tuples of integer minutes,
where 0 <= start < end. All functions treat intervals as half-open
[start, end).
"""

from typing import Iterable, List, Sequence, Tuple

Interval = Tuple[int, int]


def merge_intervals(intervals: Iterable[Interval]) -> List[Interval]:
    """Merge overlapping or touching intervals into a sorted disjoint list.

    Args:
        intervals: Iterable of (start, end) integer-minute intervals.

    Returns:
        Sorted list of disjoint intervals with touching/overlapping
        intervals merged (e.g. (0, 10) and (10, 20) -> (0, 20)).
    """
    ordered = sorted((s, e) for s, e in intervals)
    merged: List[Interval] = []
    for start, end in ordered:
        if merged and start <= merged[-1][1]:
            if end > merged[-1][1]:
                merged[-1] = (merged[-1][0], end)
        else:
            merged.append((start, end))
    return merged


def find_free_slots(
    busy: Iterable[Interval],
    day_start: int,
    day_end: int,
    min_minutes: int,
) -> List[Interval]:
    """Find free slots of at least min_minutes within [day_start, day_end].

    Busy intervals are clipped to the day; gaps between merged busy
    intervals (and the day boundaries) become candidate free slots.

    Args:
        busy: Iterable of (start, end) busy intervals.
        day_start: Day window start (inclusive), in integer minutes.
        day_end: Day window end (exclusive), in integer minutes.
        min_minutes: Minimum slot length required (must be > 0).

    Returns:
        Sorted list of free slots each of length >= min_minutes.
        Empty list if the window is invalid or min_minutes <= 0.
    """
    if min_minutes <= 0 or day_start >= day_end:
        return []

    clipped = [
        (max(s, day_start), min(e, day_end))
        for s, e in busy
        if min(e, day_end) > max(s, day_start)
    ]
    merged = merge_intervals(clipped)

    free: List[Interval] = []
    cursor = day_start
    for start, end in merged:
        if start - cursor >= min_minutes:
            free.append((cursor, start))
        cursor = max(cursor, end)
    if day_end - cursor >= min_minutes:
        free.append((cursor, day_end))
    return free


def max_concurrent(intervals: Iterable[Interval]) -> int:
    """Return the maximum number of intervals overlapping at any point.

    Uses a sweep over start (+1) and end (-1) events; ties are ordered
    so that ends are processed before starts, matching half-open
    intervals (an interval ending at t does not overlap one starting at t).

    Args:
        intervals: Iterable of (start, end) integer-minute intervals.

    Returns:
        Maximum concurrency (0 for an empty input).
    """
    events: List[Tuple[int, int]] = []
    for start, end in intervals:
        events.append((start, 1))
        events.append((end, -1))
    events.sort(key=lambda ev: (ev[0], ev[1]))

    best = 0
    current = 0
    for _, delta in events:
        current += delta
        if current > best:
            best = current
    return best
