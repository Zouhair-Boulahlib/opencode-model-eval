def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not intervals:
        return []
    
    for start, end in intervals:
        if start >= end:
            raise ValueError("interval start must be < end")
    
    sorted_intervals = sorted(intervals, key=lambda x: x[0])
    merged = [list(sorted_intervals[0])]
    
    for start, end in sorted_intervals[1:]:
        if start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    
    return [tuple(interval) for interval in merged]


def find_free_slots(busy: list[tuple[int, int]], day_start: int, day_end: int, min_minutes: int) -> list[tuple[int, int]]:
    if not busy:
        if day_end - day_start >= min_minutes:
            return [(day_start, day_end)]
        return []
    
    clipped = []
    for start, end in busy:
        clipped_start = max(start, day_start)
        clipped_end = min(end, day_end)
        if clipped_start < clipped_end:
            clipped.append((clipped_start, clipped_end))
    
    merged = merge_intervals(clipped)
    
    free = []
    current = day_start
    for start, end in merged:
        if start > current:
            if start - current >= min_minutes:
                free.append((current, start))
        current = max(current, end)
    
    if current < day_end:
        if day_end - current >= min_minutes:
            free.append((current, day_end))
    
    return free


def max_concurrent(intervals: list[tuple[int, int]]) -> int:
    if not intervals:
        return 0
    
    events = []
    for start, end in intervals:
        events.append((start, 1))
        events.append((end, -1))
    
    events.sort(key=lambda x: (x[0], x[1]))
    
    count = 0
    max_count = 0
    for _, delta in events:
        count += delta
        max_count = max(max_count, count)
    
    return max_count