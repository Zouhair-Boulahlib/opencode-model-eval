import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TODO = os.path.join(HERE, "todo.py")


def run(tmp_path, *args, use_env=True):
    env = dict(os.environ)
    if use_env:
        env["TODO_FILE"] = str(tmp_path / "tasks.json")
    else:
        env.pop("TODO_FILE", None)
    return subprocess.run([sys.executable, TODO, *args], capture_output=True, text=True,
                          env=env, cwd=str(tmp_path), timeout=30)


def test_list_empty(tmp_path):
    r = run(tmp_path, "list")
    assert r.returncode == 0
    assert r.stdout.strip() == "No tasks"


def test_add_prints_exact_line(tmp_path):
    r = run(tmp_path, "add", "buy", "milk")
    assert r.returncode == 0
    assert r.stdout == "Added 1: buy milk\n"
    assert r.stderr == ""


def test_add_and_list(tmp_path):
    run(tmp_path, "add", "buy milk")
    run(tmp_path, "add", "call", "mom")
    r = run(tmp_path, "list")
    assert r.stdout == "[ ] 1: buy milk\n[ ] 2: call mom\n"


def test_done_marks_task(tmp_path):
    run(tmp_path, "add", "a")
    run(tmp_path, "add", "b")
    r = run(tmp_path, "done", "1")
    assert r.returncode == 0 and r.stdout.strip() == "Done 1"
    r = run(tmp_path, "list")
    assert r.stdout == "[x] 1: a\n[ ] 2: b\n"


def test_done_twice_ok(tmp_path):
    run(tmp_path, "add", "a")
    run(tmp_path, "done", "1")
    r = run(tmp_path, "done", "1")
    assert r.returncode == 0 and r.stdout.strip() == "Done 1"


def test_remove(tmp_path):
    run(tmp_path, "add", "a")
    run(tmp_path, "add", "b")
    r = run(tmp_path, "remove", "1")
    assert r.returncode == 0 and r.stdout.strip() == "Removed 1"
    assert run(tmp_path, "list").stdout == "[ ] 2: b\n"


def test_ids_never_reused_after_remove(tmp_path):
    run(tmp_path, "add", "a")
    run(tmp_path, "add", "b")
    run(tmp_path, "remove", "2")
    r = run(tmp_path, "add", "c")
    assert r.stdout.strip() == "Added 3: c"


def test_ids_never_reused_after_clear(tmp_path):
    run(tmp_path, "add", "a")
    run(tmp_path, "done", "1")
    run(tmp_path, "clear")
    r = run(tmp_path, "add", "b")
    assert r.stdout.strip() == "Added 2: b"


def test_clear_counts_only_done(tmp_path):
    for t in "abc":
        run(tmp_path, "add", t)
    run(tmp_path, "done", "1")
    run(tmp_path, "done", "3")
    r = run(tmp_path, "clear")
    assert r.returncode == 0 and r.stdout.strip() == "Cleared 2"
    assert run(tmp_path, "list").stdout == "[ ] 2: b\n"


def test_done_unknown_id(tmp_path):
    r = run(tmp_path, "done", "42")
    assert r.returncode == 1
    assert r.stdout == ""
    assert "Error: no task 42" in r.stderr


def test_remove_unknown_id(tmp_path):
    run(tmp_path, "add", "a")
    r = run(tmp_path, "remove", "9")
    assert r.returncode == 1
    assert "Error: no task 9" in r.stderr
    assert run(tmp_path, "list").stdout == "[ ] 1: a\n"


def test_no_command_usage(tmp_path):
    r = run(tmp_path)
    assert r.returncode == 2
    assert r.stderr.strip().startswith("Usage:")


def test_unknown_command_usage(tmp_path):
    r = run(tmp_path, "frobnicate")
    assert r.returncode == 2
    assert r.stderr.strip().startswith("Usage:")


def test_done_missing_arg_usage(tmp_path):
    r = run(tmp_path, "done")
    assert r.returncode == 2
    assert r.stderr.strip().startswith("Usage:")


def test_default_file_in_cwd(tmp_path):
    r = run(tmp_path, "add", "x", use_env=False)
    assert r.returncode == 0
    assert (tmp_path / "todo.json").exists()
    assert run(tmp_path, "list", use_env=False).stdout == "[ ] 1: x\n"


def test_missing_file_means_no_tasks(tmp_path):
    env = dict(os.environ, TODO_FILE=str(tmp_path / "nested" / "none.json"))
    r = subprocess.run([sys.executable, TODO, "list"], capture_output=True, text=True, env=env, cwd=str(tmp_path), timeout=30)
    assert r.returncode == 0 and r.stdout.strip() == "No tasks"
