import json
import os
import subprocess
import sys

import pytest

SCRIPT = os.path.join(os.path.dirname(__file__), "todo.py")


@pytest.fixture
def run(tmp_path):
    env = os.environ.copy()
    env["TODO_FILE"] = str(tmp_path / "tasks.json")

    def _run(*args):
        return subprocess.run(
            [sys.executable, SCRIPT, *args],
            capture_output=True,
            text=True,
            env=env,
            cwd=str(tmp_path),
        )

    return _run


def test_list_empty(run):
    r = run("list")
    assert r.returncode == 0
    assert r.stdout == "No tasks\n"
    assert r.stderr == ""


def test_add_and_list(run):
    r = run("add", "buy", "milk")
    assert (r.returncode, r.stdout, r.stderr) == (0, "Added 1: buy milk\n", "")
    r = run("add", "walk", "dog")
    assert r.stdout == "Added 2: walk dog\n"
    r = run("list")
    assert r.stdout == "[ ] 1: buy milk\n[ ] 2: walk dog\n"


def test_done(run):
    run("add", "task")
    r = run("done", "1")
    assert (r.returncode, r.stdout) == (0, "Done 1\n")
    assert run("list").stdout == "[x] 1: task\n"
    r = run("done", "1")
    assert (r.returncode, r.stdout) == (0, "Done 1\n")


def test_remove_and_id_not_reused(run):
    run("add", "a")
    run("add", "b")
    r = run("remove", "1")
    assert (r.returncode, r.stdout) == (0, "Removed 1\n")
    assert run("list").stdout == "[ ] 2: b\n"
    assert run("add", "c").stdout == "Added 3: c\n"


def test_clear(run):
    run("add", "a")
    run("add", "b")
    run("add", "c")
    run("done", "1")
    run("done", "3")
    r = run("clear")
    assert (r.returncode, r.stdout) == (0, "Cleared 2\n")
    assert run("list").stdout == "[ ] 2: b\n"
    assert run("add", "d").stdout == "Added 4: d\n"
    r = run("clear")
    assert (r.returncode, r.stdout) == (0, "Cleared 0\n")


@pytest.mark.parametrize("cmd", ["done", "remove"])
def test_missing_task(run, cmd):
    r = run(cmd, "99")
    assert r.returncode == 1
    assert r.stdout == ""
    assert r.stderr == "Error: no task 99\n"


@pytest.mark.parametrize(
    "args",
    [
        (),
        ("bogus",),
        ("add",),
        ("done",),
        ("done", "abc"),
        ("done", "0", "1"),
        ("remove",),
        ("remove", "x"),
        ("clear", "extra"),
        ("list", "extra"),
    ],
)
def test_usage_errors(run, args):
    r = run(*args)
    assert r.returncode == 2
    assert r.stdout == ""
    assert r.stderr == "Usage: todo.py <add|list|done|remove|clear> ...\n"


def test_missing_file_means_no_tasks(run, tmp_path):
    assert not (tmp_path / "tasks.json").exists()
    assert run("list").stdout == "No tasks\n"
    assert not (tmp_path / "tasks.json").exists()


def test_default_path_in_cwd(tmp_path):
    env = os.environ.copy()
    env.pop("TODO_FILE", None)
    r = subprocess.run(
        [sys.executable, SCRIPT, "add", "hi"],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(tmp_path),
    )
    assert r.stdout == "Added 1: hi\n"
    assert (tmp_path / "todo.json").exists()
