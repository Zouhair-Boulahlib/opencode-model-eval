def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    for start, end in intervals:
        if start >= end:
            raise ValueError(f"Invalid interval ({start}, {end}): start >= end")

    sorted_intervals = sorted(intervals, key=lambda iv: iv[0])
    merged: list[tuple[int, int]] = []
    for start, end in sorted_intervals:
        if merged and start <= merged[-1][1]:
            prev_start, prev_end = merged[-1]
            merged[-1] = (prev_start, max(prev_end, end))
        else:
            merged.append((start, end))
    return merged


def find_free_slots(busy: list[tuple[int, int]], day_start: int, day_end: int,
                    min_minutes: int) -> list[tuple[int, int]]:
    clipped = []
    for start, end in busy:
        s = max(start, day_start)
        e = min(end, day_end)
        if s < e:
            clipped.append((s, e))

    merged_busy = merge_intervals(clipped)

    free: list[tuple[int, int]] = []
    cursor = day_start
    for start, end in merged_busy:
        if start > cursor and start - cursor >= min_minutes:
            free.append((cursor, start))
        cursor = max(cursor, end)
    if cursor < day_end and day_end - cursor >= min_minutes:
        free.append((cursor, day_end))
    return free


def max_concurrent(intervals: list[tuple[int, int]]) -> int:
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
