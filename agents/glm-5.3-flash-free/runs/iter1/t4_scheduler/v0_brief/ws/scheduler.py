"""Utilities for working with integer-minute time intervals.

All intervals are represented as (start, end) tuples of integer minutes,
half-open: [start, end).
"""


def merge_intervals(intervals):
    """Merge overlapping or touching intervals.

    Args:
        intervals: iterable of (start, end) integer-minute tuples.

    Returns:
        Sorted list of non-overlapping (start, end) tuples.
    """
    if not intervals:
        return []
    intervals = sorted((int(s), int(e)) for s, e in intervals)
    merged = [list(intervals[0])]
    for start, end in intervals[1:]:
        if start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return [tuple(m) for m in merged]


def find_free_slots(busy, day_start, day_end, min_minutes):
    """Find free gaps of at least min_minutes within [day_start, day_end).

    Args:
        busy: iterable of (start, end) busy intervals.
        day_start: start of the day window in minutes.
        day_end: end of the day window in minutes.
        min_minutes: minimum length of a free slot, in minutes.

    Returns:
        Sorted list of (start, end) free-slot tuples.
    """
    day_start, day_end = int(day_start), int(day_end)
    min_minutes = int(min_minutes)
    if day_end <= day_start:
        return []
    merged = merge_intervals(b for b in merge_intervals(busy) if b[0] < day_end and b[1] > day_start)
    free = []
    cursor = day_start
    for start, end in merged:
        if start - cursor >= min_minutes:
            free.append((cursor, start))
        cursor = max(cursor, end)
        if cursor >= day_end:
            return free
    if day_end - cursor >= min_minutes:
        free.append((cursor, day_end))
    return free


def max_concurrent(intervals):
    """Return the maximum number of intervals overlapping at any time.

    Args:
        intervals: iterable of (start, end) integer-minute tuples.

    Returns:
        Integer maximum concurrency (0 for an empty input).
    """
    events = []
    for start, end in intervals:
        events.append((start, 1))
        events.append((end, -1))
    if not events:
        return 0
    events.sort(key=lambda e: (e[0], e[1]))
    current = peak = 0
    for _, delta in events:
        current += delta
        peak = max(peak, current)
    return peak
