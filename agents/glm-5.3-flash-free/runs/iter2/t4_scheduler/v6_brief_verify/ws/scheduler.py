"""Scheduler utilities for integer-minute time intervals.

Intervals are represented as (start, end) tuples of integer minutes and
treated as half-open ranges [start, end), so an interval ending at minute
`t` and another starting at minute `t` do not overlap (they are however
adjacent and get merged by merge_intervals).
"""


def _valid(intervals):
    return [(s, e) for (s, e) in intervals if s < e]


def merge_intervals(intervals):
    """Merge overlapping or adjacent intervals.

    Returns a new sorted list of (start, end) tuples where no two
    intervals overlap or touch.
    """
    items = sorted(_valid(intervals))
    merged = []
    for start, end in items:
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return [(s, e) for s, e in merged]


def find_free_slots(busy, day_start, day_end, min_minutes):
    """Find free gaps of at least `min_minutes` inside [day_start, day_end].

    `busy` is a list of intervals which may be unsorted, overlapping,
    adjacent, or lie (partially) outside the day range. Returns a list of
    (start, end) tuples sorted by start time.
    """
    if day_end <= day_start:
        return []
    clipped = []
    for start, end in merge_intervals(busy):
        s, e = max(start, day_start), min(end, day_end)
        if s < e:
            clipped.append((s, e))
    slots = []
    cursor = day_start
    for s, e in clipped:
        if s - cursor >= min_minutes:
            slots.append((cursor, s))
        cursor = max(cursor, e)
    if day_end - cursor >= min_minutes:
        slots.append((cursor, day_end))
    return slots


def max_concurrent(intervals):
    """Return the maximum number of intervals active at the same instant.

    With half-open intervals [start, end), an interval ending at minute t
    and one starting at minute t are never both counted as active.
    """
    events = []
    for start, end in _valid(intervals):
        events.append((start, 1))
        events.append((end, -1))
    best = current = 0
    for _, delta in sorted(events, key=lambda ev: (ev[0], ev[1])):
        current += delta
        best = max(best, current)
    return best
