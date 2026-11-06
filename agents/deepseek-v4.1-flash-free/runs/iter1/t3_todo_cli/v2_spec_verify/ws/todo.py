#!/usr/bin/env python3
"""Command-line to-do manager using only the Python standard library."""

import json
import os
import sys

USAGE = "Usage: todo.py <add|list|done|remove|clear> ..."


def storage_path():
    return os.environ.get("TODO_FILE", os.path.join(os.getcwd(), "todo.json"))


def load():
    path = storage_path()
    if not os.path.exists(path):
        return {"next_id": 1, "tasks": []}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {"next_id": 1, "tasks": []}
    if not isinstance(data, dict):
        return {"next_id": 1, "tasks": []}
    tasks = data.get("tasks", [])
    if not isinstance(tasks, list):
        tasks = []
    next_id = data.get("next_id", 1)
    if not isinstance(next_id, int):
        next_id = 1
    return {"next_id": next_id, "tasks": tasks}


def save(data):
    path = storage_path()
    parent = os.path.dirname(os.path.abspath(path))
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def find_task(data, task_id):
    for task in data["tasks"]:
        if task.get("id") == task_id:
            return task
    return None


def parse_id(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def cmd_add(args):
    if not args:
        return usage()
    data = load()
    task_id = data["next_id"]
    text = " ".join(args)
    data["tasks"].append({"id": task_id, "text": text, "done": False})
    data["next_id"] = task_id + 1
    save(data)
    print("Added {}: {}".format(task_id, text))
    return 0


def cmd_list(args):
    if args:
        return usage()
    data = load()
    if not data["tasks"]:
        print("No tasks")
        return 0
    for task in sorted(data["tasks"], key=lambda t: t.get("id", 0)):
        mark = "x" if task.get("done") else " "
        print("[{}] {}: {}".format(mark, task.get("id"), task.get("text", "")))
    return 0


def cmd_done(args):
    if len(args) != 1:
        return usage()
    task_id = parse_id(args[0])
    if task_id is None:
        return usage()
    data = load()
    task = find_task(data, task_id)
    if task is None:
        print("Error: no task {}".format(task_id), file=sys.stderr)
        return 1
    task["done"] = True
    save(data)
    print("Done {}".format(task_id))
    return 0


def cmd_remove(args):
    if len(args) != 1:
        return usage()
    task_id = parse_id(args[0])
    if task_id is None:
        return usage()
    data = load()
    task = find_task(data, task_id)
    if task is None:
        print("Error: no task {}".format(task_id), file=sys.stderr)
        return 1
    data["tasks"] = [t for t in data["tasks"] if t.get("id") != task_id]
    save(data)
    print("Removed {}".format(task_id))
    return 0


def cmd_clear(args):
    if args:
        return usage()
    data = load()
    done = [t for t in data["tasks"] if t.get("done")]
    data["tasks"] = [t for t in data["tasks"] if not t.get("done")]
    save(data)
    print("Cleared {}".format(len(done)))
    return 0


def usage():
    print(USAGE, file=sys.stderr)
    return 2


COMMANDS = {
    "add": cmd_add,
    "list": cmd_list,
    "done": cmd_done,
    "remove": cmd_remove,
    "clear": cmd_clear,
}


def main(argv):
    if not argv:
        return usage()
    command = argv[0]
    handler = COMMANDS.get(command)
    if handler is None:
        return usage()
    return handler(argv[1:])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
