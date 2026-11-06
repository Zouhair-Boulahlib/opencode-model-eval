#!/usr/bin/env python3
"""Tests for todo.py using only the Python standard library (pytest)."""

import json
import os
import subprocess
import sys
import tempfile

TODO_SCRIPT = os.path.join(os.path.dirname(__file__), "todo.py")


def _run(args, tmpdir=None, todo_file=None):
    """Run todo.py with given args, return (stdout, stderr, returncode).

    If tmpdir is given, the todo.json will be placed there.
    If todo_file is given, it sets the TODO_FILE env var.
    """
    env = dict(os.environ)
    if todo_file is not None:
        env["TODO_FILE"] = todo_file
    else:
        # use a temp file in tmpdir
        pass
    result = subprocess.run(
        [sys.executable, TODO_SCRIPT] + args,
        capture_output=True,
        text=True,
        env=env,
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode


def _todo_path(tmpdir, base="todo.json"):
    """Return the full path to the todo data file."""
    return os.path.join(tmpdir, base)


def _read_tasks(path):
    """Read the todo file and return the list of tasks."""
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _cleanup_todo(tmpdir, path):
    """Remove the todo file if it exists."""
    if os.path.exists(path):
        os.remove(path)


def _make_test_dir():
    """Create a fresh temp directory for a test."""
    return tempfile.mkdtemp()


passed = 0
failed = 0


def run_test(name, fn):
    global passed, failed
    try:
        fn()
        passed += 1
        print(f"  PASS: {name}")
    except AssertionError as e:
        failed += 1
        print(f"  FAIL: {name} - {e}")
    except Exception as e:
        failed += 1
        print(f"  ERROR: {name} - {e}")


def test_add():
    tmpdir = _make_test_dir()
    todo_path = _todo_path(tmpdir)
    stdout, stderr, rc = _run(["add", "buy milk"], tmpdir=tmpdir, todo_file=todo_path)
    assert rc == 0, f"Expected exit 0, got {rc}, stderr={stderr}"
    assert stdout == "Added 1: buy milk", f"Expected 'Added 1: buy milk', got '{stdout}'"
    tasks = _read_tasks(todo_path)
    assert len(tasks) == 1
    assert tasks[0]["id"] == 1
    assert tasks[0]["text"] == "buy milk"
    assert tasks[0]["done"] is False


def test_add_multiple_words():
    tmpdir = _make_test_dir()
    todo_path = _todo_path(tmpdir)
    stdout, stderr, rc = _run(["add", "walk", "the", "dog"], tmpdir=tmpdir, todo_file=todo_path)
    assert rc == 0
    assert stdout == "Added 1: walk the dog", f"Got '{stdout}'"
    tasks = _read_tasks(todo_path)
    assert tasks[0]["text"] == "walk the dog"


def test_list_empty():
    tmpdir = _make_test_dir()
    todo_path = _todo_path(tmpdir)
    _cleanup_todo(tmpdir, todo_path)
    stdout, stderr, rc = _run(["list"], tmpdir=tmpdir, todo_file=todo_path)
    assert rc == 0
    assert stdout == "No tasks", f"Expected 'No tasks', got '{stdout}'"


def test_list_tasks():
    tmpdir = _make_test_dir()
    todo_path = _todo_path(tmpdir)
    for f in os.listdir(tmpdir):
        if f.endswith(".json"):
            os.remove(os.path.join(tmpdir, f))
    _run(["add", "task one"], tmpdir=tmpdir, todo_file=todo_path)
    _run(["add", "task two"], tmpdir=tmpdir, todo_file=todo_path)
    stdout, _, _ = _run(["list"], tmpdir=tmpdir, todo_file=todo_path)
    lines = stdout.strip().split("\n")
    assert len(lines) == 2


def test_done():
    tmpdir = _make_test_dir()
    todo_path = _todo_path(tmpdir)
    for f in os.listdir(tmpdir):
        if f.endswith(".json"):
            os.remove(os.path.join(tmpdir, f))
    _run(["add", "clean room"], tmpdir=tmpdir, todo_file=todo_path)
    _, _, rc = _run(["done", "1"], tmpdir=tmpdir, todo_file=todo_path)
    assert rc == 0
    assert "Done 1" in _run(["done", "1"], tmpdir=tmpdir, todo_file=todo_path)[0]
    stdout, _, _ = _run(["list"], tmpdir=tmpdir, todo_file=todo_path)
    assert "[x] 1: clean room" in stdout


def test_done_already_done():
    tmpdir = _make_test_dir()
    todo_path = _todo_path(tmpdir)
    for f in os.listdir(tmpdir):
        if f.endswith(".json"):
            os.remove(os.path.join(tmpdir, f))
    _run(["add", "task"], tmpdir=tmpdir, todo_file=todo_path)
    _run(["done", "1"], tmpdir=tmpdir, todo_file=todo_path)
    _, _, rc = _run(["done", "1"], tmpdir=tmpdir, todo_file=todo_path)
    assert rc == 0
    assert "Done 1" in _run(["done", "1"], tmpdir=tmpdir, todo_file=todo_path)[0]


def test_remove():
    tmpdir = _make_test_dir()
    todo_path = _todo_path(tmpdir)
    for f in os.listdir(tmpdir):
        if f.endswith(".json"):
            os.remove(os.path.join(tmpdir, f))
    _run(["add", "delete me"], tmpdir=tmpdir, todo_file=todo_path)
    _, _, rc = _run(["remove", "1"], tmpdir=tmpdir, todo_file=todo_path)
    assert rc == 0
    assert "Removed 1" in _run(["remove", "1"], tmpdir=tmpdir, todo_file=todo_path)[0]
    stdout, _, _ = _run(["list"], tmpdir=tmpdir, todo_file=todo_path)
    assert stdout == "No tasks"


def test_remove_nonexistent():
    tmpdir = _make_test_dir()
    todo_path = _todo_path(tmpdir)
    _cleanup_todo(tmpdir, todo_path)
    stdout, stderr, rc = _run(["remove", "999"], tmpdir=tmpdir, todo_file=todo_path)
    assert rc == 1
    assert stderr == "Error: no task 999", f"Expected 'Error: no task 999', got '{stderr}'"
    assert stdout == ""


def test_clear():
    tmpdir = _make_test_dir()
    todo_path = _todo_path(tmpdir)
    for f in os.listdir(tmpdir):
        if f.endswith(".json"):
            os.remove(os.path.join(tmpdir, f))
    _run(["add", "task one"], tmpdir=tmpdir, todo_file=todo_path)
    _run(["add", "task two"], tmpdir=tmpdir, todo_file=todo_path)
    _run(["done", "1"], tmpdir=tmpdir, todo_file=todo_path)
    _, _, rc = _run(["clear"], tmpdir=tmpdir, todo_file=todo_path)
    assert rc == 0
    assert "Cleared 1" in _run(["clear"], tmpdir=tmpdir, todo_file=todo_path)[0]
    stdout, _, _ = _run(["list"], tmpdir=tmpdir, todo_file=todo_path)
    assert "[ ] 2: task two" in stdout or "[x] 2: task two" in stdout


def test_clear_no_done():
    tmpdir = _make_test_dir()
    todo_path = _todo_path(tmpdir)
    for f in os.listdir(tmpdir):
        if f.endswith(".json"):
            os.remove(os.path.join(tmpdir, f))
    _run(["add", "task"], tmpdir=tmpdir, todo_file=todo_path)
    _, _, rc = _run(["clear"], tmpdir=tmpdir, todo_file=todo_path)
    assert rc == 0
    assert "Cleared 0" in _run(["clear"], tmpdir=tmpdir, todo_file=todo_path)[0]


def test_id_not_reused():
    tmpdir = _make_test_dir()
    todo_path = _todo_path(tmpdir)
    for f in os.listdir(tmpdir):
        if f.endswith(".json"):
            os.remove(os.path.join(tmpdir, f))
    _run(["add", "first"], tmpdir=tmpdir, todo_file=todo_path)
    _run(["remove", "1"], tmpdir=tmpdir, todo_file=todo_path)
    _, _, rc = _run(["add", "second"], tmpdir=tmpdir, todo_file=todo_path)
    assert rc == 0
    tasks = _read_tasks(todo_path)
    assert tasks[0]["id"] == 2, f"Expected id 2, got {tasks[0]['id']}"


def test_error_nonexistent_task_done():
    tmpdir = _make_test_dir()
    todo_path = _todo_path(tmpdir)
    _cleanup_todo(tmpdir, todo_path)
    stdout, stderr, rc = _run(["done", "5"], tmpdir=tmpdir, todo_file=todo_path)
    assert rc == 1
    assert stderr == "Error: no task 5", f"Expected 'Error: no task 5', got '{stderr}'"
    assert stdout == ""


def test_error_nonexistent_task_remove():
    tmpdir = _make_test_dir()
    todo_path = _todo_path(tmpdir)
    _cleanup_todo(tmpdir, todo_path)
    stdout, stderr, rc = _run(["remove", "3"], tmpdir=tmpdir, todo_file=todo_path)
    assert rc == 1
    assert stderr == "Error: no task 3", f"Expected 'Error: no task 3', got '{stderr}'"
    assert stdout == ""


def test_unknown_command():
    tmpdir = _make_test_dir()
    todo_path = _todo_path(tmpdir)
    _cleanup_todo(tmpdir, todo_path)
    stdout, stderr, rc = _run(["foo"], tmpdir=tmpdir, todo_file=todo_path)
    assert rc == 2
    assert stderr == "Usage: todo.py <add|list|done|remove|clear> ...", f"Got '{stderr}'"


def test_missing_command():
    tmpdir = _make_test_dir()
    todo_path = _todo_path(tmpdir)
    _cleanup_todo(tmpdir, todo_path)
    stdout, stderr, rc = _run([], tmpdir=tmpdir, todo_file=todo_path)
    assert rc == 2
    assert stderr == "Usage: todo.py <add|list|done|remove|clear> ...", f"Got '{stderr}'"