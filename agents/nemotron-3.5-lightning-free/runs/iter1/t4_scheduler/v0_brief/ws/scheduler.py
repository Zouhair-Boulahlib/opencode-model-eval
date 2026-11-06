def merge_intervals(intervals):
    if not intervals:
        return []
    sorted_intervals = sorted(intervals, key=lambda x: x[0])
    merged = [sorted_intervals[0][:]]
    for current in sorted_intervals[1:]:
        last = merged[-1]
        if current[0] <= last[1]:
            last[1] = max(last[1], current[1])
        else:
            merged.append(current[:])
    return merged


def find_free_slots(busy, day_start, day_end, min_minutes):
    merged = merge_intervals(busy)
    free = []
    current = day_start
    for start, end in merged:
        if start > current:
            slot_length = start - current
            if slot_length >= min_minutes:
                free.append([current, start])
        current = max(current, end)
    if day_end - current >= min_minutes:
        free.append([current, day_end])
    return free


def max_concurrent(intervals):
    if not intervals:
        return 0
    events = []
    for start, end in intervals:
        events.append((start, 1))
        events.append((end, -1))
    events.sort(key=lambda x: (x[0], x[1]))
    max_count = 0
    current = 0
    for _, delta in events:
        current += delta
        max_count = max(max_count, current)
    return max_count
