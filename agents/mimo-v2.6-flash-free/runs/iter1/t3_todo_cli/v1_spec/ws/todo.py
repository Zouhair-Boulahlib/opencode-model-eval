import json
import os
import sys

USAGE = "Usage: todo.py <add|list|done|remove|clear> ..."


def get_path():
    return os.environ.get("TODO_FILE") or os.path.join(os.getcwd(), "todo.json")


def load(path):
    if not os.path.exists(path):
        return {"next_id": 1, "tasks": []}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (ValueError, OSError):
        return {"next_id": 1, "tasks": []}
    if not isinstance(data, dict) or "tasks" not in data:
        return {"next_id": 1, "tasks": []}
    data.setdefault("next_id", 1)
    if not isinstance(data["tasks"], list):
        data["tasks"] = []
    return data


def save(path, data):
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


def find_task(data, tid):
    for task in data["tasks"]:
        if task.get("id") == tid:
            return task
    return None


def parse_id(arg):
    try:
        return int(arg)
    except (TypeError, ValueError):
        return None


def main(argv):
    if len(argv) < 1:
        sys.stderr.write(USAGE + "\n")
        return 2
    command = argv[0]
    args = argv[1:]
    path = get_path()

    if command == "add":
        if not args or any(a == "" for a in args):
            sys.stderr.write(USAGE + "\n")
            return 2
        data = load(path)
        text = " ".join(args)
        tid = data["next_id"]
        data["next_id"] = tid + 1
        data["tasks"].append({"id": tid, "text": text, "done": False})
        save(path, data)
        sys.stdout.write("Added %d: %s\n" % (tid, text))
        return 0

    if command == "list":
        if args:
            sys.stderr.write(USAGE + "\n")
            return 2
        data = load(path)
        if not data["tasks"]:
            sys.stdout.write("No tasks\n")
            return 0
        for task in sorted(data["tasks"], key=lambda t: t["id"]):
            mark = "x" if task.get("done") else " "
            sys.stdout.write("[%s] %d: %s\n" % (mark, task["id"], task.get("text", "")))
        return 0

    if command == "done":
        if len(args) != 1:
            sys.stderr.write(USAGE + "\n")
            return 2
        tid = parse_id(args[0])
        if tid is None:
            sys.stderr.write(USAGE + "\n")
            return 2
        data = load(path)
        task = find_task(data, tid)
        if task is None:
            sys.stderr.write("Error: no task %d\n" % tid)
            return 1
        task["done"] = True
        save(path, data)
        sys.stdout.write("Done %d\n" % tid)
        return 0

    if command == "remove":
        if len(args) != 1:
            sys.stderr.write(USAGE + "\n")
            return 2
        tid = parse_id(args[0])
        if tid is None:
            sys.stderr.write(USAGE + "\n")
            return 2
        data = load(path)
        task = find_task(data, tid)
        if task is None:
            sys.stderr.write("Error: no task %d\n" % tid)
            return 1
        data["tasks"].remove(task)
        save(path, data)
        sys.stdout.write("Removed %d\n" % tid)
        return 0

    if command == "clear":
        if args:
            sys.stderr.write(USAGE + "\n")
            return 2
        data = load(path)
        before = len(data["tasks"])
        data["tasks"] = [t for t in data["tasks"] if not t.get("done")]
        cleared = before - len(data["tasks"])
        save(path, data)
        sys.stdout.write("Cleared %d\n" % cleared)
        return 0

    sys.stderr.write(USAGE + "\n")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
