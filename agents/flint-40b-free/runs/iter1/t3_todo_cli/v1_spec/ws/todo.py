import json
import os
import sys

USAGE = "Usage: todo.py <add|list|done|remove|clear> ..."


def usage_error():
    print(USAGE, file=sys.stderr)
    sys.exit(2)


def task_path():
    return os.environ.get("TODO_FILE") or "todo.json"


def load():
    try:
        with open(task_path(), "r") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return [], 1
    if isinstance(data, dict):
        tasks = data.get("tasks") or []
        next_id = data.get("next_id") or 1
    else:
        tasks = data or []
        next_id = 1
    return tasks, next_id


def save(tasks, next_id):
    with open(task_path(), "w") as f:
        json.dump({"tasks": tasks, "next_id": next_id}, f)


def main():
    args = sys.argv[1:]
    if not args:
        usage_error()
    cmd = args[0]
    rest = args[1:]

    if cmd == "add":
        if not rest:
            usage_error()
        tasks, next_id = load()
        task = {"id": next_id, "text": " ".join(rest), "done": False}
        tasks.append(task)
        save(tasks, next_id + 1)
        print(f"Added {task['id']}: {task['text']}")
        return 0

    if cmd == "list":
        if rest:
            usage_error()
        tasks, _ = load()
        if not tasks:
            print("No tasks")
            return 0
        for t in sorted(tasks, key=lambda t: t["id"]):
            marker = "[x]" if t.get("done") else "[ ]"
            print(f"{marker} {t['id']}: {t['text']}")
        return 0

    if cmd in ("done", "remove"):
        if len(rest) != 1:
            usage_error()
        try:
            task_id = int(rest[0])
        except ValueError:
            usage_error()
        tasks, next_id = load()
        task = next((t for t in tasks if t.get("id") == task_id), None)
        if task is None:
            print(f"Error: no task {task_id}", file=sys.stderr)
            sys.exit(1)
        if cmd == "done":
            task["done"] = True
            save(tasks, next_id)
            print(f"Done {task_id}")
        else:
            tasks.remove(task)
            save(tasks, next_id)
            print(f"Removed {task_id}")
        return 0

    if cmd == "clear":
        if rest:
            usage_error()
        tasks, next_id = load()
        remaining = [t for t in tasks if not t.get("done")]
        cleared = len(tasks) - len(remaining)
        save(remaining, next_id)
        print(f"Cleared {cleared}")
        return 0

    usage_error()


if __name__ == "__main__":
    sys.exit(main())
