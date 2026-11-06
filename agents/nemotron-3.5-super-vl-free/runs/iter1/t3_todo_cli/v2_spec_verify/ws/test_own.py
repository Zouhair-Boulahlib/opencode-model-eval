import json
import os
import subprocess
import sys
import tempfile

import pytest


TODO_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "todo.py")


@pytest.fixture
def todo_file():
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    os.remove(path)
    old = os.environ.get("TODO_FILE")
    os.environ["TODO_FILE"] = path
    yield path
    if old is None:
        os.environ.pop("TODO_FILE", None)
    else:
        os.environ["TODO_FILE"] = old
    if os.path.exists(path):
        os.remove(path)


def run(*args):
    env = dict(os.environ)
    return subprocess.run([sys.executable, TODO_SCRIPT, *args],
                          capture_output=True, text=True, env=env)


def test_add(todo_file):
    r = run("add", "Buy", "milk")
    assert r.returncode == 0
    assert r.stdout == "Added 1: Buy milk\n"
    assert r.stderr == ""
    r = run("add", "Walk", "the", "dog")
    assert r.returncode == 0
    assert r.stdout == "Added 2: Walk the dog\n"


def test_list_empty(todo_file):
    r = run("list")
    assert r.returncode == 0
    assert r.stdout == "No tasks\n"


def test_list(todo_file):
    run("add", "first")
    run("add", "second")
    r = run("list")
    assert r.returncode == 0
    assert r.stdout == "[ ] 1: first\n[ ] 2: second\n"


def test_done(todo_file):
    run("add", "task")
    r = run("done", "1")
    assert r.returncode == 0
    assert r.stdout == "Done 1\n"
    r = run("list")
    assert r.stdout == "[x] 1: task\n"


def test_done_already_done(todo_file):
    run("add", "task")
    run("done", "1")
    r = run("done", "1")
    assert r.returncode == 0
    assert r.stdout == "Done 1\n"


def test_done_missing(todo_file):
    r = run("done", "5")
    assert r.returncode == 1
    assert r.stdout == ""
    assert r.stderr == "Error: no task 5\n"


def test_remove(todo_file):
    run("add", "a")
    run("add", "b")
    run("add", "c")
    r = run("remove", "2")
    assert r.returncode == 0
    assert r.stdout == "Removed 2\n"
    r = run("list")
    assert r.stdout == "[ ] 1: a\n[ ] 3: c\n"


def test_remove_missing(todo_file):
    r = run("remove", "9")
    assert r.returncode == 1
    assert r.stdout == ""
    assert r.stderr == "Error: no task 9\n"


def test_clear(todo_file):
    run("add", "done1")
    run("add", "done2")
    run("add", "open")
    run("done", "1")
    run("done", "2")
    r = run("clear")
    assert r.returncode == 0
    assert r.stdout == "Cleared 2\n"
    r = run("list")
    assert r.stdout == "[ ] 3: open\n"


def test_clear_none(todo_file):
    run("add", "open")
    r = run("clear")
    assert r.returncode == 0
    assert r.stdout == "Cleared 0\n"


def test_ids_never_reused(todo_file):
    run("add", "a")
    run("add", "b")
    run("remove", "1")
    r = run("add", "c")
    assert r.stdout == "Added 3: c\n"


def test_unknown_command(todo_file):
    r = run("frobnicate")
    assert r.returncode == 2
    assert r.stdout == ""
    assert r.stderr == "Usage: todo.py <add|list|done|remove|clear> ...\n"


def test_missing_command(todo_file):
    r = run()
    assert r.returncode == 2
    assert r.stdout == ""
    assert r.stderr == "Usage: todo.py <add|list|done|remove|clear> ...\n"


def test_add_no_args(todo_file):
    r = run("add")
    assert r.returncode == 2
    assert r.stdout == ""
    assert r.stderr == "Usage: todo.py <add|list|done|remove|clear> ...\n"


def test_done_invalid_arg(todo_file):
    r = run("done", "abc")
    assert r.returncode == 2
    assert r.stdout == ""
    assert r.stderr == "Usage: todo.py <add|list|done|remove|clear> ...\n"


def test_extra_args_list(todo_file):
    r = run("list", "extra")
    assert r.returncode == 2


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
