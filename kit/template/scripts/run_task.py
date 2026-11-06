#!/usr/bin/env python3
"""Run a task contract non-interactively through OpenCode, with the graph map in the prompt and a
full transcript saved. This is the scripted twin of the /task slash command: use it from CI, from a
batch of contracts, or when you want logs and a timeout.

    python scripts/run_task.py .opencode/tasks/<name>.md [--model provider/model] [--agent builder]
                                                        [--timeout 1800] [--test "python -m pytest -q"]

What it does: builds the prompt = contract + code map (task_context.py) + closing instruction, runs
`opencode run --format json` in the project root (PWD pinned: OpenCode reads it), stores
.opencode/runs/<name>-<timestamp>/{prompt.txt,events.jsonl,stderr.txt,summary.json}, prints the
model's final message, then runs the test command and prints its tail.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def find_opencode() -> str:
    for cand in (Path(os.environ.get("APPDATA", "")) / "npm" / "node_modules" / "opencode-ai" / "bin" / "opencode.exe",):
        if cand.exists():
            return str(cand)
    found = shutil.which("opencode")
    if not found:
        sys.exit("opencode not found on PATH")
    return found


def kill_tree(pid: int) -> None:
    if os.name == "nt":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], capture_output=True)
    else:
        subprocess.run(["kill", "-9", str(pid)], capture_output=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("contract")
    ap.add_argument("--model", help="provider/model (default: the project's opencode.json model)")
    ap.add_argument("--agent", default="builder")
    ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("--startup-timeout", type=int, default=300, help="seconds without any event before giving up")
    ap.add_argument("--test", default="python -m pytest -q", help="command run after the model finishes ('' to skip)")
    a = ap.parse_args()

    contract = Path(a.contract)
    if not contract.is_absolute():
        contract = ROOT / contract
    if not contract.exists():
        sys.exit(f"contract not found: {contract}")
    ctx = subprocess.run([sys.executable, str(ROOT / "scripts" / "task_context.py"), str(contract)],
                         capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(ROOT)).stdout
    prompt = (ctx.rstrip() + "\n\nFollow AGENTS.md. Implement the contract above exactly, in the files it names, going "
              "straight to the modules the code map points at. Run the provided tests before you finish and end with "
              "the short summary described in AGENTS.md.\n")
    name = contract.stem
    run_dir = ROOT / ".opencode" / "runs" / f"{name}-{datetime.now():%Y%m%d-%H%M%S}"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "prompt.txt").write_text(prompt, encoding="utf-8")

    cmd = [find_opencode(), "run", "--format", "json", "--auto", "--dir", str(ROOT), "--agent", a.agent,
           "--title", f"task:{name}"]
    if a.model:
        cmd += ["-m", a.model]
    cmd.append(prompt)
    env = dict(os.environ, PWD=str(ROOT), NO_COLOR="1", OPENCODE_DISABLE_AUTOUPDATE="1")
    # provider keys for opencode (NVIDIA_API_KEY, OPENAI_API_KEY, ...) come from the project's git-ignored .env
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip().strip('"').strip("'")
                if k and v and k not in env:
                    env[k] = v
    events = run_dir / "events.jsonl"
    t0 = time.time()
    status = "finished"
    with open(events, "wb") as fo, open(run_dir / "stderr.txt", "wb") as fe:
        p = subprocess.Popen(cmd, cwd=str(ROOT), stdout=fo, stderr=fe, stdin=subprocess.DEVNULL, env=env)
        last_size, last_change = 0, time.time()
        while p.poll() is None:
            now = time.time()
            size = events.stat().st_size if events.exists() else 0
            if size != last_size:
                last_size, last_change = size, now
            if now - t0 > a.timeout:
                status = "timeout"
                kill_tree(p.pid)
                break
            if last_size == 0 and now - t0 > a.startup_timeout:
                status = "no-events (provider down or quota exhausted?)"
                kill_tree(p.pid)
                break
            time.sleep(1)
    wall = round(time.time() - t0, 1)

    texts, tools, steps = [], 0, 0
    for line in events.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        part = ev.get("part") or {}
        if part.get("type") == "text":
            texts.append(part.get("text") or "")
        elif part.get("type") == "tool":
            tools += 1
        elif part.get("type") == "step-finish":
            steps += 1
    final = texts[-1].strip() if texts else ""
    print(f"[run_task] {status} in {wall}s: {steps} steps, {tools} tool calls. Transcript: {run_dir}")
    print("\n--- model's final message ---\n" + (final or "(none)"))
    test_tail = ""
    if a.test:
        r = subprocess.run(a.test, shell=True, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=600)
        test_tail = (r.stdout + r.stderr)[-1500:]
        print(f"\n--- {a.test} (exit {r.returncode}) ---\n{test_tail}")
    (run_dir / "summary.json").write_text(json.dumps({
        "contract": str(contract), "status": status, "wall_s": wall, "steps": steps, "tool_calls": tools,
        "model": a.model, "agent": a.agent, "final_message": final[:4000], "test_tail": test_tail,
    }, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
