"""Scheduler utilities for integer-minute time intervals.

Intervals are half-open [start, end) pairs of integers, where the unit is
minutes. Back-to-back intervals (e.g. (0, 30) and (30, 60)) are considered
non-overlapping and are merged into one interval.
"""


def merge_intervals(intervals):
    """Merge overlapping or touching intervals.

    Accepts any iterable of (start, end) pairs with start <= end and returns
    a sorted list of disjoint (start, end) tuples covering the same time.
    """
    normalized = sorted((int(s), int(e)) for s, e in intervals)
    if not normalized:
        return []
    merged = [normalized[0]]
    for start, end in normalized[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end:
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))
    return merged


def find_free_slots(busy, day_start, day_end, min_minutes):
    """Return free gaps of at least min_minutes within [day_start, day_end).

    Busy intervals are clipped to the day window before gaps are computed.
    Returns a list of (start, end) tuples, sorted chronologically.
    """
    if day_end <= day_start:
        return []
    clipped = []
    for start, end in busy:
        start = max(int(start), day_start)
        end = min(int(end), day_end)
        if end > start:
            clipped.append((start, end))
    merged = merge_intervals(clipped)
    free = []
    cursor = day_start
    for start, end in merged:
        if start - cursor >= min_minutes:
            free.append((cursor, start))
        cursor = max(cursor, end)
    if day_end - cursor >= min_minutes:
        free.append((cursor, day_end))
    return free


def max_concurrent(intervals):
    """Return the maximum number of intervals overlapping at any minute.

    Uses a sweep line over start/end events; because intervals are half-open,
    an interval ending at minute t does not overlap one starting at t.
    Degenerate intervals with end <= start are ignored.
    """
    events = []
    for start, end in intervals:
        if end > start:
            events.append((int(start), 1))
            events.append((int(end), -1))
    events.sort()
    current = peak = 0
    for _, delta in events:
        current += delta
        if current > peak:
            peak = current
    return peak
