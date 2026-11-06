"""Integer-minute interval scheduling helpers.

Intervals are ``(start, end)`` pairs of integer minutes and are treated as
half-open ranges: ``start`` is included, ``end`` is not.  Consequently an
interval ending at minute 10 and one starting at minute 10 do not overlap.
"""

from typing import Iterable, List, Sequence, Tuple

Interval = Tuple[int, int]


def _validate(intervals: Iterable[Sequence[int]]) -> List[Interval]:
    result: List[Interval] = []
    for interval in intervals:
        start, end = interval
        if start > end:
            raise ValueError(f"interval start must not exceed end: {interval!r}")
        result.append((start, end))
    return result


def merge_intervals(intervals: Iterable[Sequence[int]]) -> List[Interval]:
    """Merge overlapping and touching intervals.

    >>> merge_intervals([(1, 3), (2, 6), (8, 10)])
    [(1, 6), (8, 10)]
    """
    items = sorted(_validate(intervals))
    merged: List[Interval] = []
    for start, end in items:
        if merged and start <= merged[-1][1]:
            prev_start, prev_end = merged[-1]
            merged[-1] = (prev_start, max(prev_end, end))
        else:
            merged.append((start, end))
    return merged


def find_free_slots(
    busy: Iterable[Sequence[int]],
    day_start: int,
    day_end: int,
    min_minutes: int,
) -> List[Interval]:
    """Return free gaps within ``[day_start, day_end)`` lasting at least ``min_minutes``.

    Busy intervals are clipped to the day and overlapping ones are merged first.
    """
    if day_start >= day_end or min_minutes <= 0:
        if min_minutes <= 0 and day_start < day_end:
            return [(day_start, day_end)]
        return []

    clipped = []
    for start, end in _validate(busy):
        start = max(start, day_start)
        end = min(end, day_end)
        if start < end:
            clipped.append((start, end))

    free: List[Interval] = []
    cursor = day_start
    for start, end in merge_intervals(clipped):
        if start > cursor and start - cursor >= min_minutes:
            free.append((cursor, start))
        cursor = max(cursor, end)

    if day_end - cursor >= min_minutes:
        free.append((cursor, day_end))
    return free


def max_concurrent(intervals: Iterable[Sequence[int]]) -> int:
    """Return the maximum number of intervals overlapping at any instant.

    Half-open semantics mean an interval ending when another begins does not
    increase the count.  Zero-length intervals occupy no time and are ignored.
    """
    events = []
    for start, end in _validate(intervals):
        if start == end:
            continue
        events.append((start, 1))
        events.append((end, -1))

    events.sort(key=lambda event: (event[0], event[1]))
    current = 0
    best = 0
    for _, delta in events:
        current += delta
        best = max(best, current)
    return best
