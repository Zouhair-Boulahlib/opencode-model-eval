#!/usr/bin/env python3
"""A small command-line todo app backed by a JSON file."""

import argparse
import json
import sys
from pathlib import Path

DATA_FILE = Path(__file__).with_name("todos.json")


def load_tasks():
    if not DATA_FILE.exists():
        return []
    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError) as exc:
        print(f"error: could not read {DATA_FILE}: {exc}", file=sys.stderr)
        sys.exit(1)


def save_tasks(tasks):
    try:
        with DATA_FILE.open("w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=2)
            f.write("\n")
    except OSError as exc:
        print(f"error: could not write {DATA_FILE}: {exc}", file=sys.stderr)
        sys.exit(1)


def next_id(tasks):
    return max((t["id"] for t in tasks), default=0) + 1


def find_task(tasks, task_id):
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None


def parse_id(value):
    try:
        return int(value)
    except ValueError:
        print(f"error: '{value}' is not a valid task id", file=sys.stderr)
        sys.exit(1)


def cmd_add(args):
    tasks = load_tasks()
    task = {"id": next_id(tasks), "task": args.text, "done": False}
    tasks.append(task)
    save_tasks(tasks)
    print(f"Added task {task['id']}: {task['task']}")


def cmd_list(_args):
    tasks = load_tasks()
    if not tasks:
        print("No tasks.")
        return
    for task in tasks:
        mark = "x" if task.get("done") else " "
        print(f"[{mark}] {task['id']}. {task['task']}")


def cmd_done(args):
    tasks = load_tasks()
    task = find_task(tasks, parse_id(args.id))
    if task is None:
        print(f"error: no task with id {args.id}", file=sys.stderr)
        sys.exit(1)
    task["done"] = True
    save_tasks(tasks)
    print(f"Completed task {task['id']}: {task['task']}")


def cmd_remove(args):
    tasks = load_tasks()
    task_id = parse_id(args.id)
    task = find_task(tasks, task_id)
    if task is None:
        print(f"error: no task with id {args.id}", file=sys.stderr)
        sys.exit(1)
    tasks.remove(task)
    save_tasks(tasks)
    print(f"Removed task {task_id}: {task['task']}")


def cmd_clear(_args):
    tasks = load_tasks()
    count = len(tasks)
    save_tasks([])
    print(f"Cleared {count} task(s).")


def build_parser():
    parser = argparse.ArgumentParser(description="A simple command-line todo app.")
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="add a new task")
    add.add_argument("text", help="task description")
    add.set_defaults(func=cmd_add)

    lst = sub.add_parser("list", help="list all tasks")
    lst.set_defaults(func=cmd_list)

    done = sub.add_parser("done", help="mark a task as completed")
    done.add_argument("id", help="task id")
    done.set_defaults(func=cmd_done)

    remove = sub.add_parser("remove", help="remove a task")
    remove.add_argument("id", help="task id")
    remove.set_defaults(func=cmd_remove)

    clear = sub.add_parser("clear", help="remove all tasks")
    clear.set_defaults(func=cmd_clear)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
