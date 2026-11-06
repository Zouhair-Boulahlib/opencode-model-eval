#!/usr/bin/env python3
"""Print a readable transcript of one run folder: prompt, tool calls, final message, score.

Usage: python harness/inspect_run.py agents/<slug>/runs/iter1/<task>/<variant> [--full]
"""
import json
import sys
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    run_dir = Path(sys.argv[1])
    full = "--full" in sys.argv
    lim = 100000 if full else 700
    res = json.loads((run_dir / "result.json").read_text(encoding="utf-8"))
    print(f"=== {res['slug']} | {res['task']} | {res['variant']} | iter{res['iteration']} ===")
    print(f"score {res['passed']}/{res['total']}  wall {res['wall_s']}s  steps {res['steps']}  tools {res['tool_calls']}  "
          f"timed_out={res['timed_out']} protected_ok={res['protected_ok']} created={res['files_created']} modified={res['files_modified']}")
    if res.get("failed_tests"):
        print("failed:", ", ".join(res["failed_tests"][:15]))
    if res.get("errors"):
        print("errors:", res["errors"][:3])
    print("\n--- PROMPT ---")
    print((run_dir / "prompt.txt").read_text(encoding="utf-8")[:lim])
    print("\n--- TRANSCRIPT ---")
    for line in (run_dir / "events.jsonl").read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        part = ev.get("part") or {}
        t = part.get("type")
        if t == "text":
            print(f"\n[assistant text]\n{part.get('text', '')[:lim]}")
        elif t == "reasoning":
            print(f"\n[reasoning] {part.get('text', '')[:300]}")
        elif t == "tool":
            st = part.get("state") or {}
            inp = st.get("input") or {}
            name = part.get("tool")
            if name == "bash":
                head = inp.get("command", "")
            elif name in ("write", "edit"):
                head = inp.get("filePath", "") + (f"  (+{len(inp.get('content', ''))} chars)" if name == "write" else "")
            else:
                head = json.dumps(inp, ensure_ascii=False)[:200]
            out = (st.get("output") or st.get("error") or "")
            print(f"\n[tool:{name} {st.get('status')}] {head[:lim]}")
            if name == "write" and full:
                print(inp.get("content", ""))
            if out:
                print("   -> " + out[:lim].replace("\n", "\n      "))
        elif ev.get("type") == "error":
            print(f"\n[ERROR] {json.dumps(ev)[:500]}")
    print("\n--- HIDDEN TEST OUTPUT (tail) ---")
    po = run_dir / "pytest_output.txt"
    if po.exists():
        print(po.read_text(encoding="utf-8", errors="replace")[-1500:])


if __name__ == "__main__":
    main()
