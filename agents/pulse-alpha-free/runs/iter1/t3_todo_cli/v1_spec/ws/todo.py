import json
import os
import sys

USAGE = "Usage: todo.py <add|list|done|remove|clear> ..."


def store_path():
    return os.environ.get("TODO_FILE", "todo.json")


def load():
    path = store_path()
    if not os.path.exists(path):
        return {"next_id": 1, "tasks": []}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data.setdefault("next_id", 1)
    data.setdefault("tasks", [])
    return data


def save(data):
    path = store_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)


def fail_usage():
    sys.stderr.write(USAGE + "\n")
    sys.exit(2)


def main():
    args = sys.argv[1:]
    if not args:
        fail_usage()
    cmd = args[0]
    rest = args[1:]

    if cmd == "add":
        if not rest:
            fail_usage()
        text = " ".join(rest)
        data = load()
        task_id = data["next_id"]
        data["tasks"].append({"id": task_id, "text": text, "done": False})
        data["next_id"] = task_id + 1
        save(data)
        print(f"Added {task_id}: {text}")
        return

    if cmd == "list":
        if rest:
            fail_usage()
        data = load()
        tasks = sorted(data["tasks"], key=lambda t: t["id"])
        if not tasks:
            print("No tasks")
            return
        for t in tasks:
            mark = "x" if t["done"] else " "
            print(f"[{mark}] {t['id']}: {t['text']}")
        return

    if cmd in ("done", "remove"):
        if len(rest) != 1:
            fail_usage()
        try:
            task_id = int(rest[0])
        except ValueError:
            fail_usage()
        data = load()
        target = next((t for t in data["tasks"] if t["id"] == task_id), None)
        if target is None:
            sys.stderr.write(f"Error: no task {task_id}\n")
            sys.exit(1)
        if cmd == "done":
            target["done"] = True
            save(data)
            print(f"Done {task_id}")
        else:
            data["tasks"] = [t for t in data["tasks"] if t["id"] != task_id]
            save(data)
            print(f"Removed {task_id}")
        return

    if cmd == "clear":
        if rest:
            fail_usage()
        data = load()
        remaining = [t for t in data["tasks"] if not t["done"]]
        n = len(data["tasks"]) - len(remaining)
        if n:
            data["tasks"] = remaining
            save(data)
        print(f"Cleared {n}")
        return

    fail_usage()


if __name__ == "__main__":
    main()
