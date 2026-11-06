#!/usr/bin/env python3
"""Quality-control scan over all runs: result integrity and cross-run information leakage.

A model could in principle read another run's scoring artifacts (pytest_output.txt, junit.xml,
result.json) or the harness task folder (hidden tests) through bash. This scan lists every tool
call whose input references such paths and every tool output that contains hidden-test content.
"""
import glob
import json
from collections import defaultdict

MARKERS_INPUT = ("pytest_output", "junit", "test_hidden", "/hidden", "\\hidden", "harness/tasks", "harness\\tasks",
                 "../", "..\\", "result.json", "events.jsonl", "tools.jsonl", "prompt.txt")
MARKERS_OUTPUT = ("test_hidden_", "def test_jpy_csv_totals", "def test_max_length_strips", "def test_merge_invalid_raises",
                  "def test_ids_never_reused", "def test_no_function_longer")


def main():
    results = []
    for f in glob.glob("agents/*/runs/iter*/*/*/result.json"):
        r = json.load(open(f, encoding="utf-8"))
        r["_f"] = f
        results.append(r)
    print("results:", len(results))
    bad = [r["_f"] for r in results if r["passed"] > r["total"] or r["total"] == 0 or r["wall_s"] <= 0 or r.get("n_events", 1) == 0]
    print("integrity problems:", bad or "none")
    print("protected-file edits:", sum(1 for r in results if not r["protected_ok"]),
          "| question attempts:", sum(r["question_attempts"] for r in results),
          "| timeouts:", sum(1 for r in results if r["timed_out"]),
          "| retries>1:", sum(1 for r in results if r.get("attempts", 1) > 1))
    inputs_hits = defaultdict(list)
    sibling_hits = defaultdict(list)
    output_leaks = []
    for r in results:
        own_ws = (r["run_dir"] + "/ws").replace("\\", "/").lower()
        tf = r["_f"].replace("result.json", "tools.jsonl")
        for line in open(tf, encoding="utf-8", errors="replace"):
            t = json.loads(line)
            inp = t.get("input") or {}
            if t.get("tool") in ("write", "edit") and isinstance(inp, dict):
                # only the target path matters for a write/edit; file *content* legitimately mentions ../ etc.
                inp = {k: v for k, v in inp.items() if k in ("filePath", "path")}
            s = (json.dumps(inp, ensure_ascii=False) if not isinstance(inp, str) else inp)
            s_norm = s.replace("\\\\", "/").replace("\\", "/").lower()
            if any(m.replace("\\", "/") in s_norm for m in MARKERS_INPUT):
                inputs_hits[(r["slug"], r["task"], r["variant"])].append((t["tool"], t.get("status"), s[:170].replace("\n", " ")))
            # references to another run folder of the same agent (runs/iterN/... not ending in own ws)
            if "runs/iter" in s_norm and own_ws not in s_norm:
                sibling_hits[(r["slug"], r["task"], r["variant"])].append((t["tool"], t.get("status"), s[:170].replace("\n", " ")))
            out = t.get("output") or ""
            if any(m in out for m in MARKERS_OUTPUT):
                output_leaks.append((r["slug"], r["task"], r["variant"], t["tool"], out[:140].replace("\n", " ")))
    print("\nTool inputs referencing scoring files / hidden tests / parent dirs:", len(inputs_hits), "runs")
    for k, v in inputs_hits.items():
        print(" ", k)
        for tool, status, s in v[:4]:
            print("      ", tool, status, s)
    print("\nTool inputs referencing other run folders:", len(sibling_hits), "runs")
    for k, v in sibling_hits.items():
        print(" ", k)
        for tool, status, s in v[:4]:
            print("      ", tool, status, s)
    print("\nTool outputs exposing hidden-test content:", len(output_leaks))
    for row in output_leaks[:10]:
        print("  LEAK:", row)


if __name__ == "__main__":
    main()
