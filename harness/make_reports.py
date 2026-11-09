#!/usr/bin/env python3
"""Generate REPORT.md (main) and agents/<slug>/REPORT.md from result.json files.

Hand-written analysis is merged in from:
  results/FINDINGS.md      -> main report "Key findings" section
  agents/<slug>/notes.md   -> agent report "Behaviour notes" section
"""
from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

HARNESS = Path(__file__).resolve().parent
ROOT = HARNESS.parent
AGENTS = ROOT / "agents"
RESULTS = ROOT / "results"
TASKS_DIR = HARNESS / "tasks"
sys.path.insert(0, str(HARNESS))
from prompts import build_prompt, resolve_variant  # noqa: E402

BASELINE = "v0_brief"


def enrich(r: dict) -> dict:
    """Add metrics derived from tools.jsonl: permission-blocked bash calls and tool errors by name."""
    r.setdefault("bash_denied", 0)
    r.setdefault("tool_error_names", {})
    p = ROOT / r["run_dir"] / "tools.jsonl"
    if not p.exists():
        return r
    denied, errs = 0, defaultdict(int)
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            t = json.loads(line)
        except json.JSONDecodeError:
            continue
        blob = (t.get("output") or "") + (t.get("error") or "")
        if t.get("tool") == "bash" and "prevents you from using" in blob:
            denied += 1
        if t.get("status") == "error" or t.get("error"):
            errs[t.get("tool") or "?"] += 1
    r["bash_denied"] = denied
    r["tool_error_names"] = dict(errs)
    return r


def load_results() -> list[dict]:
    """All runs except those marked invalid (result.json "invalid_reason", e.g. a hidden-test read found by
    harness/isolation_scan.py). Invalid runs stay on disk for transparency but never enter a report."""
    out = []
    for p in AGENTS.glob("*/runs/iter*/*/*/result.json"):
        try:
            r = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if r.get("invalid_reason"):
            continue
        out.append(enrich(r))
    return out


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def pct(x):
    return "-" if x is None else f"{x * 100:.0f}%"


def num(x, d=0):
    return "-" if x is None else f"{x:.{d}f}"


def md_table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(out)


def task_order(results):
    return sorted({r["task"] for r in results})


def variant_order(results):
    def key(v):
        return (0 if v.startswith("v") else 1, v)
    return sorted({r["variant"] for r in results}, key=key)


def by(results, *keys):
    d = defaultdict(list)
    for r in results:
        d[tuple(r[k] for k in keys)].append(r)
    return d


def variant_means(results):
    """mean score_adj per (slug, variant) averaged over tasks (task means first, then across tasks)."""
    out = {}
    for (s, v), rs in by(results, "slug", "variant").items():
        task_means = [mean([r["score_adj"] for r in trs]) for trs in by(rs, "task").values()]
        out[(s, v)] = mean(task_means)
    return out


def coverage(results, s, v):
    return len({r["task"] for r in results if r["slug"] == s and r["variant"] == v})


def best_variant(results, s, min_cov=3):
    """Best-scoring variant among those that ran on at least `min_cov` tasks (adaptive mode skips
    runs whose predecessor already scored 100%, so a variant with one lucky cell must not win).
    Ties go to the cheaper variant (lower mean wall time)."""
    vm = variant_means(results)
    cands = [(v, m) for (sl, v), m in vm.items() if sl == s and m is not None]
    if not cands:
        return None, None
    n_tasks = len(task_order(results))
    eligible = [(v, m) for v, m in cands if coverage(results, s, v) >= min(min_cov, n_tasks)]
    pool = eligible or cands

    def wall(v):
        return mean([r["wall_s"] for r in results if r["slug"] == s and r["variant"] == v]) or 0

    return max(pool, key=lambda x: (round(x[1], 3), -wall(x[0])))


def ceiling_mean(results, s):
    """Mean over tasks of the best score any variant reached (what the model can do when prompted well)."""
    tasks = task_order(results)
    vals = []
    for t in tasks:
        rs = [r["score_adj"] for r in results if r["slug"] == s and r["task"] == t]
        if rs:
            vals.append(max(rs))
    return mean(vals)


