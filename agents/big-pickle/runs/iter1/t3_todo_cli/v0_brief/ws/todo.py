#!/usr/bin/env python3
"""A simple command-line todo app backed by a JSON file."""

import argparse
import json
import os
import sys
from datetime import datetime

DEFAULT_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.json")


def load_tasks(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"error: could not read {path}: {exc}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(data, list):
        print(f"error: {path} does not contain a task list", file=sys.stderr)
        sys.exit(1)
    return data


def save_tasks(path, tasks):
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, path)


def find_task(tasks, task_id):
    for task in tasks:
        if task.get("id") == task_id:
            return task
    return None


def cmd_add(args, path):
    tasks = load_tasks(path)
    text = " ".join(args.text).strip()
    if not text:
        print("error: task text cannot be empty", file=sys.stderr)
        return 1
    next_id = max((t.get("id", 0) for t in tasks), default=0) + 1
    task = {
        "id": next_id,
        "text": text,
        "done": False,
        "created": datetime.now().isoformat(timespec="seconds"),
    }
    tasks.append(task)
    save_tasks(path, tasks)
    print(f"Added task {next_id}: {text}")
    return 0


def cmd_list(args, path):
    tasks = load_tasks(path)
    if not tasks:
        print("No tasks.")
        return 0
    for task in tasks:
        if args.pending and task.get("done"):
            continue
        mark = "x" if task.get("done") else " "
        print(f"[{mark}] {task.get('id'):>3}  {task.get('text', '')}")
    return 0


def cmd_done(args, path):
    tasks = load_tasks(path)
    status = 0
    for task_id in args.ids:
        task = find_task(tasks, task_id)
        if task is None:
            print(f"error: no task with id {task_id}", file=sys.stderr)
            status = 1
            continue
        if task.get("done"):
            print(f"Task {task_id} is already done: {task.get('text', '')}")
        else:
            task["done"] = True
            print(f"Completed task {task_id}: {task.get('text', '')}")
    save_tasks(path, tasks)
    return status


def cmd_remove(args, path):
    tasks = load_tasks(path)
    status = 0
    for task_id in args.ids:
        task = find_task(tasks, task_id)
        if task is None:
            print(f"error: no task with id {task_id}", file=sys.stderr)
            status = 1
            continue
        tasks.remove(task)
        print(f"Removed task {task_id}: {task.get('text', '')}")
    save_tasks(path, tasks)
    return status


def cmd_clear(args, path):
    tasks = load_tasks(path)
    if not tasks:
        print("No tasks to clear.")
        return 0
    removed = len(tasks)
    save_tasks(path, [])
    print(f"Cleared {removed} task{'s' if removed != 1 else ''}.")
    return 0


def build_parser():
    parser = argparse.ArgumentParser(
        prog="todo",
        description="A simple command-line todo app.",
    )
    parser.add_argument(
        "-f",
        "--file",
        default=os.environ.get("TODO_FILE", DEFAULT_DB),
        help="path to the JSON task file (default: tasks.json next to this script)",
    )
    sub = parser.add_subparsers(dest="command", metavar="command")

    add = sub.add_parser("add", help="add a new task")
    add.add_argument("text", nargs="+", help="task description")
    add.set_defaults(func=cmd_add)

    lst = sub.add_parser("list", help="list tasks")
    lst.add_argument("-p", "--pending", action="store_true", help="show only unfinished tasks")
    lst.set_defaults(func=cmd_list)

    done = sub.add_parser("done", help="mark one or more tasks as done")
    done.add_argument("ids", nargs="+", type=int, metavar="ID")
    done.set_defaults(func=cmd_done)

    remove = sub.add_parser("remove", help="remove one or more tasks")
    remove.add_argument("ids", nargs="+", type=int, metavar="ID")
    remove.set_defaults(func=cmd_remove)

    clear = sub.add_parser("clear", help="remove all tasks")
    clear.set_defaults(func=cmd_clear)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "func", None):
        parser.print_help()
        return 1
    return args.func(args, args.file)


if __name__ == "__main__":
    sys.exit(main())
