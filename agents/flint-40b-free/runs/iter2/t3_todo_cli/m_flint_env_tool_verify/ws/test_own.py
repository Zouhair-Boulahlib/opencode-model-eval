import json
import os
import subprocess
import sys

import pytest

TODO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "todo.py")
USAGE = "Usage: todo.py <add|list|done|remove|clear> ...\n"


def run_todo(tmp_path, *args, use_default_file=False):
    env = dict(os.environ)
    if use_default_file:
        env.pop("TODO_FILE", None)
    else:
        env["TODO_FILE"] = str(tmp_path / "todo.json")
    return subprocess.run(
        [sys.executable, TODO, *args],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(tmp_path),
    )


def test_add_creates_task(tmp_path):
    proc = run_todo(tmp_path, "add", "buy", "milk")
    assert proc.returncode == 0
    assert proc.stdout == "Added 1: buy milk\n"
    assert proc.stderr == ""
    data = json.loads((tmp_path / "todo.json").read_text())
    assert data["tasks"] == [{"id": 1, "text": "buy milk", "done": False}]
    assert data["next_id"] == 2


def test_add_joins_words_with_single_space(tmp_path):
    proc = run_todo(tmp_path, "add", "walk", "the", "dog")
    assert proc.returncode == 0
    assert proc.stdout == "Added 1: walk the dog\n"


def test_list_empty(tmp_path):
    proc = run_todo(tmp_path, "list")
    assert proc.returncode == 0
    assert proc.stdout == "No tasks\n"
    assert proc.stderr == ""


def test_list_open_task_format(tmp_path):
    proc = run_todo(tmp_path, "add", "buy", "milk")
    assert proc.returncode == 0
    proc = run_todo(tmp_path, "list")
    assert proc.returncode == 0
    assert proc.stdout == "[ ] 1: buy milk\n"
    assert proc.stderr == ""


def test_done_marks_task_done(tmp_path):
    run_todo(tmp_path, "add", "buy", "milk")
    proc = run_todo(tmp_path, "done", "1")
    assert proc.returncode == 0
    assert proc.stdout == "Done 1\n"
    assert proc.stderr == ""
    proc = run_todo(tmp_path, "list")
    assert proc.returncode == 0
    assert proc.stdout == "[x] 1: buy milk\n"


def test_done_twice_is_idempotent(tmp_path):
    run_todo(tmp_path, "add", "buy", "milk")
    run_todo(tmp_path, "done", "1")
    proc = run_todo(tmp_path, "done", "1")
    assert proc.returncode == 0
    assert proc.stdout == "Done 1\n"


def test_done_missing_task_errors(tmp_path):
    proc = run_todo(tmp_path, "done", "42")
    assert proc.returncode == 1
    assert proc.stdout == ""
    assert proc.stderr == "Error: no task 42\n"


def test_remove_deletes_task(tmp_path):
    run_todo(tmp_path, "add", "buy", "milk")
    run_todo(tmp_path, "add", "walk", "dog")
    proc = run_todo(tmp_path, "remove", "1")
    assert proc.returncode == 0
    assert proc.stdout == "Removed 1\n"
    proc = run_todo(tmp_path, "list")
    assert proc.returncode == 0
    assert proc.stdout == "[ ] 2: walk dog\n"


def test_remove_missing_task_errors(tmp_path):
    proc = run_todo(tmp_path, "remove", "7")
    assert proc.returncode == 1
    assert proc.stdout == ""
    assert proc.stderr == "Error: no task 7\n"


def test_clear_removes_done_tasks(tmp_path):
    run_todo(tmp_path, "add", "buy", "milk")
    run_todo(tmp_path, "add", "walk", "dog")
    run_todo(tmp_path, "done", "1")
    proc = run_todo(tmp_path, "clear")
    assert proc.returncode == 0
    assert proc.stdout == "Cleared 1\n"
    proc = run_todo(tmp_path, "list")
    assert proc.returncode == 0
    assert proc.stdout == "[ ] 2: walk dog\n"


def test_clear_with_no_done_tasks(tmp_path):
    run_todo(tmp_path, "add", "buy", "milk")
    proc = run_todo(tmp_path, "clear")
    assert proc.returncode == 0
    assert proc.stdout == "Cleared 0\n"


def test_ids_not_reused_after_remove(tmp_path):
    run_todo(tmp_path, "add", "buy", "milk")
    run_todo(tmp_path, "remove", "1")
    proc = run_todo(tmp_path, "add", "new", "task")
    assert proc.returncode == 0
    assert proc.stdout == "Added 2: new task\n"


def test_ids_not_reused_after_clear(tmp_path):
    run_todo(tmp_path, "add", "buy", "milk")
    run_todo(tmp_path, "done", "1")
    run_todo(tmp_path, "clear")
    proc = run_todo(tmp_path, "add", "new", "task")
    assert proc.returncode == 0
    assert proc.stdout == "Added 2: new task\n"


def test_unknown_command(tmp_path):
    proc = run_todo(tmp_path, "frobnicate")
    assert proc.returncode == 2
    assert proc.stdout == ""
    assert proc.stderr == USAGE


def test_missing_command(tmp_path):
    proc = run_todo(tmp_path)
    assert proc.returncode == 2
    assert proc.stdout == ""
    assert proc.stderr == USAGE


def test_add_without_args(tmp_path):
    proc = run_todo(tmp_path, "add")
    assert proc.returncode == 2
    assert proc.stdout == ""
    assert proc.stderr == USAGE


def test_done_invalid_id(tmp_path):
    proc = run_todo(tmp_path, "done", "abc")
    assert proc.returncode == 2
    assert proc.stdout == ""
    assert proc.stderr == USAGE


def test_remove_missing_id(tmp_path):
    proc = run_todo(tmp_path, "remove")
    assert proc.returncode == 2
    assert proc.stdout == ""
    assert proc.stderr == USAGE


def test_clear_rejects_extra_args(tmp_path):
    proc = run_todo(tmp_path, "clear", "extra")
    assert proc.returncode == 2
    assert proc.stdout == ""
    assert proc.stderr == USAGE


def test_uses_todo_json_in_cwd_by_default(tmp_path):
    proc = run_todo(tmp_path, "add", "default", "path", use_default_file=True)
    assert proc.returncode == 0
    assert proc.stdout == "Added 1: default path\n"
    assert (tmp_path / "todo.json").exists()
