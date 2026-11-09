def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not intervals:
        return []
    for start, end in intervals:
        if start >= end:
            raise ValueError(f"invalid interval: ({start}, {end})")
    sorted_intervals = sorted(intervals)
    merged: list[list[int]] = [[sorted_intervals[0][0], sorted_intervals[0][1]]]
    for start, end in sorted_intervals[1:]:
        last = merged[-1]
        if start <= last[1]:
            last[1] = max(last[1], end)
        else:
            merged.append([start, end])
    return [(start, end) for start, end in merged]


def find_free_slots(
    busy: list[tuple[int, int]],
    day_start: int,
    day_end: int,
    min_minutes: int,
) -> list[tuple[int, int]]:
    clipped: list[tuple[int, int]] = []
    for start, end in busy:
        s = max(start, day_start)
        e = min(end, day_end)
        if s < e:
            clipped.append((s, e))
    merged = merge_intervals(clipped) if clipped else []
    free: list[tuple[int, int]] = []
    cursor = day_start
    for start, end in merged:
        if cursor < start and start - cursor >= min_minutes:
            free.append((cursor, start))
        cursor = max(cursor, end)
    if day_end > cursor and day_end - cursor >= min_minutes:
        free.append((cursor, day_end))
    return free


def max_concurrent(intervals: list[tuple[int, int]]) -> int:
    events: list[tuple[int, int]] = []
    for start, end in intervals:
        events.append((start, 1))
        events.append((end, -1))
    events.sort(key=lambda ev: (ev[0], ev[1]))
    current = 0
    best = 0
    for _, delta in events:
        current += delta
        if current > best:
            best = current
    return best
