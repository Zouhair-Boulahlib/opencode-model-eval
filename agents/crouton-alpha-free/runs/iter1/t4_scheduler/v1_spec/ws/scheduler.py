"""Interval scheduling utilities."""

def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    for start, end in intervals:
        if start >= end:
            raise ValueError(f"invalid interval: ({start}, {end})")
    if not intervals:
        return []
    sorted_intervals = sorted(intervals)
    merged: list[tuple[int, int]] = []
    cur_start, cur_end = sorted_intervals[0]
    for start, end in sorted_intervals[1:]:
        if start <= cur_end:
            if end > cur_end:
                cur_end = end
        else:
            merged.append((cur_start, cur_end))
            cur_start, cur_end = start, end
    merged.append((cur_start, cur_end))
    return merged


def find_free_slots(busy: list[tuple[int, int]], day_start: int, day_end: int, min_minutes: int) -> list[tuple[int, int]]:
    for start, end in busy:
        if start >= end:
            raise ValueError(f"invalid interval: ({start}, {end})")
    if day_start >= day_end:
        return []
    clipped: list[tuple[int, int]] = []
    for start, end in busy:
        if end <= day_start or start >= day_end:
            continue
        clipped.append((max(start, day_start), min(end, day_end)))
    merged = merge_intervals(clipped)
    free: list[tuple[int, int]] = []
    cursor = day_start
    for start, end in merged:
        if cursor < start and start - cursor >= min_minutes:
            free.append((cursor, start))
        if end > cursor:
            cursor = end
    if cursor < day_end and day_end - cursor >= min_minutes:
        free.append((cursor, day_end))
    return free


def max_concurrent(intervals: list[tuple[int, int]]) -> int:
    for start, end in intervals:
        if start >= end:
            raise ValueError(f"invalid interval: ({start}, {end})")
    if not intervals:
        return 0
    events: list[tuple[int, int]] = []
    for start, end in intervals:
        events.append((start, 1))
        events.append((end, -1))
    events.sort(key=lambda e: (e[0], e[1]))
    current = 0
    maximum = 0
    for _, delta in events:
        current += delta
        if current > maximum:
            maximum = current
    return maximum
