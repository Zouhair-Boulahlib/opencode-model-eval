def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    for start, end in intervals:
        if start >= end:
            raise ValueError("interval start must be less than end")
    sorted_intervals = sorted(intervals)
    merged: list[tuple[int, int]] = []
    for start, end in sorted_intervals:
        if merged and start <= merged[-1][1]:
            last_start, last_end = merged[-1]
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))
    return merged


def find_free_slots(busy: list[tuple[int, int]], day_start: int, day_end: int, min_minutes: int) -> list[tuple[int, int]]:
    for start, end in busy:
        if start >= end:
            raise ValueError("interval start must be less than end")
    clipped = []
    for start, end in busy:
        s = max(start, day_start)
        e = min(end, day_end)
        if s < e:
            clipped.append((s, e))
    merged = merge_intervals(clipped)
    free: list[tuple[int, int]] = []
    cursor = day_start
    for start, end in merged:
        if start > cursor:
            gap_start = cursor
            gap_end = start
            if gap_end - gap_start >= min_minutes:
                free.append((gap_start, gap_end))
        cursor = max(cursor, end)
    if cursor < day_end:
        gap_start = cursor
        gap_end = day_end
        if gap_end - gap_start >= min_minutes:
            free.append((gap_start, gap_end))
    return free


def max_concurrent(intervals: list[tuple[int, int]]) -> int:
    for start, end in intervals:
        if start >= end:
            raise ValueError("interval start must be less than end")
    events: list[tuple[int, int]] = []
    for start, end in intervals:
        events.append((start, 1))
        events.append((end, -1))
    events.sort(key=lambda x: (x[0], x[1]))
    current = 0
    best = 0
    for time, delta in events:
        current += delta
        if current > best:
            best = current
    return best
