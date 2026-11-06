import json
import os
import sys

DEFAULT_FILE = "todo.json"
USAGE = "Usage: todo.py <add|list|done|remove|clear> ..."


def path():
    return os.environ.get("TODO_FILE", os.path.join(os.getcwd(), DEFAULT_FILE))


def load():
    try:
        with open(path(), "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"next_id": 1, "tasks": []}
    if not isinstance(data, dict):
        return {"next_id": 1, "tasks": []}
    data.setdefault("next_id", 1)
    data.setdefault("tasks", [])
    return data


def save(data):
    with open(path(), "w", encoding="utf-8") as f:
        json.dump(data, f)


def fail_usage():
    print(USAGE, file=sys.stderr)
    sys.exit(2)


def parse_id(args):
    if len(args) != 1:
        fail_usage()
    try:
        return int(args[0])
    except ValueError:
        fail_usage()


def main(argv):
    if not argv:
        fail_usage()

    cmd, args = argv[0], argv[1:]

    if cmd == "add":
        if not args:
            fail_usage()
        data = load()
        task_id = data["next_id"]
        text = " ".join(args)
        data["tasks"].append({"id": task_id, "text": text, "done": False})
        data["next_id"] = task_id + 1
        save(data)
        print(f"Added {task_id}: {text}")
    elif cmd == "list":
        if args:
            fail_usage()
        data = load()
        if not data["tasks"]:
            print("No tasks")
        else:
            for task in sorted(data["tasks"], key=lambda t: t["id"]):
                mark = "x" if task["done"] else " "
                print(f"[{mark}] {task['id']}: {task['text']}")
    elif cmd == "done":
        task_id = parse_id(args)
        data = load()
        for task in data["tasks"]:
            if task["id"] == task_id:
                task["done"] = True
                save(data)
                print(f"Done {task_id}")
                return
        print(f"Error: no task {task_id}", file=sys.stderr)
        sys.exit(1)
    elif cmd == "remove":
        task_id = parse_id(args)
        data = load()
        remaining = [t for t in data["tasks"] if t["id"] != task_id]
        if len(remaining) == len(data["tasks"]):
            print(f"Error: no task {task_id}", file=sys.stderr)
            sys.exit(1)
        data["tasks"] = remaining
        save(data)
        print(f"Removed {task_id}")
    elif cmd == "clear":
        if args:
            fail_usage()
        data = load()
        remaining = [t for t in data["tasks"] if not t["done"]]
        cleared = len(data["tasks"]) - len(remaining)
        data["tasks"] = remaining
        save(data)
        print(f"Cleared {cleared}")
    else:
        fail_usage()


if __name__ == "__main__":
    main(sys.argv[1:])
