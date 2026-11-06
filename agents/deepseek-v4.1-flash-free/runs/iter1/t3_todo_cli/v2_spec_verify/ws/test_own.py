import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "todo.py")


@pytest.fixture
def todo(tmp_path):
    env = dict(os.environ)
    env["TODO_FILE"] = str(tmp_path / "tasks.json")

    def run(*args):
        return subprocess.run(
            [sys.executable, SCRIPT, *args],
            cwd=str(tmp_path),
            env=env,
            capture_output=True,
            text=True,
        )

    return run


def test_list_empty(todo):
    r = todo("list")
    assert r.returncode == 0
    assert r.stdout == "No tasks\n"
    assert r.stderr == ""


def test_add_and_list(todo):
    r = todo("add", "buy", "milk")
    assert r.returncode == 0
    assert r.stdout == "Added 1: buy milk\n"
    r = todo("add", "walk", "the", "dog")
    assert r.stdout == "Added 2: walk the dog\n"
    r = todo("list")
    assert r.returncode == 0
    assert r.stdout == "[ ] 1: buy milk\n[ ] 2: walk the dog\n"


def test_done_and_list(todo):
    todo("add", "a")
    r = todo("done", "1")
    assert r.returncode == 0
    assert r.stdout == "Done 1\n"
    assert todo("list").stdout == "[x] 1: a\n"
    r = todo("done", "1")
    assert r.returncode == 0
    assert r.stdout == "Done 1\n"


def test_done_missing(todo):
    todo("add", "a")
    r = todo("done", "99")
    assert r.returncode == 1
    assert r.stdout == ""
    assert r.stderr == "Error: no task 99\n"


def test_remove(todo):
    todo("add", "a")
    todo("add", "b")
    r = todo("remove", "1")
    assert r.returncode == 0
    assert r.stdout == "Removed 1\n"
    assert todo("list").stdout == "[ ] 2: b\n"


def test_remove_missing(todo):
    r = todo("remove", "5")
    assert r.returncode == 1
    assert r.stdout == ""
    assert r.stderr == "Error: no task 5\n"


def test_ids_not_reused(todo):
    todo("add", "a")
    todo("add", "b")
    todo("remove", "2")
    r = todo("add", "c")
    assert r.stdout == "Added 3: c\n"
    todo("done", "1")
    todo("clear")
    r = todo("add", "d")
    assert r.stdout == "Added 4: d\n"


def test_clear(todo):
    todo("add", "a")
    todo("add", "b")
    todo("add", "c")
    todo("done", "1")
    todo("done", "3")
    r = todo("clear")
    assert r.returncode == 0
    assert r.stdout == "Cleared 2\n"
    assert todo("list").stdout == "[ ] 2: b\n"
    r = todo("clear")
    assert r.stdout == "Cleared 0\n"


def test_usage(todo):
    for args in [(), ("bogus",), ("add",), ("done",), ("done", "x"),
                 ("remove",), ("remove", "x"), ("clear", "extra")]:
        r = todo(*args)
        assert r.returncode == 2, args
        assert r.stdout == "", args
        assert r.stderr == "Usage: todo.py <add|list|done|remove|clear> ...\n", args


def test_default_path_cwd(tmp_path):
    script = SCRIPT
    env = dict(os.environ)
    env.pop("TODO_FILE", None)
    r = subprocess.run(
        [sys.executable, script, "add", "x"], cwd=str(tmp_path), env=env,
        capture_output=True, text=True,
    )
    assert r.returncode == 0
    assert (tmp_path / "todo.json").exists()
    r = subprocess.run(
        [sys.executable, script, "list"], cwd=str(tmp_path), env=env,
        capture_output=True, text=True,
    )
    assert r.stdout == "[ ] 1: x\n"