def behaviour_stats(rs):
    n = len(rs)
    if not n:
        return {}
    tool_names = defaultdict(int)
    for r in rs:
        for k, v in r.get("tool_calls", {}).items():
            tool_names[k] += v
    return {
        "runs": n,
        "mean_score": mean([r["score_adj"] for r in rs]),
        "wall": mean([r["wall_s"] for r in rs]),
        "tokens_out": mean([r["tokens"]["output"] for r in rs]),
        "tokens_in": mean([r["tokens"]["input"] for r in rs]),
        "tokens_reason": mean([r["tokens"]["reasoning"] for r in rs]),
        "steps": mean([r["steps"] for r in rs]),
        "tools": mean([r["tool_total"] for r in rs]),
        "tool_err": mean([r["tool_errors"] for r in rs]),
        "pytest_rate": mean([1.0 if r["ran_pytest"] else 0.0 for r in rs]),
        "own_tests_rate": mean([1.0 if r["wrote_own_tests"] else 0.0 for r in rs]),
        "timeout_rate": mean([1.0 if r["timed_out"] else 0.0 for r in rs]),
        "protected_viol": sum(1 for r in rs if not r["protected_ok"]),
        "questions": sum(r["question_attempts"] for r in rs),
        "asks_q_rate": mean([1.0 if r["final_text_asks_question"] else 0.0 for r in rs]),
        "final_len": mean([r["final_text_len"] for r in rs]),
        "zero_runs": sum(1 for r in rs if r["score_adj"] == 0),
        "perfect_runs": sum(1 for r in rs if r["score_adj"] == 1.0),
        "missing_files": sum(1 for r in rs if not r["expected_files_present"]),
        "tool_names": dict(sorted(tool_names.items(), key=lambda x: -x[1])),
        "errors": sum(1 for r in rs if r["errors"]),
        "bash_denied": sum(r.get("bash_denied", 0) for r in rs),
        "tool_error_names": dict(sorted(_sum_dicts(r.get("tool_error_names", {}) for r in rs).items())),
    }


def _sum_dicts(dicts):
    out = defaultdict(int)
    for d in dicts:
        for k, v in d.items():
            out[k] += v
    return out


def component_effects(results):
    """Pairwise variant comparisons (same model, same task, same iteration) -> mean delta."""
    pairs = [
        ("v0_brief", "v1_spec", "full spec instead of one-line brief"),
        ("v1_spec", "v2_spec_verify", "+ self-verify loop (write tests, run pytest, fix)"),
        ("v2_spec_verify", "v3_spec_plan_verify", "+ plan-first instruction"),
        ("v1_spec", "v4_spec_contract", "+ rules/contract (no questions, stdlib, summary)"),
        ("v1_spec", "v7_spec_examples", "+ worked I/O examples"),
        ("v2_spec_verify", "v8_spec_examples_verify_contract", "+ examples + contract on top of verify"),
        ("v2_spec_verify", "v5_full", "+ role + examples + plan + contract (everything)"),
        ("v0_brief", "v6_brief_verify", "+ verify loop on the one-line brief"),
    ]
    idx = {}
    for r in results:
        idx.setdefault((r["slug"], r["task"], r["variant"]), []).append(r["score_adj"])
    rows = []
    for a, b, label in pairs:
        deltas, per_model = [], defaultdict(list)
        for (s, t, v), scores in idx.items():
            if v != a:
                continue
            other = idx.get((s, t, b))
            if other:
                d = mean(other) - mean(scores)
                deltas.append(d)
                per_model[s].append(d)
        if not deltas:
            continue
        model_means = {s: mean(ds) for s, ds in per_model.items()}
        up = sum(1 for m in model_means.values() if m > 0.02)
        down = sum(1 for m in model_means.values() if m < -0.02)
        rows.append((a, b, label, mean(deltas), len(deltas), up, down, len(model_means)))
    return rows


