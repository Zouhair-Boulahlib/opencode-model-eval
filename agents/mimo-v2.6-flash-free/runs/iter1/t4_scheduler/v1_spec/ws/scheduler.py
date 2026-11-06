"""Pure functions for interval arithmetic.

Times are integers (minutes). An interval is a tuple ``(start, end)`` and is
half-open: it covers ``start`` but not ``end``.
"""

from __future__ import annotations

__all__ = ["merge_intervals", "find_free_slots", "max_concurrent"]


def _validate(interval: tuple[int, int]) -> tuple[int, int]:
    start, end = interval
    if start >= end:
        raise ValueError(f"invalid interval {interval!r}: start must be < end")
    return start, end


def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Return a new sorted list with overlapping or touching intervals merged.

    ``(1, 3)`` and ``(3, 5)`` become ``(1, 5)``; ``(1, 4)`` and ``(2, 3)``
    become ``(1, 4)``. The input list is not mutated. Empty input returns
    ``[]``. Raises ``ValueError`` for any interval with ``start >= end``.
    """
    cleaned = [_validate(interval) for interval in intervals]
    cleaned.sort(key=lambda pair: (pair[0], pair[1]))

    merged: list[tuple[int, int]] = []
    for start, end in cleaned:
        if merged and start <= merged[-1][1]:
            if end > merged[-1][1]:
                merged[-1] = (merged[-1][0], end)
        else:
            merged.append((start, end))
    return merged


def find_free_slots(
    busy: list[tuple[int, int]],
    day_start: int,
    day_end: int,
    min_minutes: int,
) -> list[tuple[int, int]]:
    """Return free gaps inside ``[day_start, day_end)`` of length >= ``min_minutes``.

    Busy intervals may overlap, be unsorted, or extend outside the day; they
    are clipped to the day and intervals entirely outside are ignored. The
    result is sorted by start.
    """
    if day_start >= day_end:
        return []

    clipped: list[tuple[int, int]] = []
    for start, end in busy:
        low = max(start, day_start)
        high = min(end, day_end)
        if low < high:
            clipped.append((low, high))

    merged = merge_intervals(clipped)

    free: list[tuple[int, int]] = []
    cursor = day_start
    for start, end in merged:
        if cursor < start:
            if start - cursor >= min_minutes:
                free.append((cursor, start))
        if end > cursor:
            cursor = end
    if cursor < day_end and day_end - cursor >= min_minutes:
        free.append((cursor, day_end))
    return free


def max_concurrent(intervals: list[tuple[int, int]]) -> int:
    """Return the maximum number of intervals overlapping at one instant.

    Touching intervals such as ``(1, 3)`` and ``(3, 5)`` do not overlap.
    Empty input returns ``0``.
    """
    events: list[tuple[int, int]] = []
    for interval in intervals:
        start, end = _validate(interval)
        events.append((start, 1))
        events.append((end, -1))

    events.sort(key=lambda item: (item[0], item[1]))

    current = 0
    best = 0
    for _, delta in events:
        current += delta
        if current > best:
            best = current
    return best
