import json
import os
import sys

USAGE = "Usage: todo.py <add|list|done|remove|clear> ..."


def load():
    path = os.environ.get("TODO_FILE") or "todo.json"
    if not os.path.exists(path):
        return path, [], 1
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return path, [], 1
    if isinstance(data, dict):
        tasks = data.get("tasks")
        if not isinstance(tasks, list):
            tasks = []
        try:
            nxt = int(data.get("next", 1))
        except (TypeError, ValueError):
            nxt = 1
        return path, tasks, max(nxt, 1)
    if isinstance(data, list):
        nxt = max((t.get("id", 0) for t in data if isinstance(t, dict)), default=0) + 1
        return path, data, nxt
    return path, [], 1


def save(path, tasks, nxt):
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"tasks": tasks, "next": nxt}, f)


def main(argv):
    if not argv:
        print(USAGE, file=sys.stderr)
        return 2
    cmd = argv[0]
    args = argv[1:]

    if cmd == "add":
        if not args:
            print(USAGE, file=sys.stderr)
            return 2
        text = " ".join(args)
        path, tasks, nxt = load()
        tid = nxt
        tasks.append({"id": tid, "text": text, "done": False})
        save(path, tasks, tid + 1)
        print(f"Added {tid}: {text}")
        return 0

    if cmd == "list":
        _, tasks, _ = load()
        if not tasks:
            print("No tasks")
        else:
            for t in sorted(tasks, key=lambda t: t["id"]):
                mark = "x" if t.get("done") else " "
                print(f"[{mark}] {t['id']}: {t['text']}")
        return 0

    if cmd in ("done", "remove"):
        if len(args) != 1 or not args[0].lstrip("-").isdigit():
            print(USAGE, file=sys.stderr)
            return 2
        tid = int(args[0])
        path, tasks, nxt = load()
        for t in tasks:
            if t["id"] == tid:
                if cmd == "done":
                    t["done"] = True
                    save(path, tasks, nxt)
                    print(f"Done {tid}")
                else:
                    tasks.remove(t)
                    save(path, tasks, nxt)
                    print(f"Removed {tid}")
                return 0
        print(f"Error: no task {tid}", file=sys.stderr)
        return 1

    if cmd == "clear":
        path, tasks, nxt = load()
        kept = [t for t in tasks if not t.get("done")]
        n = len(tasks) - len(kept)
        if n:
            save(path, kept, nxt)
        print(f"Cleared {n}")
        return 0

    print(USAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
