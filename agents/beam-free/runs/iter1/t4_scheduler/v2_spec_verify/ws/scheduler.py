def merge_intervals(intervals):
    for s, e in intervals:
        if s >= e:
            raise ValueError("invalid interval")
    sorted_iv = sorted(intervals)
    merged = []
    for s, e in sorted_iv:
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
        if cs < ce and cs < day_end and ce > day_start:
            clipped.append((cs, ce))
    merged = merge_intervals(clipped) if clipped else []
    free = []
    cur = day_start
    for s, e in merged:
        if s > cur:
            gap = (cur, s)
            if gap[1] - gap[0] >= min_minutes:
                free.append(gap)
        cur = max(cur, e)
    if cur < day_end:
        gap = (cur, day_end)
        if gap[1] - gap[0] >= min_minutes:
            free.append(gap)
    return free


def max_concurrent(intervals):
    for s, e in intervals:
        if s >= e:
            raise ValueError("invalid interval")
    events = []
    for s, e in intervals:
        events.append((s, 1))
        events.append((e, -1))
    # at same time, ends (-1) before starts (+1): sort by time then delta
    events.sort(key=lambda x: (x[0], x[1]))
    cur = 0
    best = 0
    for _, d in events:
        cur += d
        if cur > best:
            best = cur
    return best