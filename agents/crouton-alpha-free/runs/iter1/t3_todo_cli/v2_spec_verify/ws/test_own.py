import os
import subprocess
import sys

import pytest

TODO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "todo.py")
USAGE = "Usage: todo.py <add|list|done|remove|clear> ..."


def run(tmp_path, *args, use_env=True):
    env = os.environ.copy()
    f = tmp_path / "todo.json"
    if use_env:
        env["TODO_FILE"] = str(f)
    else:
        env.pop("TODO_FILE", None)
    # Use cwd=tmp_path so default todo.json also lands there
    r = subprocess.run(
        [sys.executable, TODO, *args],
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
        env=env,
    )
    return r


def test_missing_file_list(tmp_path):
    r = run(tmp_path, "list")
    assert r.returncode == 0
    assert r.stdout == "No tasks\n"
    assert r.stderr == ""


def test_add_and_list(tmp_path):
    r = run(tmp_path, "add", "buy", "milk")
    assert r.returncode == 0
    assert r.stdout == "Added 1: buy milk\n"
    assert r.stderr == ""
    r = run(tmp_path, "add", "walk", "dog")
    assert r.stdout == "Added 2: walk dog\n"
    r = run(tmp_path, "list")
    assert r.stdout == "[ ] 1: buy milk\n[ ] 2: walk dog\n"


def test_done_and_idempotent(tmp_path):
    run(tmp_path, "add", "a")
    r = run(tmp_path, "done", "1")
    assert r.returncode == 0
    assert r.stdout == "Done 1\n"
    r = run(tmp_path, "done", "1")
    assert r.returncode == 0
    assert r.stdout == "Done 1\n"
    r = run(tmp_path, "list")
    assert r.stdout == "[x] 1: a\n"


def test_remove_and_id_not_reused(tmp_path):
    run(tmp_path, "add", "a")
    run(tmp_path, "add", "b")
    r = run(tmp_path, "remove", "1")
    assert r.returncode == 0
    assert r.stdout == "Removed 1\n"
    r = run(tmp_path, "add", "c")
    assert r.stdout == "Added 3: c\n"
    r = run(tmp_path, "list")
    assert r.stdout == "[ ] 2: b\n[ ] 3: c\n"


def test_clear_only_done_and_id_not_reused(tmp_path):
    run(tmp_path, "add", "a")
    run(tmp_path, "add", "b")
    run(tmp_path, "add", "c")
    run(tmp_path, "done", "1")
    run(tmp_path, "done", "3")
    r = run(tmp_path, "clear")
    assert r.returncode == 0
    assert r.stdout == "Cleared 2\n"
    r = run(tmp_path, "list")
    assert r.stdout == "[ ] 2: b\n"
    r = run(tmp_path, "add", "d")
    assert r.stdout == "Added 4: d\n"
    r = run(tmp_path, "clear")
    assert r.stdout == "Cleared 0\n"


def test_not_found(tmp_path):
    run(tmp_path, "add", "a")
    for cmd in ("done", "remove"):
        r = run(tmp_path, cmd, "999")
        assert r.returncode == 1
        assert r.stdout == ""
        assert r.stderr == "Error: no task 999\n"


def test_usage_errors(tmp_path):
    cases = [
        (),
        ("unknown",),
        ("add",),
        ("done",),
        ("done", "abc"),
        ("done", "1", "extra"),
        ("remove",),
        ("remove", "x"),
        ("list", "extra"),
        ("clear", "extra"),
    ]
    for args in cases:
        r = run(tmp_path, *args)
        assert r.returncode == 2, args
        assert r.stdout == "", args
        assert r.stderr == USAGE + "\n", args


def test_default_path(tmp_path):
    r = run(tmp_path, "add", "hello", use_env=False)
    assert r.returncode == 0
    assert r.stdout == "Added 1: hello\n"
    assert (tmp_path / "todo.json").exists()
    r = run(tmp_path, "list", use_env=False)
    assert r.stdout == "[ ] 1: hello\n"
