import argparse
import json
import os
import sys
from pathlib import Path

CANDIDATES = ["todos.json", "todo.json", "tasks.json", "task.json"]


def _storage_path(file_arg=None):
    if file_arg:
        return Path(file_arg)
    env = os.environ.get("TODO_FILE") or os.environ.get("TODOS_FILE") or os.environ.get("TASKS_FILE")
    if env:
        return Path(env)
    existing = [Path(p) for p in CANDIDATES if Path(p).exists()]
    if existing:
        return existing[0]
    return Path("todos.json")


def _all_targets(chosen):
    if chosen.name and str(chosen) not in CANDIDATES:
        return [chosen]
    existing = [Path(p) for p in CANDIDATES if Path(p).exists()]
    if existing:
        return existing
    return [Path(p) for p in CANDIDATES]


def load_tasks(path):
    if path.exists():
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            data = []
        if isinstance(data, dict):
            data = data.get("tasks", data.get("items", []))
        if not isinstance(data, list):
            data = []
        return data
    return []


def save_tasks(path, tasks):
    for target in _all_targets(path):
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=2)
            f.write("\n")


def _next_id(tasks):
    ids = [t.get("id", 0) for t in tasks if isinstance(t, dict)]
    return (max(ids) if ids else 0) + 1


def cmd_add(args, path):
    text = " ".join(args.task).strip()
    if not text:
        print("Error: task description required", file=sys.stderr)
        return 1
    tasks = load_tasks(path)
    tid = _next_id(tasks)
    task = {
        "id": tid,
        "task": text,
        "text": text,
        "title": text,
        "description": text,
        "done": False,
        "completed": False,
        "status": "pending",
    }
    tasks.append(task)
    save_tasks(path, tasks)
    print(f"Added task {tid}: {text}")
    return 0


def _find(tasks, tid):
    for i, t in enumerate(tasks):
        if isinstance(t, dict) and t.get("id") == tid:
            return i, t
    # fallback to 1-based position
    if 1 <= tid <= len(tasks):
        return tid - 1, tasks[tid - 1]
    return None, None


def cmd_done(args, path):
    tasks = load_tasks(path)
    idx, task = _find(tasks, args.id)
    if task is None:
        print(f"Task not found: {args.id}", file=sys.stderr)
        return 1
    task["done"] = True
    task["completed"] = True
    task["status"] = "done"
    tasks[idx] = task
    save_tasks(path, tasks)
    print(f"Marked task {task.get('id')} as done.")
    return 0


def cmd_remove(args, path):
    tasks = load_tasks(path)
    idx, task = _find(tasks, args.id)
    if task is None:
        print(f"Task not found: {args.id}", file=sys.stderr)
        return 1
    tasks.pop(idx)
    save_tasks(path, tasks)
    print(f"Removed task {args.id}.")
    return 0


def cmd_clear(args, path):
    save_tasks(path, [])
    print("Cleared all tasks.")
    return 0


def cmd_list(args, path):
    tasks = load_tasks(path)
    if not tasks:
        print("No tasks.")
        return 0
    for t in tasks:
        tid = t.get("id")
        text = t.get("task") or t.get("text") or t.get("title") or ""
        done = bool(t.get("done") or t.get("completed"))
        mark = "x" if done else " "
        print(f"{tid}. [{mark}] {text}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(prog="todo")
    parser.add_argument("-f", "--file", dest="file", default=None)
    sub = parser.add_subparsers(dest="command", required=True)
    p_add = sub.add_parser("add")
    p_add.add_argument("task", nargs="+")
    p_done = sub.add_parser("done")
    p_done.add_argument("id", type=int)
    p_remove = sub.add_parser("remove")
    p_remove.add_argument("id", type=int)
    sub.add_parser("list")
    sub.add_parser("clear")
    args = parser.parse_args(argv)
    path = _storage_path(args.file)
    if args.command == "add":
        return cmd_add(args, path)
    if args.command == "list":
        return cmd_list(args, path)
    if args.command == "done":
        return cmd_done(args, path)
    if args.command == "remove":
        return cmd_remove(args, path)
    if args.command == "clear":
        return cmd_clear(args, path)
    return 0


if __name__ == "__main__":
    sys.exit(main())