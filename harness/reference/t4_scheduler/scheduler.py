def _validate(intervals):
    for s, e in intervals:
        if s >= e:
            raise ValueError(f"invalid interval {(s, e)}")


def merge_intervals(intervals):
    _validate(intervals)
    out = []
    for s, e in sorted(intervals):
        if out and s <= out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], e))
        else:
            out.append((s, e))
    return out


def find_free_slots(busy, day_start, day_end, min_minutes):
    clipped = []
    for s, e in busy:
        s2, e2 = max(s, day_start), min(e, day_end)
        if s2 < e2:
            clipped.append((s2, e2))
    merged = merge_intervals(clipped)
    free, cursor = [], day_start
    for s, e in merged:
        if s - cursor >= min_minutes:
            free.append((cursor, s))
        cursor = max(cursor, e)
    if day_end - cursor >= min_minutes:
        free.append((cursor, day_end))
    return free


def max_concurrent(intervals):
    events = []
    for s, e in intervals:
        events.append((s, 1))
        events.append((e, -1))
    events.sort(key=lambda x: (x[0], x[1]))
    cur = best = 0
    for _, d in events:
        cur += d
        best = max(best, cur)
    return best
