#!/usr/bin/env python3
"""Evaluation harness: run opencode models on coding tasks inside isolated agent
folders, then score the result with hidden pytest suites.

Layout produced per run:
  agents/<slug>/runs/iter<N>/<task>/<variant>[_r<rep>]/
      ws/                  workspace the model worked in (cwd of `opencode run`)
      prompt.txt           exact prompt sent
      events.jsonl         raw JSON event stream from `opencode run --format json`
      stderr.txt           opencode stderr
      tools.jsonl          one line per tool call (name, input summary, status)
      pytest_output.txt    hidden-test output
      junit.xml            hidden-test junit report
      result.json          all metrics for this run

Usage examples:
  python harness/run_eval.py --selftest
  python harness/run_eval.py --iter 1 --variants v0_brief v1_spec v2_spec_verify --workers 5
  python harness/run_eval.py --iter 2 --models glm-5.3-flash-free --variants m_glm_a --tasks t3_todo_cli
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import threading
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

HARNESS = Path(__file__).resolve().parent
ROOT = HARNESS.parent
AGENTS = ROOT / "agents"
RESULTS = ROOT / "results"
TASKS_DIR = HARNESS / "tasks"
REFERENCE_DIR = HARNESS / "reference"
sys.path.insert(0, str(HARNESS))
from prompts import build_prompt  # noqa: E402

MODELS = [
    "opencode/beam-free",
    "opencode/big-pickle",
    "opencode/crouton-alpha-free",
    "opencode/deepseek-v4.1-flash-free",
    "opencode/flint-40b-free",
    "opencode/glm-5.3-flash-free",
    "opencode/mimo-v2.6-flash-free",
    "opencode/nemotron-3.5-lightning-free",
    "opencode/nemotron-3.5-super-vl-free",
    "opencode/pulse-alpha-free",
]
# Models the free tier no longer serves: kept in MODELS for the reports, skipped by "--models all".
RETIRED = {"opencode/pulse-alpha-free"}  # retired 2026-11-07
# Extra providers/models (e.g. NVIDIA NIM "nvidia/z-ai/glm-5.3-flash") can be listed in
# harness/models_extra.json as a JSON array of "provider/model" ids. They need credentials
# configured in opencode (`opencode providers login` or the provider's env var).
_extra = HARNESS / "models_extra.json"
if _extra.exists():
    MODELS += [m for m in json.loads(_extra.read_text(encoding="utf-8")) if m not in MODELS]


def _find_opencode() -> str:
    cands = [
        Path(os.environ.get("APPDATA", "")) / "npm" / "node_modules" / "opencode-ai" / "bin" / "opencode.exe",
    ]
    for c in cands:
        if c.exists():
            return str(c)
    found = shutil.which("opencode")
    if not found:
        raise SystemExit("opencode executable not found")
    return found


OPENCODE_EXE = _find_opencode()
_print_lock = threading.Lock()
_jsonl_lock = threading.Lock()


def log(msg: str) -> None:
    with _print_lock:
        print(f"[{datetime.now():%H:%M:%S}] {msg}", flush=True)


# ------------------------------------------------------------------ quota gate
# The hosted free tier has an account-wide usage limit. When it is exhausted,
# `opencode run` hangs without emitting a single event. A run that produces zero
# events closes the gate; a background prober sends a tiny request every
# PROBE_INTERVAL seconds and reopens the gate once a real answer comes back.
PROBE_MODEL = "opencode/big-pickle"  # pulse-alpha-free was retired on 2026-11-07
PROBE_INTERVAL = 300
_gate = threading.Event()
_gate.set()
_gate_lock = threading.Lock()


def probe_quota(timeout: int = 75) -> bool:
    ws = RESULTS / "_probe"
    ws.mkdir(parents=True, exist_ok=True)
    cmd = [OPENCODE_EXE, "run", "--pure", "--format", "json", "-m", PROBE_MODEL, "--dir", str(ws),
           "--title", "quota-probe", "Reply with exactly the word PONG."]
    env = dict(os.environ)
    env["PWD"] = str(ws)
    out_path = ws / "probe_out.jsonl"
    with open(out_path, "wb") as fo:
        p = subprocess.Popen(cmd, cwd=str(ws), stdout=fo, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, env=env)
        try:
            p.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            kill_tree(p.pid)
    try:
        return '"type":"text"' in out_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False


def _prober() -> None:
    """Cheap HTTP probe first (returns the server's Retry-After, no opencode process); sleep until
    the announced reset, then confirm with a real `opencode run` before reopening the gate."""
    try:
        import quota_probe  # harness/quota_probe.py
    except ImportError:
        quota_probe = None
    while True:
        if quota_probe is not None:
            r = quota_probe.probe()
            # Since 2026-11-07 the HTTP endpoint answers every non-OpenCode client with 429
            # FreeUsageLimitError ("Free models work in OpenCode"), so its Retry-After is not a quota
            # signal any more; only trust it when the message does not say that.
            if (not r["ok"] and r.get("retry_after_s")
                    and "work in OpenCode" not in (r.get("message") or "")):
                wait = min(int(r["retry_after_s"]) + 30, 6 * 3600)
                log(f"QUOTA exhausted; server says Retry-After {r['retry_after_s']}s "
                    f"(reset about {r.get('reset_at_local')}), sleeping {wait}s")
                time.sleep(wait)
                continue
        if probe_quota():
            log("QUOTA OK: free tier answering again, resuming runs")
            _gate.set()
            return
        log(f"QUOTA still exhausted, next probe in {PROBE_INTERVAL}s")
        time.sleep(PROBE_INTERVAL)


def quota_pause(reason: str) -> None:
    with _gate_lock:
        if _gate.is_set():
            _gate.clear()
            log(f"QUOTA PAUSE ({reason}); all workers wait until a probe succeeds")
            threading.Thread(target=_prober, daemon=True).start()
    _gate.wait()


def slug(model: str) -> str:
    """Folder-safe name: drop the provider prefix, turn remaining slashes into '__'.
    opencode/glm-5.3-flash-free -> glm-5.3-flash-free; nvidia/z-ai/glm-5.3 -> z-ai__glm-5.3.
    Same model name under two providers would collide, so a non-opencode provider is prefixed."""
    provider, rest = model.split("/", 1)
    rest = rest.replace("/", "__")
    return rest if provider == "opencode" else f"{provider}__{rest}"


def model_from_slug(s: str) -> str:
    for m in MODELS:
        if slug(m) == s or m == s:
            return m
    if "/" in s:  # a full provider/model id that is not in the list yet
        return s
    raise SystemExit(f"unknown model {s}")


def ensure_agent_dir(model: str) -> Path:
    """Create agents/<slug>/ with its pinned opencode.json on first use of a model."""
    d = AGENTS / slug(model)
    if not (d / "opencode.json").exists():
        (d / "runs").mkdir(parents=True, exist_ok=True)
        (d / "prompts").mkdir(exist_ok=True)
        cfg = {
            "$schema": "https://opencode.ai/config.json",
            "model": model,
            "small_model": model,
            "disabled_providers": ["ollama"],
            "permission": {"external_directory": "deny", "webfetch": "deny", "websearch": "deny", "question": "deny"},
        }
        (d / "opencode.json").write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
        (d / "prompts" / "variants.json").write_text("{}\n", encoding="utf-8")
        (d / "notes.md").write_text(f"<!-- Hand-written behaviour notes for {model}. Included in REPORT.md -->\n_No notes yet._\n",
                                    encoding="utf-8")
        log(f"created agent folder {d.relative_to(ROOT)} for {model}")
    return d


def load_task(tid: str) -> dict:
    return json.loads((TASKS_DIR / tid / "task.json").read_text(encoding="utf-8"))


def all_tasks() -> list[str]:
    return sorted(p.name for p in TASKS_DIR.iterdir() if (p / "task.json").exists())


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def snapshot(ws: Path) -> dict[str, str]:
    out = {}
    for p in ws.rglob("*"):
        if (p.is_file() and "__pycache__" not in p.parts and ".pytest_cache" not in p.parts
                and ".git" not in p.parts and p.name != "opencode.json"):
            out[str(p.relative_to(ws)).replace("\\", "/")] = sha(p)
    return out


def isolate_workspace(ws: Path, agent_dir: Path) -> None:
    """Make ws/ its own project so OpenCode's `external_directory: deny` starts at ws/.

    OpenCode treats the enclosing git worktree as the project. Once this evaluation folder became a git
    repository (2026-11-06), every run could read anything inside it, hidden tests included (one NVIDIA
    MiniMax run did; see harness/isolation_scan.py). A git repository inside ws/ moves the boundary back to
    ws/, and a copy of the agent's opencode.json keeps the pinned model and permissions, since config
    discovery stops at the worktree root. Both are excluded from the file snapshot.
    """
    subprocess.run(["git", "init", "-q", str(ws)], check=True, capture_output=True)
    shutil.copy2(agent_dir / "opencode.json", ws / "opencode.json")


def kill_tree(pid: int) -> None:
    subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], capture_output=True)


# --------------------------------------------------------------------------- run
def _last_line(path: Path) -> str:
    try:
        with open(path, "rb") as f:
            f.seek(0, 2)
            size = f.tell()
            f.seek(max(0, size - 4096))
            tail = f.read().decode("utf-8", "replace")
        lines = [ln for ln in tail.splitlines() if ln.strip()]
        return lines[-1] if lines else ""
    except OSError:
        return ""


STARTUP_TIMEOUT = 120


def run_opencode(model: str, prompt: str, ws: Path, title: str, timeout: int, run_dir: Path,
                 idle_after_stop: int = 20, startup_timeout: int | None = None):
    startup_timeout = startup_timeout or STARTUP_TIMEOUT
    """Run `opencode run` with cwd=ws. Returns (rc, timed_out, forced_exit, wall_s).

    opencode derives the session directory from the PWD environment variable, so PWD is
    pinned to the workspace (otherwise files land in the parent shell's directory). A
    polling loop enforces the timeout and also kills the process if it lingers after the
    model's final `stop` step.
    """
    cmd = [OPENCODE_EXE, "run", "--pure", "--auto", "--format", "json", "-m", model,
           "--dir", str(ws), "--title", title, prompt]
    env = dict(os.environ)
    env["PWD"] = str(ws)
    env["OPENCODE_DISABLE_AUTOUPDATE"] = "1"
    env["NO_COLOR"] = "1"
    env.update(provider_env(model))
    events = run_dir / "events.jsonl"
    t0 = time.time()
    timed_out = forced_exit = False
    with open(events, "wb") as fo, open(run_dir / "stderr.txt", "wb") as fe:
        p = subprocess.Popen(cmd, cwd=str(ws), stdout=fo, stderr=fe, stdin=subprocess.DEVNULL, env=env)
        last_size, last_change = 0, time.time()
        while True:
            rc = p.poll()
            if rc is not None:
                break
            now = time.time()
            size = events.stat().st_size if events.exists() else 0
            if size != last_size:
                last_size, last_change = size, now
            if now - t0 > timeout or (last_size == 0 and now - t0 > startup_timeout):
                # full timeout, or opencode never produced a single event (startup hang)
                timed_out = now - t0 > timeout
                kill_tree(p.pid)
                rc = -9
                break
            if now - last_change > idle_after_stop and '"reason":"stop"' in _last_line(events):
                forced_exit = True
                kill_tree(p.pid)
                rc = 0
                break
            time.sleep(1)
        try:
            p.wait(timeout=30)
        except subprocess.TimeoutExpired:
            pass
    return rc, timed_out, forced_exit, round(time.time() - t0, 1)


# ------------------------------------------------------------- provider keys
# API keys for non-free providers are read from the OS credential store (Windows Credential
# Manager via the `keyring` library) and injected only into the opencode child process. Store
# one with:  python -c "import keyring,getpass; keyring.set_password('opencode-eval','NVIDIA_API_KEY',getpass.getpass())"
PROVIDER_ENV = {"nvidia": "NVIDIA_API_KEY", "openai": "OPENAI_API_KEY", "anthropic": "ANTHROPIC_API_KEY",
                "google": "GOOGLE_GENERATIVE_AI_API_KEY", "groq": "GROQ_API_KEY", "openrouter": "OPENROUTER_API_KEY",
                "mistral": "MISTRAL_API_KEY", "deepseek": "DEEPSEEK_API_KEY", "xai": "XAI_API_KEY"}
KEYRING_SERVICE = "opencode-eval"


ENV_FILE = ROOT / ".env.local"  # git-ignored; lines of VAR=value


def _env_file_value(var: str) -> str | None:
    if not ENV_FILE.exists():
        return None
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            if k.strip() == var:
                return v.strip().strip('"').strip("'") or None
    return None


def provider_env(model: str) -> dict[str, str]:
    """Environment additions for the model's provider: the API key, looked up in this order:
    already-set process environment, the git-ignored `.env.local` file, the OS credential store."""
    provider = model.split("/", 1)[0]
    var = PROVIDER_ENV.get(provider)
    if not var or os.environ.get(var):
        return {}
    secret = _env_file_value(var)
    if not secret:
        try:
            import keyring  # type: ignore
            secret = keyring.get_password(KEYRING_SERVICE, var)
        except Exception as e:  # noqa: BLE001
            log(f"WARNING: cannot read {var} from the credential store: {e!r}")
    if not secret:
        log(f"WARNING: no {var} in .env.local or the credential store; provider {provider} runs will fail")
        return {}
    return {var: secret}


def _short(obj, n=300) -> str:
    s = obj if isinstance(obj, str) else json.dumps(obj, ensure_ascii=False)
    return s if len(s) <= n else s[:n] + "..."


def parse_events(events_path: Path, tools_path: Path) -> dict:
    st = {
        "steps": 0,
        "tokens": {"input": 0, "output": 0, "reasoning": 0, "cache_read": 0, "cache_write": 0},
        "cost": 0.0,
        "finish_reasons": [],
        "texts": [],
        "errors": [],
        "session_id": None,
        "tool_calls": {},
        "tool_total": 0,
        "tool_errors": 0,
        "bash_cmds": [],
        "question_attempts": 0,
        "event_types": {},
        "n_events": 0,
    }
    tools: dict[str, dict] = {}
    if not events_path.exists():
        return st
    with open(events_path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            st["n_events"] += 1
            t = ev.get("type") or ""
            st["event_types"][t] = st["event_types"].get(t, 0) + 1
            part = ev.get("part") or {}
            ptype = part.get("type") or ""
            st["session_id"] = st["session_id"] or ev.get("sessionID") or part.get("sessionID")
            if t == "step_finish" or ptype == "step-finish":
                st["steps"] += 1
                tok = part.get("tokens") or {}
                for k in ("input", "output", "reasoning"):
                    st["tokens"][k] += int(tok.get(k) or 0)
                cache = tok.get("cache") or {}
                st["tokens"]["cache_read"] += int(cache.get("read") or 0)
                st["tokens"]["cache_write"] += int(cache.get("write") or 0)
                st["cost"] += float(part.get("cost") or 0)
                st["finish_reasons"].append(part.get("reason"))
            elif t == "text" or ptype == "text":
                st["texts"].append(part.get("text") or "")
            elif t == "error" or ptype == "error":
                st["errors"].append(_short(ev.get("error") or ev, 600))
            elif "tool" in t or ptype == "tool":
                pid = part.get("id") or part.get("callID") or f"anon{len(tools)}"
                name = part.get("tool") or part.get("name") or ev.get("tool") or "unknown"
                state = part.get("state") or {}
                tools[pid] = {
                    "tool": name,
                    "status": state.get("status") or ev.get("status"),
                    "input": state.get("input") or part.get("input") or {},
                    "output": _short(state.get("output") or "", 500),
                    "error": _short(state.get("error") or "", 300),
                }
    with open(tools_path, "w", encoding="utf-8") as f:
        for pid, tc in tools.items():
            f.write(json.dumps({"id": pid, **tc}, ensure_ascii=False) + "\n")
            name = tc["tool"]
            st["tool_calls"][name] = st["tool_calls"].get(name, 0) + 1
            st["tool_total"] += 1
            if tc["status"] == "error" or tc["error"]:
                st["tool_errors"] += 1
            if name == "question":
                st["question_attempts"] += 1
            if name == "bash":
                inp = tc["input"] or {}
                cmd = inp.get("command") if isinstance(inp, dict) else str(inp)
                if cmd:
                    st["bash_cmds"].append(_short(cmd, 200))
    return st


# ------------------------------------------------------------------------- score
def count_tests_in_junit(junit: Path):
    root = ET.parse(junit).getroot()
    passed, failed = 0, []
    collection_error = False
    for tc in root.iter("testcase"):
        bad = any(tc.find(tag) is not None for tag in ("failure", "error", "skipped"))
        name = tc.get("name") or "?"
        if bad:
            failed.append(name)
            if tc.find("error") is not None and name.endswith(".py"):
                collection_error = True
        else:
            passed += 1
    return passed, failed, collection_error


def score_run(task: dict, ws: Path, run_dir: Path) -> dict:
    tid = task["id"]
    starter = TASKS_DIR / tid / "starter"
    hidden = TASKS_DIR / tid / "hidden"
    protected_ok = True
    for rel in task.get("protected", []):
        f = ws / rel
        protected_ok = protected_ok and f.exists() and sha(f) == sha(starter / rel)
    tests = task["hidden_tests"]
    for t in tests:
        shutil.copy(hidden / t, ws / t)
    junit = run_dir / "junit.xml"
    cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--junitxml", str(junit), *tests]
    try:
        proc = subprocess.run(cmd, cwd=str(ws), capture_output=True, text=True, timeout=300,
                              encoding="utf-8", errors="replace")
        pytest_out = proc.stdout + "\n" + proc.stderr
    except subprocess.TimeoutExpired:
        pytest_out = "PYTEST TIMEOUT"
    (run_dir / "pytest_output.txt").write_text(pytest_out, encoding="utf-8")
    for t in tests:
        (ws / t).unlink(missing_ok=True)
    expected_total = int(task.get("n_tests") or 0)
    passed, failed, collection_error = 0, [], False
    if junit.exists():
        passed, failed, collection_error = count_tests_in_junit(junit)
    total = expected_total or (passed + len(failed))
    if collection_error or passed + len(failed) < total:
        failed = failed if failed else ["<collection error>"]
    score = round(passed / total, 4) if total else 0.0
    expected = task.get("expect_files", [])
    files_present = all((ws / f).exists() for f in expected)
    return {
        "passed": passed,
        "total": total,
        "score": score,
        "score_adj": score if protected_ok else 0.0,
        "failed_tests": failed[:40],
        "collection_error": collection_error,
        "protected_ok": protected_ok,
        "expected_files_present": files_present,
    }


# --------------------------------------------------------------------------- job
def do_run(model: str, tid: str, variant: str, iteration: int, rep: int, timeout: int, force: bool,
           prev_variant: str | None = None):
    task = load_task(tid)
    s = slug(model)
    ensure_agent_dir(model)
    name = variant if rep == 0 else f"{variant}_r{rep}"
    run_dir = AGENTS / s / "runs" / f"iter{iteration}" / tid / name
    res_path = run_dir / "result.json"
    if res_path.exists() and not force:
        return json.loads(res_path.read_text(encoding="utf-8"))
    if prev_variant:
        # adaptive mode: decided at execution time, once the cheaper predecessor variant has run
        pname = prev_variant if rep == 0 else f"{prev_variant}_r{rep}"
        prp = AGENTS / s / "runs" / f"iter{iteration}" / tid / pname / "result.json"
        if prp.exists() and json.loads(prp.read_text(encoding="utf-8")).get("score_adj") == 1.0:
            log(f"SKIP  {s:30} {tid:14} {name} (predecessor {prev_variant} already 100%)")
            return None
    if run_dir.exists():
        shutil.rmtree(run_dir)
    ws = run_dir / "ws"
    ws.mkdir(parents=True)
    starter = TASKS_DIR / tid / "starter"
    if starter.exists():
        shutil.copytree(starter, ws, dirs_exist_ok=True)
    isolate_workspace(ws, AGENTS / s)
    before = snapshot(ws)
    prompt = build_prompt(tid, variant, s)
    (run_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
    title = f"{s}|{tid}|{name}|iter{iteration}"
    log(f"START {s:30} {tid:14} {name}")
    attempts = 0
    while True:
        _gate.wait()
        attempts += 1
        rc, timed_out, forced_exit, wall = run_opencode(model, prompt, ws, title, timeout, run_dir)
        ev = parse_events(run_dir / "events.jsonl", run_dir / "tools.jsonl")
        infra = ev["n_events"] == 0 or (ev["steps"] == 0 and ev["tool_total"] == 0 and not timed_out)
        if infra and attempts < 6:
            log(f"RETRY {s} {tid} {name} (events={ev['n_events']}, rc={rc}, wall={wall}s) errors={ev['errors'][:1]}")
            if ev["n_events"] == 0:
                quota_pause(f"{s} {tid} {name} produced no events")
            else:
                time.sleep(15 * attempts)
            # reset the workspace so the retry starts clean
            shutil.rmtree(ws)
            ws.mkdir()
            if starter.exists():
                shutil.copytree(starter, ws, dirs_exist_ok=True)
            continue
        break
    after = snapshot(ws)
    created = sorted(f for f in after if f not in before)
    modified = sorted(f for f in after if f in before and after[f] != before[f])
    deleted = sorted(f for f in before if f not in after)
    sc = score_run(task, ws, run_dir)
    final_text = ev["texts"][-1].strip() if ev["texts"] else ""
    bash_joined = "\n".join(ev["bash_cmds"]).lower()
    result = {
        "model": model,
        "slug": s,
        "task": tid,
        "variant": variant,
        "rep": rep,
        "iteration": iteration,
        "run_dir": str(run_dir.relative_to(ROOT)).replace("\\", "/"),
        "finished": datetime.now().isoformat(timespec="seconds"),
        "wall_s": wall,
        "exit_code": rc,
        "timed_out": timed_out,
        "forced_exit_after_stop": forced_exit,
        "attempts": attempts,
        "infra_error": infra,
        **sc,
        "files_created": created,
        "files_modified": modified,
        "files_deleted": deleted,
        "wrote_own_tests": any(Path(f).name.startswith("test_") for f in created),
        "ran_pytest": ("pytest" in bash_joined) or ("unittest" in bash_joined),
        "ran_python": "python" in bash_joined,
        "tool_calls": ev["tool_calls"],
        "tool_total": ev["tool_total"],
        "tool_errors": ev["tool_errors"],
        "question_attempts": ev["question_attempts"],
        "steps": ev["steps"],
        "finish_reasons": ev["finish_reasons"],
        "tokens": ev["tokens"],
        "cost": round(ev["cost"], 6),
        "errors": ev["errors"][:5],
        "n_events": ev["n_events"],
        "session_id": ev["session_id"],
        "final_text": final_text[:4000],
        "final_text_len": len(final_text),
        "final_text_asks_question": final_text.rstrip().endswith("?"),
        "prompt_chars": len(prompt),
    }
    res_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    RESULTS.mkdir(exist_ok=True)
    with _jsonl_lock:
        with open(RESULTS / "runs.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")
    flag = "TIMEOUT" if timed_out else ("PROTECTED!" if not sc["protected_ok"] else "")
    log(f"DONE  {s:30} {tid:14} {name:28} {sc['passed']:>2}/{sc['total']:<2} "
        f"wall={wall:>6}s tools={ev['tool_total']:<3} out_tok={ev['tokens']['output']:<6} {flag}")
    return result


# ---------------------------------------------------------------------- selftest
def selftest() -> None:
    """Score reference solutions (expect 100%) and bare starters, and record n_tests."""
    tmp = RESULTS / "_selftest"
    if tmp.exists():
        shutil.rmtree(tmp)
    ok = True
    for tid in all_tasks():
        task = load_task(tid)
        for label in ("reference", "starter"):
            run_dir = tmp / tid / label
            ws = run_dir / "ws"
            ws.mkdir(parents=True)
            starter = TASKS_DIR / tid / "starter"
            if starter.exists():
                shutil.copytree(starter, ws, dirs_exist_ok=True)
            if label == "reference":
                shutil.copytree(REFERENCE_DIR / tid, ws, dirs_exist_ok=True)
            sc = score_run(task, ws, run_dir)
            if label == "reference":
                if sc["score"] != 1.0:
                    ok = False
                if not task.get("n_tests"):
                    task["n_tests"] = sc["passed"] + len(sc["failed_tests"])
                    (TASKS_DIR / tid / "task.json").write_text(json.dumps(task, indent=2) + "\n", encoding="utf-8")
            print(f"{tid:14} {label:9} {sc['passed']:>2}/{sc['total']:<2} failed={sc['failed_tests'][:6]}")
    print("SELFTEST", "OK" if ok else "FAILED")
    if not ok:
        sys.exit(1)


# -------------------------------------------------------------------------- main
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--iter", type=int, default=1)
    ap.add_argument("--variants", nargs="+", default=["v0_brief", "v1_spec", "v2_spec_verify"])
    ap.add_argument("--tasks", nargs="+", default=["all"])
    ap.add_argument("--models", nargs="+", default=["all"])
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--timeout", type=int, default=480)
    ap.add_argument("--reps", type=int, default=1)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--redo-infra", action="store_true",
                    help="re-run only the selected runs whose result has zero events (startup hang)")
    ap.add_argument("--order", choices=["variant", "model"], default="variant",
                    help="variant: all models per variant first; model: finish each model's full matrix first")
    ap.add_argument("--probe-first", action="store_true", help="check the free-tier quota before starting")
    ap.add_argument("--startup-timeout", type=int, default=120,
                    help="seconds to wait for the first event before treating the run as hung (slow providers: 600+)")
    ap.add_argument("--adaptive", action="store_true",
                    help="skip a variant on a (model, task) whose preceding variant in --variants already scored 100%%")
    a = ap.parse_args()
    global STARTUP_TIMEOUT
    STARTUP_TIMEOUT = a.startup_timeout
    if a.selftest:
        selftest()
        return
    if a.probe_first and not probe_quota():
        quota_pause("startup probe failed")
    tasks = all_tasks() if a.tasks == ["all"] else a.tasks
    models = [m for m in MODELS if m not in RETIRED] if a.models == ["all"] else [model_from_slug(m) for m in a.models]
    jobs = []
    for rep in range(a.reps):
        for variant in a.variants:
            for tid in tasks:
                for model in models:
                    force = a.force
                    if a.redo_infra:
                        name = variant if rep == 0 else f"{variant}_r{rep}"
                        rp = AGENTS / slug(model) / "runs" / f"iter{a.iter}" / tid / name / "result.json"
                        if not rp.exists():
                            continue
                        prev = json.loads(rp.read_text(encoding="utf-8"))
                        if prev.get("n_events", 1) != 0:
                            continue
                        force = True
                    vi = a.variants.index(variant)
                    prev = a.variants[vi - 1] if (a.adaptive and vi > 0) else None
                    jobs.append((model, tid, variant, a.iter, rep, a.timeout, force, prev))
    if a.order == "model":
        jobs.sort(key=lambda j: (MODELS.index(j[0]), a.variants.index(j[2]), j[1], j[4]))
    log(f"{len(jobs)} jobs, {a.workers} workers, timeout {a.timeout}s, order={a.order}, opencode={OPENCODE_EXE}")
    if a.dry_run:
        for j in jobs:
            print(j[:5])
        return
    t0 = time.time()
    results = []
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(do_run, *j): j for j in jobs}
        for fut in as_completed(futs):
            j = futs[fut]
            try:
                r = fut.result()
                if r:
                    results.append(r)
            except Exception as e:  # noqa: BLE001
                log(f"FAILED {j[:3]}: {e!r}")
    log(f"finished {len(results)}/{len(jobs)} runs in {round((time.time() - t0) / 60, 1)} min")


if __name__ == "__main__":
    main()
