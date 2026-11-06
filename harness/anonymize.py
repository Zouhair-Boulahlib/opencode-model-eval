#!/usr/bin/env python3
"""Replace the author's machine user name in text files with the placeholder USER.

Walks agents/, results/, harness/ and the top-level REPORT.md / README.md and rewrites
text files (.json .jsonl .txt .md .log .xml .csv .py .sh, plus the extension-less graphify
marker files) in place. Replacements are case-sensitive, applied in the order below, and
idempotent: a second run changes nothing. Binary files, .git/, __pycache__/,
results/_probe/ and results/_selftest/ are skipped, as is this file (it has to contain the
patterns it replaces).

Usage: python harness/anonymize.py
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SELF = Path(__file__).resolve()

BS = chr(92)  # a single backslash


def win_path(sep: str) -> str:
    return "C:" + sep + "Users" + sep + "zouhair"


# (pattern, replacement), applied in this order:
#   1. the JSON-escaped form with two backslashes between components
#   2. the plain Windows form with single backslashes
#   3. forward-slash Windows form, 4. Git Bash form
#   5. extras: the form nested one JSON level deeper (four backslashes), and the form with
#      the backslashes stripped by a shell
#   6. the bare user name, wherever it is left
PATTERNS: list[tuple[str, str]] = [
    (win_path(BS * 2), win_path(BS * 2).replace("zouhair", "USER")),
    (win_path(BS), win_path(BS).replace("zouhair", "USER")),
    ("C:/Users/zouhair", "C:/Users/USER"),
    ("/c/Users/zouhair", "/c/Users/USER"),
    (win_path(BS * 4), win_path(BS * 4).replace("zouhair", "USER")),
    (win_path(""), win_path("").replace("zouhair", "USER")),
    # 6. final catch-all for the bare user name (ls -l owner column, pytest temp dirs such as
    #    pytest-of-<name>, claude project-folder names, paths that start at "Users")
    ("zouhair", "USER"),
    # 7. machine hostname (pytest writes it into junit.xml) and an unrelated project folder that
    #    one model listed with `find /`
    ("DESKTOP-FS733RS", "HOST"),
    ("C--Users-USER-Documents-psp/5f873398-6a61-42ff-9e14-5f02ddffa837", "OTHER-PROJECT/SESSION"),
    ("C--Users-USER-Documents-psp", "OTHER-PROJECT"),
]

SCAN = ["agents", "results", "harness", "REPORT.md", "README.md"]
EXTENSIONS = {".json", ".jsonl", ".txt", ".md", ".log", ".xml", ".csv", ".py", ".sh"}
EXTRA_NAMES = {".graphify_root", ".graphify_python"}
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache"}
SKIP_PATHS = [ROOT / "results" / "_probe", ROOT / "results" / "_selftest"]


def is_skipped(path: Path) -> bool:
    if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
        return True
    return any(p == path or p in path.parents for p in SKIP_PATHS)


def iter_files():
    for name in SCAN:
        base = ROOT / name
        if base.is_file():
            yield base
        elif base.is_dir():
            for p in sorted(base.rglob("*")):
                if p.is_file() and not is_skipped(p):
                    yield p


def main() -> None:
    subs = [(a.encode(), b.encode()) for a, b in PATTERNS]
    seen = changed = 0
    for path in iter_files():
        if path.resolve() == SELF:
            continue
        if path.suffix.lower() not in EXTENSIONS and path.name not in EXTRA_NAMES:
            continue
        data = path.read_bytes()
        if b"\x00" in data[:8192]:  # binary
            continue
        seen += 1
        new = data
        for a, b in subs:
            new = new.replace(a, b)
        if new != data:
            path.write_bytes(new)
            changed += 1
    print(f"scanned {seen} text files, changed {changed}")


if __name__ == "__main__":
    main()
