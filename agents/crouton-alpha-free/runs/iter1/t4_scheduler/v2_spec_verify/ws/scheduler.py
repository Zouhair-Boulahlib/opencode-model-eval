def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    for start, end in intervals:
        if start >= end:
            raise ValueError("invalid interval: start >= end")
    if not intervals:
        return []
    sorted_intervals = sorted(intervals, key=lambda x: (x[0], x[1]))
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
    if day_end <= day_start:
        return []
    clipped: list[tuple[int, int]] = []
    for start, end in busy:
        s = max(start, day_start)
        e = min(end, day_end)
        if s < e:
            clipped.append((s, e))
    if not clipped:
        if day_end - day_start >= min_minutes:
            return [(day_start, day_end)]
        return []
    merged = merge_intervals(clipped)
    free: list[tuple[int, int]] = []
    cursor = day_start
    for start, end in merged:
        if start > cursor and start - cursor >= min_minutes:
            free.append((cursor, start))
        if end > cursor:
            cursor = end
    if day_end > cursor and day_end - cursor >= min_minutes:
        free.append((cursor, day_end))
    return free


def max_concurrent(intervals: list[tuple[int, int]]) -> int:
    if not intervals:
        return 0
    events: list[tuple[int, int]] = []
    for start, end in intervals:
        if start >= end:
            continue
        events.append((start, 1))
        events.append((end, -1))
    events.sort(key=lambda x: (x[0], x[1]))
    current = 0
    best = 0
    for _, delta in events:
        current += delta
        if current > best:
            best = current
    return best
