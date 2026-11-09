import json
import os
import sys

USAGE = "Usage: todo.py <add|list|done|remove|clear> ..."


def todo_path():
    return os.environ.get("TODO_FILE") or "todo.json"


def load_state():
    path = todo_path()
    tasks = []
    next_id = 1
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            tasks = data.get("tasks") or []
            next_id = data.get("next_id") or 1
    except (OSError, ValueError):
        tasks = []
        next_id = 1
    return tasks, next_id


def save_state(tasks, next_id):
    with open(todo_path(), "w", encoding="utf-8") as f:
        json.dump({"tasks": tasks, "next_id": next_id}, f)


def usage_error():
    sys.stderr.write(USAGE + "\n")
    return 2


def no_task_error(task_id):
    sys.stderr.write("Error: no task %d\n" % task_id)
    return 1


def cmd_add(args):
    if not args:
        return usage_error()
    tasks, next_id = load_state()
    task = {"id": next_id, "text": " ".join(args), "done": False}
    tasks.append(task)
    save_state(tasks, next_id + 1)
    print("Added %d: %s" % (task["id"], task["text"]))
    return 0


def cmd_list(_args):
    tasks, _ = load_state()
    if not tasks:
        print("No tasks")
        return 0
    for task in sorted(tasks, key=lambda t: t["id"]):
        marker = "x" if task.get("done") else " "
        print("[%s] %d: %s" % (marker, task["id"], task["text"]))
    return 0


def cmd_done(args):
    if len(args) != 1 or not args[0].lstrip("-").isdigit():
        return usage_error()
    task_id = int(args[0])
    tasks, next_id = load_state()
    for task in tasks:
        if task.get("id") == task_id:
            task["done"] = True
            save_state(tasks, next_id)
            print("Done %d" % task_id)
            return 0
    return no_task_error(task_id)


def cmd_remove(args):
    if len(args) != 1 or not args[0].lstrip("-").isdigit():
        return usage_error()
    task_id = int(args[0])
    tasks, next_id = load_state()
    remaining = [t for t in tasks if t.get("id") != task_id]
    if len(remaining) == len(tasks):
        return no_task_error(task_id)
    save_state(remaining, next_id)
    print("Removed %d" % task_id)
    return 0


def cmd_clear(_args):
    tasks, next_id = load_state()
    remaining = [t for t in tasks if not t.get("done")]
    cleared = len(tasks) - len(remaining)
    save_state(remaining, next_id)
    print("Cleared %d" % cleared)
    return 0


def main(argv):
    if not argv:
        return usage_error()
    command = argv[0]
    args = argv[1:]
    if command == "add":
        return cmd_add(args)
    if command == "list":
        if args:
            return usage_error()
        return cmd_list(args)
    if command == "done":
        return cmd_done(args)
    if command == "remove":
        return cmd_remove(args)
    if command == "clear":
        if args:
            return usage_error()
        return cmd_clear(args)
    return usage_error()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
