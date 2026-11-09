def merge_intervals(intervals):
    for s, e in intervals:
        if s >= e:
            raise ValueError("invalid interval")
    merged = []
    for s, e in sorted(intervals):
        if merged and s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))
    return merged


def find_free_slots(busy, day_start, day_end, min_minutes):
    clipped = []
    for s, e in busy:
        if s >= e:
            raise ValueError("invalid interval")
        cs = max(s, day_start)
        ce = min(e, day_end)
        if cs < ce:
            clipped.append((cs, ce))
    merged = merge_intervals(clipped) if clipped else []
    free = []
    cur = day_start
    for s, e in merged:
        if s > cur and s - cur >= min_minutes:
            free.append((cur, s))
        cur = max(cur, e)
    if day_end > cur and day_end - cur >= min_minutes:
        free.append((cur, day_end))
    return free


def max_concurrent(intervals):
    for s, e in intervals:
        if s >= e:
            raise ValueError("invalid interval")
    events = []
    for s, e in intervals:
        events.append((s, 1))
        events.append((e, -1))
    events.sort(key=lambda x: (x[0], x[1]))
    cur = 0
    best = 0
    for _, delta in events:
        cur += delta
        if cur > best:
            best = cur
    return best
