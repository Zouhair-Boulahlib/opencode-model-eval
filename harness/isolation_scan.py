#!/usr/bin/env python3
"""Flag every tool call that reached outside the run's own workspace (ws/).

qc_scan.py looks for known hidden-test markers. This scan is stricter: any tool input that names a path
outside the run's ws/ folder (an absolute path elsewhere, or a '..' parent reference) is reported, split
into READS (a read tool that completed: file content reached the model) and LISTINGS (bash/glob/grep/list
calls: names, and for grep matching lines, reached the model).

    python harness/isolation_scan.py [--iterations iter1 iter2 iter3]

Writes results/isolation_scan.csv (one row per run that reached outside).
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ABS = re.compile(r"[A-Za-z]:/[^\"'|<>\n]*")


REPO_PREFIX = re.compile(r"[A-Za-z]:/Users/[^/]+/Desktop/eval opencode/?", re.IGNORECASE)
PATH_KEYS = ("filePath", "path", "workdir", "command", "pattern", "include")


def outside(inp: dict, ws_rel: str) -> bool:
    """True when a path-carrying field names something outside ws/ (absolute elsewhere, or a '..' parent step)."""
    for key in PATH_KEYS:
        val = inp.get(key)
        if not isinstance(val, str):
            continue
        t = val.replace("\\", "/").replace("\\", "/")
        if re.search(r"(^|[\s\"'/=])\.\.(/|\"|'|\s|$)", t):
            return True
        for m in ABS.findall(t) + re.findall(r"(?:^|\s)(/agents/[^\s\"']*)", t):
            rel = REPO_PREFIX.sub("", m).lstrip("/")
            if not rel.lower().startswith(ws_rel.lower()):
                return True
    return False


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--iterations", nargs="*", default=["iter1", "iter2", "iter3"])
    a = ap.parse_args()
    scores = {}
    with open(ROOT / "results" / "summary.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            scores[r["run_dir"].replace("\\", "/")] = f"{r['passed']}/{r['total']}"
    out_rows = []
    for p in sorted(glob.glob(str(ROOT / "agents" / "*" / "runs" / "*" / "*" / "*" / "events.jsonl"))):
        run_abs = Path(p).parent
        rel = run_abs.relative_to(ROOT).as_posix()
        if rel.split("/")[3] not in a.iterations:
            continue
        ws_rel = rel + "/ws"
        reads, listings = [], []
        for line in open(p, encoding="utf-8", errors="replace"):
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            part = ev.get("part") or {}
            if part.get("type") != "tool":
                continue
            st = part.get("state") or {}
            raw = st.get("input") or {}
            inp = json.dumps(raw, ensure_ascii=False)
            if not isinstance(raw, dict) or not outside(raw, ws_rel):
                continue
            ok = st.get("status") == "completed"
            target = re.sub(r"[A-Za-z]:/Users/[^/]+/Desktop/eval opencode/", "", inp.replace("\\\\", "/"))[:140]
            entry = f"{part.get('tool')}{'' if ok else ' (blocked)'} {target}"
            (reads if part.get("tool") == "read" and ok else listings).append(entry)
        if reads or listings:
            hidden_read = any("hidden" in r for r in reads)
            out_rows.append({"run": rel, "score": scores.get(rel, "?"), "reads": len(reads), "listings": len(listings),
                             "read_hidden_test": hidden_read, "first_read": reads[0] if reads else "",
                             "first_listing": listings[0] if listings else ""})
            print(f"\n{rel}  score {scores.get(rel, '?')}  reads={len(reads)} listings={len(listings)}"
                  f"{'  HIDDEN TEST READ' if hidden_read else ''}")
            for r in reads[:6]:
                print("   READ ", r)
            for x in listings[:3]:
                print("   list ", x)
    print(f"\nruns reaching outside ws: {len(out_rows)}; of which read a hidden test: "
          f"{sum(r['read_hidden_test'] for r in out_rows)}")
    dest = ROOT / "results" / "isolation_scan.csv"
    with dest.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["run", "score", "reads", "listings", "read_hidden_test", "first_read", "first_listing"])
        w.writeheader()
        w.writerows(out_rows)
    print("written", dest.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
