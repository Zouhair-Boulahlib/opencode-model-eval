def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    for start, end in intervals:
        if start >= end:
            raise ValueError(f"invalid interval: ({start}, {end})")

    merged: list[tuple[int, int]] = []
    for start, end in sorted(intervals):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def find_free_slots(
    busy: list[tuple[int, int]],
    day_start: int,
    day_end: int,
    min_minutes: int,
) -> list[tuple[int, int]]:
    if day_end <= day_start:
        return []

    clipped: list[tuple[int, int]] = []
    for start, end in busy:
        start = max(start, day_start)
        end = min(end, day_end)
        if start < end:
            clipped.append((start, end))

    clipped.sort()
    merged: list[tuple[int, int]] = []
    for start, end in clipped:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))

    gaps: list[tuple[int, int]] = []
    cursor = day_start
    for start, end in merged:
        if start > cursor:
            gaps.append((cursor, start))
        cursor = max(cursor, end)
    if cursor < day_end:
        gaps.append((cursor, day_end))

    return [(start, end) for start, end in gaps if end - start >= min_minutes]


def max_concurrent(intervals: list[tuple[int, int]]) -> int:
    events: list[tuple[int, int]] = []
    for start, end in intervals:
        if start < end:
            events.append((start, 1))
            events.append((end, -1))

    events.sort(key=lambda event: (event[0], event[1]))

    current = 0
    best = 0
    for _, delta in events:
        current += delta
        best = max(best, current)
    return best
