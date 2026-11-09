def merge_intervals(intervals):
    cleaned = [(start, end) for start, end in intervals if start < end]
    if not cleaned:
        return []

    cleaned.sort()
    merged = [cleaned[0]]

    for start, end in cleaned[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end:
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))

    return merged


def find_free_slots(busy, day_start, day_end, min_minutes):
    if day_end <= day_start:
        return []

    free = []
    cursor = day_start

    for start, end in merge_intervals(busy):
        if end <= day_start or start >= day_end:
            continue

        start = max(start, day_start)
        end = min(end, day_end)

        if start > cursor and start - cursor >= min_minutes:
            free.append((cursor, start))

        cursor = max(cursor, end)

    if day_end > cursor and day_end - cursor >= min_minutes:
        free.append((cursor, day_end))

    return free


def max_concurrent(intervals):
    events = []
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
