def _validate(intervals):
    for start, end in intervals:
        if start >= end:
            raise ValueError(f"invalid interval: ({start}, {end})")


def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    _validate(intervals)
    ordered = sorted(intervals)
    merged: list[tuple[int, int]] = []
    for start, end in ordered:
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
    _validate(busy)
    clipped = []
    for start, end in busy:
        start = max(start, day_start)
        end = min(end, day_end)
        if start < end:
            clipped.append((start, end))

    free: list[tuple[int, int]] = []
    cursor = day_start
    for start, end in merge_intervals(clipped):
        if start > cursor and start - cursor >= min_minutes:
            free.append((cursor, start))
        cursor = max(cursor, end)
    if day_end > cursor and day_end - cursor >= min_minutes:
        free.append((cursor, day_end))
    return free


def max_concurrent(intervals: list[tuple[int, int]]) -> int:
    _validate(intervals)
    events = []
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