# ----------------------------------------------------------------- main report
def write_main(results):
    slugs = sorted({r["slug"] for r in results})
    tasks = task_order(results)
    variants = variant_order(results)
    vm = variant_means(results)
    lines = []
    lines.append("# OpenCode free models: coding evaluation and prompting guide")
    lines.append("")
    lines.append(f"Generated {datetime.now():%Y-%m-%d %H:%M}. {len(results)} runs, {len(slugs)} models, "
                 f"{len(tasks)} tasks, {len(variants)} prompt variants, "
                 f"iterations {sorted({r['iteration'] for r in results})}.")
    lines.append("")
    lines.append("Every model ran through `opencode run` inside its own folder under `agents/<model>/`, "
                 "with its own `opencode.json` (model pinned, Ollama disabled, web and question tools denied). "
                 "Scores are the fraction of hidden pytest cases passed; a run that edits a protected test file scores 0.")
    lines.append("")
    # Leaderboard
    lines.append("## 1. Leaderboard (best prompt variant per model)")
    lines.append("")
    rows = []
    for s in slugs:
        bv, bm = best_variant(results, s)
        base = vm.get((s, BASELINE))
        st = behaviour_stats([r for r in results if r["slug"] == s])
        lift = None if (bm is None or base is None) else bm - base
        rows.append((s, bv, bm, base, lift, st))
    rows.sort(key=lambda x: -(x[2] or 0))
    table = []
    for i, (s, bv, bm, base, lift, st) in enumerate(rows, 1):
        table.append([i, f"[{s}](agents/{s}/REPORT.md)", f"{bv} ({coverage(results, s, bv)} tasks)" if bv else "-", pct(bm),
                      pct(ceiling_mean(results, s)), pct(base),
                      ("+" if (lift or 0) > 0 else "") + pct(lift) if lift is not None else "-",
                      num(st.get("wall")), num(st.get("tokens_out")), pct(st.get("timeout_rate"))])
    lines.append(md_table(["#", "model", "best variant (coverage)", "best variant mean", "ceiling (best per task)",
                           "baseline (v0)", "lift", "avg wall s", "avg out tokens", "timeouts"], table))
    lines.append("")
    lines.append("Cells with fewer than all tasks exist because adaptive mode skips a variant on a task whose cheaper "
                 "predecessor already scored 100%; the ceiling column is the fairest cross-model comparison.")
    lines.append("")
    # Matrix model x variant
    lines.append("## 2. Score matrix: model x prompt variant (mean over tasks run; task count in parentheses)")
    lines.append("")
    table = []
    for s in slugs:
        table.append([s] + [(pct(vm.get((s, v))) + f" ({coverage(results, s, v)})") if (s, v) in vm else "-" for v in variants])
    table.append(["**mean**"] + [pct(mean([vm.get((s, v)) for s in slugs])) for v in variants])
    lines.append(md_table(["model"] + variants, table))
    lines.append("")
    # Score by task (best variant)
    lines.append("## 3. Score by task (each model at its best variant)")
    lines.append("")
    table = []
    for s in slugs:
        bv, _ = best_variant(results, s)
        row = [s]
        for t in tasks:
            rs = [r for r in results if r["slug"] == s and r["variant"] == bv and r["task"] == t]
            row.append(pct(mean([r["score_adj"] for r in rs])) if rs else "-")
        table.append(row)
    table.append(["**mean (all runs)**"] + [pct(mean([r["score_adj"] for r in results if r["task"] == t])) for t in tasks])
    lines.append(md_table(["model"] + tasks, table))
    lines.append("")
    # Component effects
    lines.append("## 4. What each prompting trick is worth (paired comparison, same model and task)")
    lines.append("")
    eff = component_effects(results)
    if eff:
        table = [[f"{a} -> {b}", label, ("+" if d > 0 else "") + f"{d * 100:.1f} pts", n, f"{up}/{nm}", f"{down}/{nm}"]
                 for a, b, label, d, n, up, down, nm in eff]
        lines.append(md_table(["change", "meaning", "mean delta", "pairs", "models up", "models down"], table))
    lines.append("")
    # Behaviour profile
    lines.append("## 5. Behaviour profile per model (all runs)")
    lines.append("")
    table = []
    for s in slugs:
        st = behaviour_stats([r for r in results if r["slug"] == s])
        table.append([s, st["runs"], num(st["tools"], 1), pct(st["pytest_rate"]), pct(st["own_tests_rate"]),
                      num(st["steps"], 1), num(st["final_len"]), pct(st["timeout_rate"]), st["protected_viol"],
                      st["questions"], st["missing_files"], num(st["tool_err"], 2), st["bash_denied"]])
    lines.append(md_table(["model", "runs", "tool calls/run", "ran pytest", "wrote own tests", "LLM steps/run",
                           "final msg chars", "timeouts", "edited protected tests", "question attempts",
                           "missing target file", "tool errors/run", "bash blocked (unquoted path)"], table))
    lines.append("")
    # Findings
    findings = RESULTS / "FINDINGS.md"
    lines.append("## 6. Key findings and recommended tricks")
    lines.append("")
    lines.append(findings.read_text(encoding="utf-8").strip() if findings.exists() else "_FINDINGS.md not written yet._")
    lines.append("")
    # Agent links
    lines.append("## 7. Per-agent reports")
    lines.append("")
    for s in slugs:
        bv, bm = best_variant(results, s)
        lines.append(f"- [{s}](agents/{s}/REPORT.md): best variant `{bv}` at {pct(bm)}; runs live in `agents/{s}/runs/`")
    lines.append("")
    lines.append("## 8. Method")
    lines.append("")
    lines.append("- Tasks (`harness/tasks/`): " + "; ".join(f"`{t}` ({json.loads((TASKS_DIR / t / 'task.json').read_text())['skill']})" for t in tasks))
    lines.append("- Prompt variants are ordered lists of components (`harness/prompts.py`); per-model custom variants live in `agents/<model>/prompts/variants.json`.")
    lines.append("- Loop: run variant -> score with hidden tests -> read transcripts and failure modes -> write a targeted variant -> rerun. Iteration 1 is the broad sweep; later iterations are per-model refinements.")
    lines.append("- Each run folder holds `prompt.txt`, `events.jsonl` (raw model/tool stream), `tools.jsonl`, `pytest_output.txt`, `result.json` and the workspace `ws/`.")
    lines.append("- Regenerate with `python harness/make_reports.py`; rerun with `python harness/run_eval.py --iter N --variants ...`.")
    (ROOT / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- agent report
def write_agent(results, s):
    rs = [r for r in results if r["slug"] == s]
    if not rs:
        return
    tasks = task_order(results)
    iters = sorted({r["iteration"] for r in rs})
    vm = variant_means(rs)
    bv, bm = best_variant(rs, s)
    base = vm.get((s, BASELINE))
    st = behaviour_stats(rs)
    L = []
    L.append(f"# opencode/{s}: behaviour and prompting report")
    L.append("")
    L.append(f"Generated {datetime.now():%Y-%m-%d %H:%M} from {len(rs)} runs. "
             f"Best variant: `{bv}` with mean score {pct(bm)} (baseline `{BASELINE}`: {pct(base)}).")
    L.append("")
    L.append("## 1. Scores")
    L.append("")
    for it in iters:
        irs = [r for r in rs if r["iteration"] == it]
        vars_ = variant_order(irs)
        L.append(f"### Iteration {it}")
        L.append("")
        table = []
        for t in tasks:
            row = [t]
            for v in vars_:
                cell = [r for r in irs if r["task"] == t and r["variant"] == v]
                if not cell:
                    row.append("-")
                else:
                    parts = []
                    for r in sorted(cell, key=lambda r: r["rep"]):
                        tag = " T" if r["timed_out"] else (" P!" if not r["protected_ok"] else "")
                        parts.append(f"{r['passed']}/{r['total']}{tag}")
                    row.append(", ".join(parts))
            table.append(row)
        table.append(["**mean**"] + [pct(mean([r["score_adj"] for r in irs if r["variant"] == v])) for v in vars_])
        L.append(md_table(["task"] + vars_, table))
        L.append("")
        L.append("Legend: `passed/total`; `T` = timed out; `P!` = edited a protected test file (scored 0).")
        L.append("")
    L.append("## 2. Behaviour profile")
    L.append("")
    L.append(md_table(["metric", "value"], [
        ["runs", st["runs"]],
        ["mean score (all runs)", pct(st["mean_score"])],
        ["perfect runs / zero runs", f"{st['perfect_runs']} / {st['zero_runs']}"],
        ["avg wall time", f"{num(st['wall'])} s"],
        ["avg tokens in / out / reasoning", f"{num(st['tokens_in'])} / {num(st['tokens_out'])} / {num(st['tokens_reason'])}"],
        ["avg LLM steps per run", num(st["steps"], 1)],
        ["avg tool calls per run (errors)", f"{num(st['tools'], 1)} ({num(st['tool_err'], 2)})"],
        ["tool usage (total)", ", ".join(f"{k}: {v}" for k, v in st["tool_names"].items()) or "-"],
        ["tool errors by tool (total)", ", ".join(f"{k}: {v}" for k, v in st["tool_error_names"].items()) or "-"],
        ["bash calls blocked by permission (unquoted absolute path with a space)", st["bash_denied"]],
        ["ran pytest / wrote own tests", f"{pct(st['pytest_rate'])} / {pct(st['own_tests_rate'])}"],
        ["timeouts", pct(st["timeout_rate"])],
        ["edited protected test files", st["protected_viol"]],
        ["question-tool attempts / final message is a question", f"{st['questions']} / {pct(st['asks_q_rate'])}"],
        ["target file missing at end", st["missing_files"]],
        ["avg final message length", f"{num(st['final_len'])} chars"],
        ["runs with provider/tool errors", st["errors"]],
    ]))
    L.append("")
    # per-variant behaviour
    L.append("### Behaviour by prompt variant")
    L.append("")
    table = []
    for v in variant_order(rs):
        vs = behaviour_stats([r for r in rs if r["variant"] == v])
        table.append([v, vs["runs"], pct(vs["mean_score"]), num(vs["wall"]), num(vs["tools"], 1), pct(vs["pytest_rate"]),
                      pct(vs["own_tests_rate"]), pct(vs["timeout_rate"]), num(vs["final_len"])])
    L.append(md_table(["variant", "runs", "mean score", "wall s", "tools/run", "ran pytest", "own tests", "timeouts", "final chars"], table))
    L.append("")
    L.append("## 3. Failure analysis")
    L.append("")
    for t in tasks:
        trs = sorted([r for r in rs if r["task"] == t], key=lambda r: (r["iteration"], r["variant"], r["rep"]))
        if not trs:
            continue
        L.append(f"### {t}")
        L.append("")
        for r in trs:
            status = "PASS" if r["score_adj"] == 1.0 else ("TIMEOUT" if r["timed_out"] else ("PROTECTED-EDIT" if not r["protected_ok"] else "FAIL"))
            why = ""
            if status != "PASS":
                if not r["expected_files_present"]:
                    why = "target file never created"
                elif r["collection_error"]:
                    why = "import/collection error (module broken or wrong names)"
                elif r["failed_tests"]:
                    why = "failed: " + ", ".join(r["failed_tests"][:8]) + (" ..." if len(r["failed_tests"]) > 8 else "")
            L.append(f"- iter{r['iteration']} `{r['variant']}`{'' if r['rep'] == 0 else ' rep' + str(r['rep'])}: "
                     f"**{status}** {r['passed']}/{r['total']} in {r['wall_s']}s, {r['tool_total']} tool calls"
                     f"{', ran pytest' if r['ran_pytest'] else ', never ran tests'}. {why} "
                     f"([run folder]({Path(r['run_dir']).relative_to(Path('agents') / s).as_posix()}))")
        L.append("")
    notes = AGENTS / s / "notes.md"
    L.append("## 4. Behaviour notes (hand-written)")
    L.append("")
    L.append(notes.read_text(encoding="utf-8").strip() if notes.exists() else "_none_")
    L.append("")
    L.append("## 5. Recommended prompt recipe")
    L.append("")
    if bv:
        comps, _ = resolve_variant(bv, s)
        L.append(f"Best-performing variant `{bv}` = components `{' + '.join(comps)}`. Rendered for `t3_todo_cli`:")
        L.append("")
        L.append("```text")
        L.append(build_prompt("t3_todo_cli", bv, s).rstrip())
        L.append("```")
    L.append("")
    L.append("## 6. Sample final messages")
    L.append("")
    for label, pick in (("best", max(rs, key=lambda r: (r["score_adj"], -r["wall_s"]))),
                        ("worst", min(rs, key=lambda r: (r["score_adj"], r["wall_s"])))):
        L.append(f"**{label} run** ({pick['task']} / iter{pick['iteration']} / `{pick['variant']}`, {pick['passed']}/{pick['total']}):")
        L.append("")
        txt = (pick["final_text"] or "_(no final text)_").strip()
        L.append("> " + txt[:1500].replace("\n", "\n> "))
        L.append("")
    (AGENTS / s / "REPORT.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def write_csv(results):
    RESULTS.mkdir(exist_ok=True)
    cols = ["slug", "task", "variant", "iteration", "rep", "passed", "total", "score", "score_adj", "protected_ok",
            "timed_out", "wall_s", "steps", "tool_total", "tool_errors", "ran_pytest", "wrote_own_tests",
            "question_attempts", "final_text_len", "expected_files_present", "collection_error", "run_dir"]
    with open(RESULTS / "summary.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols + ["tokens_in", "tokens_out", "tokens_reasoning"])
        for r in sorted(results, key=lambda r: (r["slug"], r["iteration"], r["task"], r["variant"], r["rep"])):
            w.writerow([r.get(c) for c in cols] + [r["tokens"]["input"], r["tokens"]["output"], r["tokens"]["reasoning"]])


def main():
    results = load_results()
    if not results:
        print("no results yet")
        return
    write_csv(results)
    write_main(results)
    for s in sorted({r["slug"] for r in results}):
        write_agent(results, s)
    print(f"reports written for {len(results)} runs: REPORT.md, results/summary.csv, agents/*/REPORT.md")


if __name__ == "__main__":
    main()
