#!/usr/bin/env python3
"""Build or refresh the graphify architecture map of this project, headless and without any LLM.

Writes graphify-out/GRAPH_REPORT.md (the map the agents read), graphify-out/graph.json (the graph
task_context.py queries) and graphify-out/.graphify_labels.json. Only code files are extracted
(AST-based, deterministic); documents are listed but not semantically extracted, which keeps the
refresh free and fast. Run it from anywhere: paths are resolved from this file's location.

    python scripts/graph_refresh.py            # build or rebuild
    python scripts/graph_refresh.py --force    # rebuild even if the graph would shrink (files deleted)
"""
from __future__ import annotations

import json
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "graphify-out"


def auto_label(G, members: list[str]) -> str:
    """Deterministic community name: dominant directory plus the two most connected symbols."""
    dirs = Counter()
    for m in members:
        src = (G.nodes[m].get("source_file") or "").replace("\\", "/")
        if src:
            dirs[src.rsplit("/", 1)[0] if "/" in src else "(root)"] += 1
    top_dir = dirs.most_common(1)[0][0] if dirs else "misc"
    ranked = sorted(members, key=lambda n: G.degree(n), reverse=True)
    syms = [G.nodes[n].get("label") or n for n in ranked[:2]]
    return f"{top_dir}: {', '.join(syms)}" if syms else top_dir


def main() -> None:
    force = "--force" in sys.argv
    try:
        from graphify.analyze import god_nodes, suggest_questions, surprising_connections
        from graphify.build import build_from_json
        from graphify.cluster import cluster, score_all
        from graphify.detect import detect
        from graphify.export import to_json
        from graphify.extract import collect_files, extract
        from graphify.report import generate
    except ImportError:
        sys.exit("graphify is not installed for this interpreter: pip install graphifyy")
    t0 = time.time()
    OUT.mkdir(exist_ok=True)
    det = detect(ROOT)
    code_files: list[Path] = []
    for f in det.get("files", {}).get("code", []):
        p = Path(f)
        code_files += collect_files(p) if p.is_dir() else [p]
    code_files = [p for p in code_files if OUT not in p.parents and ".opencode" not in p.parts]
    skipped_docs = sum(len(det.get("files", {}).get(k, [])) for k in ("document", "paper", "image", "video"))
    if not code_files:
        sys.exit("no code files detected under " + str(ROOT))
    ext = extract(code_files, cache_root=ROOT)
    ext.setdefault("hyperedges", [])
    ext.setdefault("input_tokens", 0)
    ext.setdefault("output_tokens", 0)
    G = build_from_json(ext, root=str(ROOT), directed=False)
    if G.number_of_nodes() == 0:
        sys.exit("graph is empty: extraction produced no nodes")
    comms = cluster(G)
    coh = score_all(G, comms)
    gods = god_nodes(G)
    surprises = surprising_connections(G, comms)
    labels = {cid: auto_label(G, members) for cid, members in comms.items()}
    questions = suggest_questions(G, comms, labels)
    target = OUT / "graph.json"
    if force and target.exists():
        target.unlink()
    wrote = to_json(G, comms, str(target), community_labels=labels)
    if not wrote:
        sys.exit("refused to overwrite graph.json with a smaller graph (files deleted?); rerun with --force")
    report = generate(G, comms, coh, labels, gods, surprises, det, {"input": 0, "output": 0}, str(ROOT),
                      suggested_questions=questions)
    (OUT / "GRAPH_REPORT.md").write_text(report, encoding="utf-8")
    (OUT / ".graphify_labels.json").write_text(json.dumps({str(k): v for k, v in labels.items()}, ensure_ascii=False),
                                              encoding="utf-8")
    def god_name(g) -> str:
        nid = g.get("id") if isinstance(g, dict) else (g[0] if isinstance(g, (list, tuple)) else g)
        if nid in G.nodes:
            return f"{G.nodes[nid].get('label', nid)} ({G.degree(nid)})"
        return str(g.get("label", nid) if isinstance(g, dict) else nid)

    top = ", ".join(god_name(g) for g in gods[:5])
    print(f"graphify map rebuilt in {time.time() - t0:.1f}s: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges, "
          f"{len(comms)} communities, {len(code_files)} code files ({skipped_docs} non-code files not extracted)")
    print("god nodes:", top)
    print("written:", OUT / "GRAPH_REPORT.md")


if __name__ == "__main__":
    main()
