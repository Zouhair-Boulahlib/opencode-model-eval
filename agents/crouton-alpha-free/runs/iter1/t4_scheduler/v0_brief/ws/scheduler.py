"""Scheduler utilities for integer-minute time intervals.

Intervals are half-open [start, end) in integer minutes: an interval
ending at minute 10 and another starting at minute 10 do not overlap.
"""


def _clean(intervals):
    cleaned = []
    for interval in intervals or []:
        if not interval:
            continue
        start, end = int(interval[0]), int(interval[1])
        if end > start:
            cleaned.append((start, end))
    cleaned.sort()
    return cleaned


def merge_intervals(intervals):
    """Merge overlapping or touching intervals.

    Args:
        intervals: Iterable of [start, end] pairs.

    Returns:
        Sorted list of merged [start, end] lists.
    """
    cleaned = _clean(intervals)
    if not cleaned:
        return []

    merged = [[cleaned[0][0], cleaned[0][1]]]
    for start, end in cleaned[1:]:
        last = merged[-1]
        if start <= last[1]:
            if end > last[1]:
                last[1] = end
        else:
            merged.append([start, end])
    return merged


def find_free_slots(busy, day_start, day_end, min_minutes):
    """Find free slots within [day_start, day_end).

    Args:
        busy: Iterable of [start, end] pairs.
        day_start: Start of the day window (inclusive).
        day_end: End of the day window (exclusive).
        min_minutes: Minimum free duration to return.

    Returns:
        Sorted list of [start, end] free slots with duration >= min_minutes.
    """
    day_start, day_end, min_minutes = int(day_start), int(day_end), int(min_minutes)
    if day_end <= day_start or min_minutes < 0:
        return []

    clipped = []
    for start, end in merge_intervals(busy):
        start, end = max(start, day_start), min(end, day_end)
        if end > start:
            clipped.append([start, end])

    free = []
    cursor = day_start
    for start, end in clipped:
        if start > cursor and start - cursor >= min_minutes:
            free.append([cursor, start])
        cursor = max(cursor, end)
    if day_end > cursor and day_end - cursor >= min_minutes:
        free.append([cursor, day_end])
    return free


def max_concurrent(intervals):
    """Return the maximum number of overlapping intervals.

    Intervals are half-open, so end events at a minute are processed
    before start events at the same minute.
    """
    events = []
    for start, end in _clean(intervals):
        events.append((start, 1))
        events.append((end, -1))
    events.sort(key=lambda event: (event[0], event[1]))

    current = best = 0
    for _, delta in events:
        current += delta
        if current > best:
            best = current
    return best
