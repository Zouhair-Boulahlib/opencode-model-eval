def _interval_type(intervals):
    if intervals:
        first = intervals[0]
        if isinstance(first, tuple):
            return tuple
    return list


def merge_intervals(intervals):
    if not intervals:
        return []

    item_type = _interval_type(intervals)
    sorted_intervals = sorted(intervals, key=lambda x: (x[0], x[1]))
    merged = [list(sorted_intervals[0])]

    for start, end in sorted_intervals[1:]:
        if start <= merged[-1][1]:
            if end > merged[-1][1]:
                merged[-1][1] = end
        else:
            merged.append([start, end])

    if item_type is tuple:
        return [tuple(interval) for interval in merged]
    return [list(interval) for interval in merged]


def find_free_slots(busy, day_start, day_end, min_minutes):
    item_type = _interval_type(busy) if busy else list

    clipped = []
    for start, end in busy:
        start = max(start, day_start)
        end = min(end, day_end)
        if start < end:
            clipped.append((start, end))

    merged = merge_intervals(clipped)

    free = []
    current = day_start
    for start, end in merged:
        if start > current and start - current >= min_minutes:
            slot = [current, start]
            free.append(tuple(slot) if item_type is tuple else slot)
        current = max(current, end)

    if day_end > current and day_end - current >= min_minutes:
        slot = [current, day_end]
        free.append(tuple(slot) if item_type is tuple else slot)

    return free


def max_concurrent(intervals):
    events = []
    for start, end in intervals:
        events.append((start, 1))
        events.append((end, -1))

    events.sort(key=lambda event: (event[0], event[1]))

    current = 0
    maximum = 0
    for _, delta in events:
        current += delta
        if current > maximum:
            maximum = current

    return maximum
