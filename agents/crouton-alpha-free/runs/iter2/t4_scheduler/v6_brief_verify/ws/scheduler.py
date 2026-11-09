"""Scheduler utilities for integer-minute intervals."""


def merge_intervals(intervals):
    """Merge overlapping or touching intervals, returned sorted."""
    if intervals is None:
        return []
    normalized = []
    for interval in intervals:
        start, end = interval
        if start > end:
            start, end = end, start
        normalized.append((start, end))
    if not normalized:
        return []
    normalized.sort(key=lambda item: (item[0], item[1]))
    merged = []
    cur_start, cur_end = normalized[0]
    for start, end in normalized[1:]:
        if start <= cur_end:
            if end > cur_end:
                cur_end = end
        else:
            merged.append((cur_start, cur_end))
            cur_start, cur_end = start, end
    merged.append((cur_start, cur_end))
    return merged


def find_free_slots(busy, day_start=0, day_end=1440, min_minutes=0):
    """Return free slots within [day_start, day_end) of at least min_minutes."""
    if day_end <= day_start:
        return []
    threshold = min_minutes if min_minutes is not None else 0
    clipped = []
    if busy:
        for interval in busy:
            start, end = interval
            if start > end:
                start, end = end, start
            start = max(start, day_start)
            end = min(end, day_end)
            if end > start:
                clipped.append((start, end))
    merged = merge_intervals(clipped)
    free = []
    cursor = day_start
    for start, end in merged:
        if start > cursor and start - cursor >= threshold:
            free.append((cursor, start))
        if end > cursor:
            cursor = end
    if day_end > cursor and day_end - cursor >= threshold:
        free.append((cursor, day_end))
    return free


def max_concurrent(intervals):
    """Return the maximum number of intervals overlapping at any point."""
    if not intervals:
        return 0
    events = []
    for interval in intervals:
        start, end = interval
        if start > end:
            start, end = end, start
        if start == end:
            continue
        events.append((start, 1))
        events.append((end, -1))
    if not events:
        return 0
    events.sort(key=lambda item: (item[0], item[1]))
    current = 0
    peak = 0
    for _, delta in events:
        current += delta
        if current > peak:
            peak = current
    return peak
