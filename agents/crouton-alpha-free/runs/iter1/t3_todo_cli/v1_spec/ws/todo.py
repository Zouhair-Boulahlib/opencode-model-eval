#!/usr/bin/env python3
import json
import os
import sys

USAGE = "Usage: todo.py <add|list|done|remove|clear> ..."


def get_path():
    return os.environ.get("TODO_FILE") or "todo.json"


def load():
    path = get_path()
    if not os.path.exists(path):
        return {"next_id": 1, "tasks": []}
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        return {"next_id": 1, "tasks": []}
    if not content.strip():
        return {"next_id": 1, "tasks": []}
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return {"next_id": 1, "tasks": []}
    tasks = []
    next_id = None
    if isinstance(data, dict):
        raw_tasks = data.get("tasks", [])
        if isinstance(raw_tasks, list):
            tasks = raw_tasks
        next_id = data.get("next_id")
        if next_id is None:
            next_id = data.get("nextId")
    elif isinstance(data, list):
        tasks = data
    normalized = []
    max_id = 0
    for item in tasks:
        if not isinstance(item, dict):
            continue
        try:
            tid = int(item.get("id"))
        except (TypeError, ValueError):
            continue
        text = str(item.get("text", ""))
        done = bool(item.get("done", False))
        normalized.append({"id": tid, "text": text, "done": done})
        if tid > max_id:
            max_id = tid
    normalized.sort(key=lambda t: t["id"])
    if next_id is None:
        next_id = max_id + 1
    else:
        try:
            next_id = int(next_id)
        except (TypeError, ValueError):
            next_id = max_id + 1
        if next_id <= max_id:
            next_id = max_id + 1
    return {"next_id": next_id, "tasks": normalized}


def save(state):
    path = get_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f)


def usage_error():
    print(USAGE, file=sys.stderr)
    return 2


def main(argv):
    if len(argv) < 2:
        return usage_error()

    cmd = argv[1]
    args = argv[2:]

    if cmd == "add":
        if len(args) < 1:
            return usage_error()
        text = " ".join(args)
        state = load()
        tid = state["next_id"]
        state["tasks"].append({"id": tid, "text": text, "done": False})
        state["tasks"].sort(key=lambda t: t["id"])
        state["next_id"] = tid + 1
        save(state)
        print(f"Added {tid}: {text}")
        return 0

    elif cmd == "list":
        if len(args) != 0:
            return usage_error()
        state = load()
        tasks = sorted(state["tasks"], key=lambda t: t["id"])
        if not tasks:
            print("No tasks")
        else:
            for t in tasks:
                mark = "x" if t["done"] else " "
                print(f"[{mark}] {t['id']}: {t['text']}")
        return 0

    elif cmd == "done":
        if len(args) != 1:
            return usage_error()
        try:
            tid = int(args[0], 10)
        except ValueError:
            return usage_error()
        state = load()
        for t in state["tasks"]:
            if t["id"] == tid:
                t["done"] = True
                save(state)
                print(f"Done {tid}")
                return 0
        print(f"Error: no task {tid}", file=sys.stderr)
        return 1

    elif cmd == "remove":
        if len(args) != 1:
            return usage_error()
        try:
            tid = int(args[0], 10)
        except ValueError:
            return usage_error()
        state = load()
        for i, t in enumerate(state["tasks"]):
            if t["id"] == tid:
                del state["tasks"][i]
                save(state)
                print(f"Removed {tid}")
                return 0
        print(f"Error: no task {tid}", file=sys.stderr)
        return 1

    elif cmd == "clear":
        if len(args) != 0:
            return usage_error()
        state = load()
        before = len(state["tasks"])
        state["tasks"] = [t for t in state["tasks"] if not t["done"]]
        n = before - len(state["tasks"])
        save(state)
        print(f"Cleared {n}")
        return 0

    else:
        return usage_error()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
