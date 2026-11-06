import json
import os
import sys

USAGE = "Usage: todo.py <add|list|done|remove|clear> ..."


def path():
    return os.environ.get("TODO_FILE") or os.path.join(os.getcwd(), "todo.json")


def load():
    try:
        with open(path(), encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"next_id": 1, "tasks": []}


def save(data):
    p = path()
    d = os.path.dirname(p)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f)


def usage():
    print(USAGE, file=sys.stderr)
    sys.exit(2)


def find(data, tid):
    for t in data["tasks"]:
        if t["id"] == tid:
            return t
    print(f"Error: no task {tid}", file=sys.stderr)
    sys.exit(1)


def parse_id(args):
    if len(args) != 1 or not args[0].isdigit():
        usage()
    return int(args[0])


def main(argv):
    if not argv:
        usage()
    cmd, args = argv[0], argv[1:]
    data = load()
    if cmd == "add":
        if not args:
            usage()
        text = " ".join(args)
        tid = data["next_id"]
        data["tasks"].append({"id": tid, "text": text, "done": False})
        data["next_id"] = tid + 1
        save(data)
        print(f"Added {tid}: {text}")
    elif cmd == "list":
        if args:
            usage()
        if not data["tasks"]:
            print("No tasks")
        for t in sorted(data["tasks"], key=lambda t: t["id"]):
            print(f"[{'x' if t['done'] else ' '}] {t['id']}: {t['text']}")
    elif cmd == "done":
        tid = parse_id(args)
        find(data, tid)["done"] = True
        save(data)
        print(f"Done {tid}")
    elif cmd == "remove":
        tid = parse_id(args)
        t = find(data, tid)
        data["tasks"].remove(t)
        save(data)
        print(f"Removed {tid}")
    elif cmd == "clear":
        if args:
            usage()
        before = len(data["tasks"])
        data["tasks"] = [t for t in data["tasks"] if not t["done"]]
        save(data)
        print(f"Cleared {before - len(data['tasks'])}")
    else:
        usage()


if __name__ == "__main__":
    main(sys.argv[1:])
