import json
import os
import sys


def storage_path():
    return os.environ.get("TODO_FILE", "todo.json")


def load():
    path = storage_path()
    if not os.path.exists(path):
        return {"next_id": 1, "tasks": []}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    tasks = data.get("tasks", [])
    next_id = data.get("next_id", 1)
    if tasks:
        next_id = max(next_id, max(task["id"] for task in tasks) + 1)
    return {"next_id": next_id, "tasks": tasks}


def save(data):
    path = storage_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def usage():
    print("Usage: todo.py <add|list|done|remove|clear> ...", file=sys.stderr)


def main(argv):
    if len(argv) < 1:
        usage()
        return 2

    command = argv[0]
    args = argv[1:]

    if command == "add":
        if not args:
            usage()
            return 2
        data = load()
        task_id = data["next_id"]
        text = " ".join(args)
        data["tasks"].append({"id": task_id, "text": text, "done": False})
        data["next_id"] = task_id + 1
        save(data)
        print(f"Added {task_id}: {text}")
        return 0

    if command == "list":
        if args:
            usage()
            return 2
        data = load()
        tasks = sorted(data["tasks"], key=lambda t: t["id"])
        if not tasks:
            print("No tasks")
            return 0
        for task in tasks:
            mark = "x" if task.get("done") else " "
            print(f"[{mark}] {task['id']}: {task['text']}")
        return 0

    if command in ("done", "remove"):
        if len(args) != 1:
            usage()
            return 2
        try:
            task_id = int(args[0])
        except ValueError:
            usage()
            return 2
        data = load()
        index = None
        for i, task in enumerate(data["tasks"]):
            if task["id"] == task_id:
                index = i
                break
        if index is None:
            print(f"Error: no task {task_id}", file=sys.stderr)
            return 1
        if command == "done":
            data["tasks"][index]["done"] = True
            save(data)
            print(f"Done {task_id}")
            return 0
        del data["tasks"][index]
        save(data)
        print(f"Removed {task_id}")
        return 0

    if command == "clear":
        if args:
            usage()
            return 2
        data = load()
        before = len(data["tasks"])
        data["tasks"] = [task for task in data["tasks"] if not task.get("done")]
        cleared = before - len(data["tasks"])
        save(data)
        print(f"Cleared {cleared}")
        return 0

    usage()
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))