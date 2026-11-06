#!/usr/bin/env python3
"""Command-line to-do manager using only the Python standard library."""

import json
import os
import sys


def get_todo_file():
    """Return the path to the todo data file."""
    path = os.environ.get("TODO_FILE")
    if path:
        return path
    return os.path.join(os.getcwd(), "todo.json")


def load_tasks(path):
    """Load tasks from the JSON file. Returns empty list if file doesn't exist."""
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)


def save_tasks(path, tasks):
    """Write tasks to the JSON file."""
    with open(path, "w") as f:
        json.dump(tasks, f)


def next_id(tasks):
    """Return the next available ID."""
    if not tasks:
        return 1
    return max(t["id"] for t in tasks) + 1


def cmd_add(args, tasks, path):
    """Add a task. args are the task words joined by spaces."""
    text = " ".join(args)
    tasks.append({"id": next_id(tasks), "text": text, "done": False})
    save_tasks(path, tasks)
    print(f"Added {tasks[-1]['id']}: {text}")


def cmd_list(tasks):
    """List all tasks."""
    if not tasks:
        print("No tasks")
        return
    for t in tasks:
        if t["done"]:
            print(f"[x] {t['id']}: {t['text']}")
        else:
            print(f"[ ] {t['id']}: {t['text']}")


def cmd_done(args, tasks, path):
    """Mark task as done."""
    try:
        task_id = int(args[0])
    except (ValueError, IndexError):
        print("Usage: todo.py <add|list|done|remove|clear> ...", file=sys.stderr)
        sys.exit(2)
    for t in tasks:
        if t["id"] == task_id:
            t["done"] = True
            save_tasks(path, tasks)
            print(f"Done {task_id}")
            return
    print(f"Error: no task {task_id}", file=sys.stderr)
    sys.exit(1)


def cmd_remove(args, tasks, path):
    """Remove a task by ID."""
    try:
        task_id = int(args[0])
    except (ValueError, IndexError):
        print("Usage: todo.py <add|list|done|remove|clear> ...", file=sys.stderr)
        sys.exit(2)
    for i, t in enumerate(tasks):
        if t["id"] == task_id:
            tasks.pop(i)
            save_tasks(path, tasks)
            print(f"Removed {task_id}")
            return
    print(f"Error: no task {task_id}", file=sys.stderr)
    sys.exit(1)


def cmd_clear(tasks, path):
    """Delete all done tasks."""
    before = len(tasks)
    tasks = [t for t in tasks if not t["done"]]
    after = len(tasks)
    removed = before - after
    save_tasks(path, tasks)
    print(f"Cleared {removed}")


def main():
    path = get_todo_file()
    tasks = load_tasks(path)

    args = sys.argv[1:]
    if not args or args[0] not in ("add", "list", "done", "remove", "clear"):
        print("Usage: todo.py <add|list|done|remove|clear> ...", file=sys.stderr)
        sys.exit(2)

    command = args[0]
    rest = args[1:]

    if command == "add":
        cmd_add(rest, tasks, path)
    elif command == "list":
        cmd_list(tasks)
    elif command == "done":
        cmd_done(rest, tasks, path)
    elif command == "remove":
        cmd_remove(rest, tasks, path)
    elif command == "clear":
        cmd_clear(tasks, path)


if __name__ == "__main__":
    main()
