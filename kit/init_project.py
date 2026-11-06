#!/usr/bin/env python3
"""Set up a project for graph-engineered development with OpenCode.

    python kit/init_project.py <project-dir> [--model provider/model] [--no-graph] [--force]

Copies the template (AGENTS.md, .opencode/{agents,commands,tasks}, scripts/, opencode.json) into the
project without overwriting files that already exist (unless --force), merges the needed keys into an
existing opencode.json, appends graphify entries to .gitignore, builds the architecture map, and
prints the next steps. Safe to rerun: it only adds what is missing.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent
TEMPLATE = KIT / "template"
GITIGNORE_LINES = ["graphify-out/.graphify_*", "graphify-out/cost.json", "graphify-out/manifest.json",
                   ".opencode/runs/", "__pycache__/", ".pytest_cache/"]


def copy_tree(src: Path, dst: Path, force: bool) -> tuple[int, int]:
    added = kept = 0
    for p in src.rglob("*"):
        if p.is_dir():
            continue
        rel = p.relative_to(src)
        target = dst / rel
        if target.exists() and not force:
            kept += 1
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, target)
        added += 1
    return added, kept


def merge_opencode_json(target: Path, model: str | None) -> str:
    tpl = json.loads((TEMPLATE / "opencode.json").read_text(encoding="utf-8"))
    if model:
        tpl["model"] = model
    if not target.exists():
        target.write_text(json.dumps(tpl, indent=2) + "\n", encoding="utf-8")
        return "created"
    try:
        cur = json.loads(target.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return "left as is (existing opencode.json is not valid JSON; merge the template by hand)"
    changed = False
    for key in ("$schema", "model", "default_agent"):
        if key not in cur:
            cur[key] = tpl[key]
            changed = True
    if model and cur.get("model") != model:
        cur["model"] = model
        changed = True
    ins = list(cur.get("instructions", []))
    for item in tpl["instructions"]:
        if item not in ins:
            ins.append(item)
            changed = True
    cur["instructions"] = ins
    perm = dict(cur.get("permission", {}))
    for k, v in tpl["permission"].items():
        if k not in perm:
            perm[k] = v
            changed = True
    cur["permission"] = perm
    if changed:
        target.write_text(json.dumps(cur, indent=2) + "\n", encoding="utf-8")
    return "merged" if changed else "already complete"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--model", help="provider/model for the project default (builder agent keeps its own unless you edit it)")
    ap.add_argument("--no-graph", action="store_true", help="skip building the graphify map now")
    ap.add_argument("--force", action="store_true", help="overwrite template files that already exist")
    a = ap.parse_args()
    project = Path(a.project).resolve()
    if not project.is_dir():
        sys.exit(f"not a directory: {project}")
    if " " in str(project):
        print("note: the project path contains a space; the AGENTS.md rules tell agents to quote paths, "
              "but a path without spaces avoids a whole class of model mistakes.")
    added, kept = 0, 0
    for sub in ("AGENTS.md", ".opencode", "scripts"):
        src = TEMPLATE / sub
        if src.is_file():
            target = project / sub
            if target.exists() and not a.force:
                kept += 1
            else:
                shutil.copy2(src, target)
                added += 1
        else:
            x, y = copy_tree(src, project / sub, a.force)
            added += x
            kept += y
    status = merge_opencode_json(project / "opencode.json", a.model)
    gi = project / ".gitignore"
    existing = gi.read_text(encoding="utf-8").splitlines() if gi.exists() else []
    missing = [ln for ln in GITIGNORE_LINES if ln not in existing]
    if missing:
        with open(gi, "a", encoding="utf-8") as f:
            if existing and existing[-1].strip():
                f.write("\n")
            f.write("# graph-engineered dev kit\n" + "\n".join(missing) + "\n")
    print(f"template files: {added} added, {kept} kept (use --force to overwrite); opencode.json {status}; "
          f".gitignore +{len(missing)} lines")
    if not a.no_graph:
        r = subprocess.run([sys.executable, str(project / "scripts" / "graph_refresh.py")], cwd=str(project),
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        print(r.stdout.strip() or r.stderr.strip())
        if r.returncode != 0:
            print("graph build failed; fix the message above and rerun: python scripts/graph_refresh.py")
    print("\nNext steps:")
    print(f"  1. cd \"{project}\" && opencode        # agents: builder (default), @navigator, @reviewer; commands: /task /map /graph /review")
    print("  2. cp .opencode/tasks/TEMPLATE.md .opencode/tasks/my-task.md and fill the contract")
    print("  3. /map <question>  ->  /task my-task  ->  /review my-task   (or: python scripts/run_task.py .opencode/tasks/my-task.md)")
    print("  4. after structural changes: /graph  (or python scripts/graph_refresh.py)")


if __name__ == "__main__":
    main()
