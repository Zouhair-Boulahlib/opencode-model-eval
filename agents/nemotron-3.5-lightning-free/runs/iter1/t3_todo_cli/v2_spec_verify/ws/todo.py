#!/usr/bin/env python3
"""Command-line to-do manager using only the Python standard library."""

import json
import os
import sys


def get_todo_file():
    """Return the path to the todo data file."""
    return os.environ.get("TODO_FILE", "todo.json")


def load_tasks(path):
    """Load tasks from the JSON file. Returns empty list if file doesn't exist."""
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_tasks(path, tasks):
    """Save tasks to the JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(tasks, f)


def next_id(tasks):
    """Return the next available ID (higher of current max and 1)."""
    if not tasks:
        return 1
    return max(t["id"] for t in tasks) + 1


def cmd_add(args):
    """Add a task: python todo.py add <word> [<word> ...]"""
    if len(args) < 1:
        print("Usage: todo.py <add|list|done|remove|clear> ...", file=sys.stderr)
        sys.exit(2)
    text = " ".join(args)
    path = get_todo_file()
    tasks = load_tasks(path)
    new_id = next_id(tasks)
    tasks.append({"id": new_id, "text": text, "done": False})
    save_tasks(path, tasks)
    print(f"Added {new_id}: {text}")


def cmd_list(args):
    """List tasks: python todo.py list"""
    path = get_todo_file()
    tasks = load_tasks(path)
    if not tasks:
        print("No tasks")
        return
    for t in sorted(tasks, key=lambda t: t["id"]):
        status = "x" if t["done"] else " "
        print(f"[ ] {t['id']}: {t['text']}" if not t["done"] else f"[x] {t['id']}: {t['text']}")
    # Simpler: always print with [ ] or [x] based on done status


def cmd_done(args):
    """Mark task done: python todo.py done <id>"""
    if len(args) < 1:
        print("Usage: todo.py <add|list|done|remove|clear> ...", file=sys.stderr)
        sys.exit(2)
    try:
        tid = int(args[0])
    except ValueError:
        print("Usage: todo.py <add|list|done|remove|clear> ...", file=sys.stderr)
        sys.exit(2)
    path = get_todo_file()
    tasks = load_tasks(path)
    found = False
    for t in tasks:
        if t["id"] == tid:
            found = True
            t["done"] = True
            break
    if not found:
        print(f"Error: no task {tid}", file=sys.stderr)
        sys.exit(1)
    save_tasks(path, tasks)
    print(f"Done {tid}")


def cmd_remove(args):
    """Remove task: python todo.py remove <id>"""
    if len(args) < 1:
        print("Usage: todo.py <add|list|done|remove|clear> ...", file=sys.stderr)
        sys.exit(2)
    try:
        tid = int(args[0])
    except ValueError:
        print("Usage: todo.py <add|list|done|remove|clear> ...", file=sys.stderr)
        sys.exit(2)
    path = get_todo_file()
    tasks = load_tasks(path)
    found = False
    new_tasks = []
    for t in tasks:
        if t["id"] == tid:
            found = True
            break
        new_tasks.append(t)
    if not found:
        print(f"Error: no task {tid}", file=sys.stderr)
        sys.exit(1)
    save_tasks(path, new_tasks)


def cmd_clear(args):
    """Clear all done tasks: python todo.py clear"""
    path = get_todo_file()
    tasks = load_tasks(path)
    before = len(tasks)
    after = [t for t in tasks if not t["done"]]
    removed = before - len(after)
    if removed > 0:
        save_tasks(path, after)
    print(f"Cleared {removed}")


def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: todo.py <add|list|done|remove|clear> ...", file=sys.stderr)
        sys.exit(2)
    command = args[0]
    rest = args[1:]
    if command == "add":
        cmd_add(rest)
    elif command == "list":
        cmd_list(rest)
    elif command == "done":
        cmd_done(rest)
    elif command == "remove":
        cmd_remove(rest)
    elif command == "clear":
        cmd_clear(rest)
    else:
        print("Usage: todo.py <add|list|done|remove|clear> ...", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()