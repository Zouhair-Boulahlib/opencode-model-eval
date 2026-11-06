def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    for start, end in intervals:
        if start >= end:
            raise ValueError(f"invalid interval: ({start}, {end})")
    if not intervals:
        return []
    sorted_intervals = sorted(intervals)
    merged = [sorted_intervals[0]]
    for start, end in sorted_intervals[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end:
            if end > last_end:
                merged[-1] = (last_start, end)
        else:
            merged.append((start, end))
    return merged


def find_free_slots(
    busy: list[tuple[int, int]],
    day_start: int,
    day_end: int,
    min_minutes: int,
) -> list[tuple[int, int]]:
    if day_start >= day_end:
        return []
    clipped = []
    for start, end in busy:
        c_start = max(start, day_start)
        c_end = min(end, day_end)
        if c_start < c_end:
            clipped.append((c_start, c_end))
    merged = merge_intervals(clipped)
    slots = []
    current = day_start
    for start, end in merged:
        if start > current:
            slots.append((current, start))
        current = max(current, end)
    if current < day_end:
        slots.append((current, day_end))
    return [(s, e) for s, e in slots if e - s >= min_minutes]


def max_concurrent(intervals: list[tuple[int, int]]) -> int:
    events = []
    for start, end in intervals:
        events.append((start, 1))
        events.append((end, -1))
    events.sort(key=lambda e: (e[0], e[1]))
    count = 0
    peak = 0
    for _, delta in events:
        count += delta
        if count > peak:
            peak = count
    return peak
