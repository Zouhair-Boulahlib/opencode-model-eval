import os
import subprocess
import sys

TODO = os.path.abspath("todo.py")


def run(args, env=None, cwd=None):
    e = dict(os.environ)
    if env:
        e.update(env)
    return subprocess.run(
        [sys.executable, TODO] + args,
        capture_output=True,
        text=True,
        env=e,
        cwd=cwd,
    )


def test_missing_file_means_no_tasks(tmp_path):
    env = {"TODO_FILE": str(tmp_path / "todo.json")}
    r = run(["list"], env=env)
    assert r.returncode == 0
    assert r.stdout == "No tasks\n"
    assert r.stderr == ""
    assert not (tmp_path / "todo.json").exists()


def test_add_and_list(tmp_path):
    env = {"TODO_FILE": str(tmp_path / "todo.json")}
    r = run(["add", "buy", "milk"], env=env)
    assert r.returncode == 0
    assert r.stdout == "Added 1: buy milk\n"
    r = run(["list"], env=env)
    assert r.stdout == "[ ] 1: buy milk\n"


def test_done_and_already_done(tmp_path):
    env = {"TODO_FILE": str(tmp_path / "todo.json")}
    run(["add", "task"], env=env)
    r = run(["done", "1"], env=env)
    assert r.returncode == 0
    assert r.stdout == "Done 1\n"
    r = run(["list"], env=env)
    assert r.stdout == "[x] 1: task\n"
    r = run(["done", "1"], env=env)
    assert r.returncode == 0
    assert r.stdout == "Done 1\n"


def test_remove(tmp_path):
    env = {"TODO_FILE": str(tmp_path / "todo.json")}
    run(["add", "a"], env=env)
    run(["add", "b"], env=env)
    r = run(["remove", "1"], env=env)
    assert r.returncode == 0
    assert r.stdout == "Removed 1\n"
    r = run(["list"], env=env)
    assert r.stdout == "[ ] 2: b\n"


def test_ids_never_reused(tmp_path):
    env = {"TODO_FILE": str(tmp_path / "todo.json")}
    run(["add", "a"], env=env)
    run(["remove", "1"], env=env)
    run(["clear"], env=env)
    r = run(["add", "b"], env=env)
    assert r.stdout == "Added 2: b\n"


def test_clear_counts(tmp_path):
    env = {"TODO_FILE": str(tmp_path / "todo.json")}
    run(["add", "a"], env=env)
    run(["add", "b"], env=env)
    run(["done", "1"], env=env)
    r = run(["clear"], env=env)
    assert r.returncode == 0
    assert r.stdout == "Cleared 1\n"
    r = run(["list"], env=env)
    assert r.stdout == "[ ] 2: b\n"


def test_missing_id_errors(tmp_path):
    env = {"TODO_FILE": str(tmp_path / "todo.json")}
    for cmd in (["done", "999"], ["remove", "999"]):
        r = run(cmd, env=env)
        assert r.returncode == 1
        assert r.stdout == ""
        assert r.stderr == "Error: no task 999\n"


def test_usage_missing_command():
    r = run([])
    assert r.returncode == 2
    assert r.stderr == "Usage: todo.py <add|list|done|remove|clear> ...\n"


def test_usage_unknown_command():
    r = run(["frob"])
    assert r.returncode == 2
    assert r.stderr == "Usage: todo.py <add|list|done|remove|clear> ...\n"


def test_usage_add_no_args(tmp_path):
    env = {"TODO_FILE": str(tmp_path / "todo.json")}
    r = run(["add"], env=env)
    assert r.returncode == 2
    assert r.stderr == "Usage: todo.py <add|list|done|remove|clear> ...\n"


def test_usage_invalid_id(tmp_path):
    env = {"TODO_FILE": str(tmp_path / "todo.json")}
    r = run(["done", "abc"], env=env)
    assert r.returncode == 2
    assert r.stderr == "Usage: todo.py <add|list|done|remove|clear> ...\n"


def test_usage_extra_args(tmp_path):
    env = {"TODO_FILE": str(tmp_path / "todo.json")}
    for cmd in (["list", "x"], ["clear", "x"], ["done", "1", "x"], ["remove", "1", "x"]):
        r = run(cmd, env=env)
        assert r.returncode == 2


def test_default_file_in_cwd(tmp_path):
    r = run(["add", "hello"], cwd=str(tmp_path))
    assert r.returncode == 0
    assert r.stdout == "Added 1: hello\n"
    assert (tmp_path / "todo.json").exists()


def test_clear_empty_does_not_crash(tmp_path):
    env = {"TODO_FILE": str(tmp_path / "todo.json")}
    r = run(["clear"], env=env)
    assert r.returncode == 0
    assert r.stdout == "Cleared 0\n"


def test_list_order_after_remove(tmp_path):
    env = {"TODO_FILE": str(tmp_path / "todo.json")}
    run(["add", "a"], env=env)
    run(["add", "b"], env=env)
    run(["add", "c"], env=env)
    run(["remove", "2"], env=env)
    r = run(["list"], env=env)
    assert r.stdout == "[ ] 1: a\n[ ] 3: c\n"