"""Utilities for integer-minute scheduling intervals.

Convention
----------
All intervals are half-open ``[start, end)`` ranges of integer minutes:
minute ``start`` is included, minute ``end`` is excluded.  The duration of
``(a, b)`` is ``b - a`` minutes.  Zero-length intervals (``start == end``)
are empty and are ignored; ``end < start`` is invalid and raises
``ValueError``.
"""

__all__ = ["merge_intervals", "find_free_slots", "max_concurrent"]


def _check_interval(interval):
    start, end = interval
    if end < start:
        raise ValueError(f"invalid interval {interval!r}: end < start")
    return start, end


def merge_intervals(intervals):
    """Return the sorted union of ``intervals`` as minimal disjoint blocks.

    Overlapping *and* touching intervals are merged: under half-open
    semantics the union of ``(1, 4)`` and ``(4, 6)`` is the single block
    ``(1, 6)``.  Empty intervals are dropped.  The input is not modified.
    """
    cleaned = []
    for raw in intervals:
        start, end = _check_interval(raw)
        if start < end:
            cleaned.append((start, end))
    cleaned.sort()
    merged = []
    for start, end in cleaned:
        if merged and start <= merged[-1][1]:
            if end > merged[-1][1]:
                merged[-1] = (merged[-1][0], end)
        else:
            merged.append((start, end))
    return merged


def find_free_slots(busy, day_start, day_end, min_minutes):
    """Return free gaps inside ``[day_start, day_end)``.

    ``busy`` may be unsorted and overlapping; it is merged first.  Busy
    time outside the day is ignored.  A gap qualifies when its length is
    at least ``min_minutes`` (zero-length gaps never qualify).
    ``min_minutes`` must be >= 0 and ``day_end`` >= ``day_start``.
    """
    if day_end < day_start:
        raise ValueError(f"invalid day: end {day_end} < start {day_start}")
    if min_minutes < 0:
        raise ValueError(f"min_minutes must be >= 0, got {min_minutes}")

    slots = []
    cursor = day_start
    for start, end in merge_intervals(busy):
        if start >= day_end:
            break
        if end <= cursor:
            continue
        if start > cursor and start - cursor >= min_minutes:
            slots.append((cursor, start))
        if end > cursor:
            cursor = end
        if cursor >= day_end:
            break
    if cursor < day_end and day_end - cursor >= min_minutes:
        slots.append((cursor, day_end))
    return slots


def max_concurrent(intervals):
    """Return the peak number of simultaneously active intervals.

    Uses a sweep line over interval endpoints.  Because intervals are
    half-open, an interval ending at minute ``t`` does not overlap one
    starting at ``t``, so end events are applied before start events at
    equal times.  Empty intervals are ignored; returns 0 for no overlap.
    """
    events = []
    for raw in intervals:
        start, end = _check_interval(raw)
        if start == end:
            continue
        events.append((start, 1))
        events.append((end, -1))
    events.sort(key=lambda event: (event[0], event[1]))
    current = best = 0
    for _, delta in events:
        current += delta
        if current > best:
            best = current
    return best
