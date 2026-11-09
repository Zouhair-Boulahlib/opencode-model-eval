#!/usr/bin/env python3
"""Flag evaluation runs whose wall-clock window overlaps a laptop sleep or modern-standby period.

Wall-clock timers keep counting while a laptop sleeps, so a run that spans a standby period can show an
inflated duration or a false timeout. This reads the Windows power log (Kernel-Power events 42/107 =
sleep/resume, 506/507 = modern standby enter/exit), rebuilds the standby periods, and compares them with
every run's [finished - wall_s, finished] window.

    python harness/standby_check.py [--since 2026-11-05] [--min-minutes 1]

Writes results/standby_check.csv (one row per run) and prints the overlapping runs. Windows only.
"""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PS = r"""
$ev = Get-WinEvent -FilterHashtable @{LogName='System'; StartTime=[datetime]'%s'; Id=@(42,107,506,507)} -ErrorAction SilentlyContinue |
  Where-Object { $_.ProviderName -eq 'Microsoft-Windows-Kernel-Power' } | Sort-Object TimeCreated
$ev | ForEach-Object { '{0:yyyy-MM-ddTHH:mm:ss} {1}' -f $_.TimeCreated, $_.Id }
"""


def standby_periods(since: str, min_minutes: float) -> list[tuple[datetime, datetime]]:
    out = subprocess.run(["powershell", "-NoProfile", "-Command", PS % since], capture_output=True, text=True,
                         encoding="utf-8", errors="replace").stdout
    periods, start = [], None
    for line in out.splitlines():
        try:
            stamp, ev_id = line.split()
        except ValueError:
            continue
        t = datetime.fromisoformat(stamp)
        if ev_id in ("42", "506"):
            start = start or t
        elif start is not None:
            if (t - start).total_seconds() >= min_minutes * 60:
                periods.append((start, t))
            start = None
    return periods


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2026-11-05")
    ap.add_argument("--min-minutes", type=float, default=1.0)
    a = ap.parse_args()
    periods = standby_periods(a.since, a.min_minutes)
    print(f"{len(periods)} standby/sleep periods of at least {a.min_minutes} min since {a.since}")

    rows = []
    for p in sorted(ROOT.glob("agents/*/runs/**/result.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        if not d.get("finished"):
            continue
        end = datetime.fromisoformat(d["finished"])
        start = end - timedelta(seconds=d.get("wall_s") or 0)
        overlap = sum(max(0.0, (min(end, b) - max(start, s)).total_seconds()) for s, b in periods)
        rows.append({"slug": d["slug"], "iteration": d["iteration"], "task": d["task"], "variant": d["variant"],
                     "rep": d.get("rep", 0), "start": start.isoformat(timespec="seconds"), "wall_s": d.get("wall_s"),
                     "standby_overlap_s": round(overlap), "timed_out": d.get("timed_out"), "score": d.get("score")})
    hit = [r for r in rows if r["standby_overlap_s"] > 0]
    print(f"{len(rows)} runs checked, {len(hit)} overlap standby "
          f"({sum(1 for r in hit if r['timed_out'])} of them timed out; {sum(1 for r in rows if r['timed_out'])} timeouts in total)")
    for r in sorted(hit, key=lambda r: -r["standby_overlap_s"]):
        print(f"  {r['slug']} iter{r['iteration']} {r['task']} {r['variant']} start {r['start']} "
              f"wall {r['wall_s']}s standby {r['standby_overlap_s']}s timeout={r['timed_out']} score={r['score']}")
    out = ROOT / "results" / "standby_check.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]) if rows else ["slug"])
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: r["start"]))
    print(f"written {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
