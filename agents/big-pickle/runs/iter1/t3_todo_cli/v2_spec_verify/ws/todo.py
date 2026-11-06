import json
import os
import sys

USAGE = "Usage: todo.py <add|list|done|remove|clear> ..."


def storage_path():
    return os.environ.get("TODO_FILE") or os.path.join(os.getcwd(), "todo.json")


def load():
    path = storage_path()
    if not os.path.exists(path):
        return {"next_id": 1, "tasks": []}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return {"next_id": 1, "tasks": []}
    if not isinstance(data, dict):
        return {"next_id": 1, "tasks": []}
    data.setdefault("next_id", 1)
    data.setdefault("tasks", [])
    return data


def save(data):
    path = storage_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)


def fail_usage():
    print(USAGE, file=sys.stderr)
    return 2


def fail_no_task(task_id):
    print(f"Error: no task {task_id}", file=sys.stderr)
    return 1


def parse_id(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def cmd_add(args):
    if not args:
        return fail_usage()
    data = load()
    task_id = data["next_id"]
    data["next_id"] = task_id + 1
    text = " ".join(args)
    data["tasks"].append({"id": task_id, "text": text, "done": False})
    save(data)
    print(f"Added {task_id}: {text}")
    return 0


def cmd_list(args):
    if args:
        return fail_usage()
    data = load()
    tasks = sorted(data["tasks"], key=lambda t: t["id"])
    if not tasks:
        print("No tasks")
        return 0
    for task in tasks:
        mark = "x" if task.get("done") else " "
        print(f"[{mark}] {task['id']}: {task['text']}")
    return 0


def cmd_done(args):
    if len(args) != 1:
        return fail_usage()
    task_id = parse_id(args[0])
    if task_id is None:
        return fail_usage()
    data = load()
    for task in data["tasks"]:
        if task["id"] == task_id:
            task["done"] = True
            save(data)
            print(f"Done {task_id}")
            return 0
    return fail_no_task(task_id)


def cmd_remove(args):
    if len(args) != 1:
        return fail_usage()
    task_id = parse_id(args[0])
    if task_id is None:
        return fail_usage()
    data = load()
    for i, task in enumerate(data["tasks"]):
        if task["id"] == task_id:
            del data["tasks"][i]
            save(data)
            print(f"Removed {task_id}")
            return 0
    return fail_no_task(task_id)


def cmd_clear(args):
    if args:
        return fail_usage()
    data = load()
    done = [t for t in data["tasks"] if t.get("done")]
    data["tasks"] = [t for t in data["tasks"] if not t.get("done")]
    if done:
        save(data)
    print(f"Cleared {len(done)}")
    return 0


COMMANDS = {
    "add": cmd_add,
    "list": cmd_list,
    "done": cmd_done,
    "remove": cmd_remove,
    "clear": cmd_clear,
}


def main(argv):
    if not argv:
        return fail_usage()
    command, args = argv[0], argv[1:]
    handler = COMMANDS.get(command)
    if handler is None:
        return fail_usage()
    return handler(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
