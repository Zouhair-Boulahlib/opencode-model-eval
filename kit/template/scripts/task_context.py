#!/usr/bin/env python3
"""Print the part of the graphify architecture map that matters for a task or a question.

    python scripts/task_context.py .opencode/tasks/<name>.md     # the contract, then its code map
    python scripts/task_context.py --query "<question>"           # the code map for a question
    options: --budget <chars> (default 6000)  --hops <n> (default 1)  --seeds <n> (default 8)

Works directly on graphify-out/graph.json (NetworkX node-link format written by graph_refresh.py).
If the graph is missing it says so and exits 0, so prompts that embed this script still work.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GRAPH = ROOT / "graphify-out" / "graph.json"
REPORT = ROOT / "graphify-out" / "GRAPH_REPORT.md"
STOP = {"the", "and", "for", "with", "that", "this", "from", "into", "when", "then", "than", "must", "should",
        "not", "are", "is", "a", "an", "of", "to", "in", "on", "it", "its", "be", "by", "or", "as", "at", "all",
        "any", "each", "only", "file", "files", "function", "functions", "module", "modules", "code", "task",
        "create", "modify", "does", "do", "have", "has", "will", "can", "may", "use", "using", "used", "new"}


def tokens(text: str) -> set[str]:
    words = re.findall(r"[A-Za-z_][A-Za-z0-9_]{2,}", text)
    out: set[str] = set()
    for w in words:
        out.add(w.lower())
        for part in re.split(r"_|(?<=[a-z0-9])(?=[A-Z])", w):
            if len(part) >= 3:
                out.add(part.lower())
    return {t for t in out if t not in STOP}


def node_tokens(n: dict) -> set[str]:
    return tokens(f"{n.get('label', '')} {n.get('id', '')} {n.get('source_file', '')}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("contract", nargs="?", help="path of a task contract .md file")
    ap.add_argument("--query", help="free-text question instead of a contract file")
    ap.add_argument("--budget", type=int, default=6000)
    ap.add_argument("--hops", type=int, default=1)
    ap.add_argument("--seeds", type=int, default=8)
    a = ap.parse_args()

    text = ""
    if a.contract:
        p = Path(a.contract)
        if not p.is_absolute():
            p = ROOT / p
        if not p.exists():
            print(f"[task_context] contract not found: {p}")
            return
        contract = p.read_text(encoding="utf-8")
        print(contract.rstrip())
        print("\n" + "=" * 72 + "\n")
        text = contract
    if a.query:
        text = (text + "\n" + a.query) if text else a.query
    if not text.strip():
        print("[task_context] give a contract path or --query")
        return
    if not GRAPH.exists():
        print("[task_context] no graphify-out/graph.json yet: run `python scripts/graph_refresh.py` to build the map.")
        return

    g = json.loads(GRAPH.read_text(encoding="utf-8"))
    nodes = {n["id"]: n for n in g.get("nodes", [])}
    links = g.get("links", g.get("edges", []))
    adj: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for e in links:
        s, t = e.get("source"), e.get("target")
        rel = e.get("relation") or e.get("type") or "related"
        if s in nodes and t in nodes:
            adj[s].append((t, rel))
            adj[t].append((s, rel))
    q = tokens(text)
    scored = []
    for nid, n in nodes.items():
        nt = node_tokens(n)
        overlap = len(q & nt)
        if overlap:
            scored.append((overlap + 0.01 * len(adj[nid]), nid))
    scored.sort(reverse=True)
    seeds = [nid for _, nid in scored[: a.seeds]]
    if not seeds:
        print("[task_context] no symbol in the map matches the task words; here are the god nodes instead.")
        seeds = [nid for nid, _ in sorted(((n, len(adj[n])) for n in nodes), key=lambda x: -x[1])[: a.seeds]]

    selected = set(seeds)
    frontier = set(seeds)
    for _ in range(a.hops):
        nxt = set()
        for nid in frontier:
            for t, _ in adj[nid]:
                if t not in selected:
                    nxt.add(t)
        selected |= nxt
        frontier = nxt

    by_file: dict[str, list[str]] = defaultdict(list)
    for nid in selected:
        n = nodes[nid]
        by_file[(n.get("source_file") or "(external)").replace("\\", "/")].append(nid)
    comms = sorted({nodes[n].get("community_name") for n in selected if nodes[n].get("community_name")})

    out: list[str] = []
    label = a.query or Path(a.contract).name
    out.append(f"CODE MAP (graphify) for: {label}")
    out.append("Communities touched: " + ("; ".join(comms) if comms else "n/a"))
    out.append("Start here (best matching symbols): " + ", ".join(f"{nodes[s].get('label', s)} [{(nodes[s].get('source_file') or '').replace(chr(92), '/')}]" for s in seeds[:5]))
    out.append("")
    # files ordered by number of seed symbols they hold
    def file_rank(f: str) -> tuple[int, int]:
        ids = by_file[f]
        return (-sum(1 for i in ids if i in seeds), -len(ids))
    for f in sorted(by_file, key=file_rank):
        if f == "(external)":
            continue
        ids = by_file[f]
        cname = next((nodes[i].get("community_name") for i in ids if nodes[i].get("community_name")), "")
        out.append(f"{f}  [{cname}]" if cname else f)
        for nid in sorted(ids, key=lambda i: (i not in seeds, -len(adj[i]))):
            n = nodes[nid]
            rels = defaultdict(list)
            for t, rel in adj[nid]:
                if t in nodes and nodes[t].get("source_file") != n.get("source_file"):
                    rels[rel].append(nodes[t].get("label", t))
            rel_txt = "; ".join(f"{rel}: {', '.join(sorted(set(v))[:4])}" for rel, v in sorted(rels.items())[:3])
            mark = "*" if nid in seeds else "-"
            loc = f" ({n['source_location']})" if n.get("source_location") else ""
            out.append(f"  {mark} {n.get('label', nid)}{loc}" + (f"  <- {rel_txt}" if rel_txt else ""))
    text_out = "\n".join(out)
    if REPORT.exists():
        rep = REPORT.read_text(encoding="utf-8")
        m = re.search(r"## God Nodes.*?(?=\n## )", rep, re.S)
        if m:
            text_out += "\n\n" + m.group(0).strip()
    if len(text_out) > a.budget:
        text_out = text_out[: a.budget].rsplit("\n", 1)[0] + "\n[... map truncated to budget ...]"
    print(text_out)


if __name__ == "__main__":
    main()
