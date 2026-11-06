"""Pure scheduling helpers for interval arithmetic."""

from __future__ import annotations


def _validate(interval: tuple[int, int]) -> None:
    start, end = interval
    if start >= end:
        raise ValueError(f"invalid interval: {interval!r}")


def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Merge overlapping or touching intervals into a new sorted list."""
    for interval in intervals:
        _validate(interval)

    merged: list[tuple[int, int]] = []
    for start, end in sorted(intervals):
        if merged and start <= merged[-1][1]:
            prev_start, prev_end = merged[-1]
            merged[-1] = (prev_start, max(prev_end, end))
        else:
            merged.append((start, end))
    return merged


def find_free_slots(
    busy: list[tuple[int, int]],
    day_start: int,
    day_end: int,
    min_minutes: int,
) -> list[tuple[int, int]]:
    """Return free gaps within [day_start, day_end) of at least min_minutes."""
    if day_start >= day_end:
        return []

    clipped: list[tuple[int, int]] = []
    for start, end in busy:
        if end <= day_start or start >= day_end:
            continue
        clipped.append((max(start, day_start), min(end, day_end)))

    free: list[tuple[int, int]] = []
    cursor = day_start
    for start, end in merge_intervals(clipped):
        if start > cursor:
            free.append((cursor, start))
        cursor = max(cursor, end)
    if cursor < day_end:
        free.append((cursor, day_end))

    return [(start, end) for start, end in free if end - start >= min_minutes]


def max_concurrent(intervals: list[tuple[int, int]]) -> int:
    """Return the maximum number of intervals overlapping at one instant."""
    events: list[tuple[int, int]] = []
    for start, end in intervals:
        events.append((start, 1))
        events.append((end, -1))

    events.sort(key=lambda event: (event[0], event[1]))

    current = 0
    best = 0
    for _, delta in events:
        current += delta
        best = max(best, current)
    return best
