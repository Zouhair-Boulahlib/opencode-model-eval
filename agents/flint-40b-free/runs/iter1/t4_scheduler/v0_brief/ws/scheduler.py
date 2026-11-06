"""Scheduler helpers for integer-minute time intervals."""

from typing import List, Tuple

Interval = Tuple[int, int]


def merge_intervals(intervals: List[Interval]) -> List[Interval]:
    """Merge overlapping or adjacent intervals into sorted, disjoint intervals."""
    if not intervals:
        return []
    ordered = sorted(intervals, key=lambda iv: iv[0])
    merged: List[List[int]] = [[ordered[0][0], ordered[0][1]]]
    for start, end in ordered[1:]:
        if start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return [(start, end) for start, end in merged]


def find_free_slots(
    busy: List[Interval],
    day_start: int,
    day_end: int,
    min_minutes: int,
) -> List[Interval]:
    """Return free slots within [day_start, day_end] of at least min_minutes.

    Intervals are half-open [start, end) in integer minutes.
    """
    free_slots: List[Interval] = []
    cursor = day_start
    for start, end in merge_intervals(busy):
        if start > cursor and start - cursor >= min_minutes:
            free_slots.append((cursor, start))
        cursor = max(cursor, end)
    if day_end - cursor >= min_minutes:
        free_slots.append((cursor, day_end))
    return free_slots


def max_concurrent(intervals: List[Interval]) -> int:
    """Return the maximum number of intervals overlapping at any minute."""
    events: List[Tuple[int, int]] = []
    for start, end in intervals:
        events.append((start, 1))
        events.append((end, -1))
    events.sort()
    current = 0
    maximum = 0
    for _, delta in events:
        current += delta
        maximum = max(maximum, current)
    return maximum
