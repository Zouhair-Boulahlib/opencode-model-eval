def merge_intervals(intervals):
    """Merge overlapping and contiguous [start, end) intervals."""
    valid = sorted((s, e) for s, e in intervals if e > s)
    if not valid:
        return []
    merged = [list(valid[0])]
    for start, end in valid[1:]:
        last = merged[-1]
        if start <= last[1]:
            if end > last[1]:
                last[1] = end
        else:
            merged.append([start, end])
    return [(s, e) for s, e in merged]


def find_free_slots(busy, day_start, day_end, min_minutes):
    """Return free [start, end) slots within the day, at least min_minutes long."""
    if day_end <= day_start:
        return []

    clipped = []
    for start, end in busy:
        start = max(start, day_start)
        end = min(end, day_end)
        if end > start:
            clipped.append((start, end))

    free = []
    cursor = day_start
    for start, end in merge_intervals(clipped):
        if start > cursor:
            free.append((cursor, start))
        cursor = max(cursor, end)
    if cursor < day_end:
        free.append((cursor, day_end))

    return [(s, e) for s, e in free if e - s >= min_minutes]


def max_concurrent(intervals):
    """Return the maximum number of overlapping [start, end) intervals."""
    events = []
    for start, end in intervals:
        if end > start:
            events.append((start, 1))
            events.append((end, -1))
    if not events:
        return 0

    events.sort(key=lambda ev: (ev[0], ev[1]))
    current = 0
    best = 0
    for _, delta in events:
        current += delta
        if current > best:
            best = current
    return best
