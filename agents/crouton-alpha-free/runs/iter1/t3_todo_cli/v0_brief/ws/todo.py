#!/usr/bin/env python3
"""Command-line todo app that saves tasks to a JSON file."""
import argparse
import json
import sys
from pathlib import Path

DATA_FILE = Path(__file__).parent / "tasks.json"


def load_tasks():
    if not DATA_FILE.exists():
        return []
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def save_tasks(tasks):
    DATA_FILE.write_text(json.dumps(tasks, indent=2) + "\n", encoding="utf-8")


def next_id(tasks):
    return max((t["id"] for t in tasks), default=0) + 1


def find_task(tasks, task_id):
    for t in tasks:
        if t["id"] == task_id:
            return t
    return None


def cmd_add(args):
    tasks = load_tasks()
    task = {"id": next_id(tasks), "text": args.text, "done": False}
    tasks.append(task)
    save_tasks(tasks)
    print(f"Added task {task['id']}: {task['text']}")


def cmd_list(args):
    tasks = load_tasks()
    if not tasks:
        print("No tasks.")
        return
    for t in tasks:
        status = "x" if t.get("done") else " "
        print(f"[{status}] {t['id']}: {t['text']}")


def cmd_done(args):
    tasks = load_tasks()
    task = find_task(tasks, args.id)
    if task is None:
        print(f"Task {args.id} not found.", file=sys.stderr)
        sys.exit(1)
    task["done"] = True
    save_tasks(tasks)
    print(f"Marked task {args.id} as done.")


def cmd_remove(args):
    tasks = load_tasks()
    task = find_task(tasks, args.id)
    if task is None:
        print(f"Task {args.id} not found.", file=sys.stderr)
        sys.exit(1)
    tasks = [t for t in tasks if t["id"] != args.id]
    save_tasks(tasks)
    print(f"Removed task {args.id}.")


def cmd_clear(args):
    tasks = load_tasks()
    if getattr(args, "completed", False):
        tasks = [t for t in tasks if not t.get("done")]
    else:
        tasks = []
    save_tasks(tasks)
    print("Cleared tasks.")


def main():
    parser = argparse.ArgumentParser(description="Command-line todo app")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_add = subparsers.add_parser("add", help="Add a task")
    p_add.add_argument("text", help="Task text")
    p_add.set_defaults(func=cmd_add)

    p_list = subparsers.add_parser("list", help="List tasks")
    p_list.set_defaults(func=cmd_list)

    p_done = subparsers.add_parser("done", help="Mark a task as done")
    p_done.add_argument("id", type=int, help="Task ID")
    p_done.set_defaults(func=cmd_done)

    p_remove = subparsers.add_parser("remove", help="Remove a task")
    p_remove.add_argument("id", type=int, help="Task ID")
    p_remove.set_defaults(func=cmd_remove)

    p_clear = subparsers.add_parser("clear", help="Clear tasks")
    p_clear.add_argument("--completed", action="store_true", help="Only clear completed tasks")
    p_clear.set_defaults(func=cmd_clear)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
