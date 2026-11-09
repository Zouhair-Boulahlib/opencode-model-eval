import json
import os
import sys

USAGE = "Usage: todo.py <add|list|done|remove|clear> ..."
TASKS_FILE = os.environ.get("TODO_FILE") or "todo.json"


def load_state():
    state = {"tasks": [], "next_id": 1}
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return state
    if not isinstance(data, dict):
        return state
    tasks = data.get("tasks")
    if isinstance(tasks, list):
        loaded = []
        for t in tasks:
            if not isinstance(t, dict):
                continue
            try:
                tid = int(t.get("id"))
            except (TypeError, ValueError):
                continue
            loaded.append({
                "id": tid,
                "text": str(t.get("text") or ""),
                "done": bool(t.get("done") or False),
            })
        state["tasks"] = loaded
    next_id = data.get("next_id")
    if isinstance(next_id, int) and next_id > 0:
        state["next_id"] = next_id
    if state["tasks"]:
        state["next_id"] = max(state["next_id"], max(t["id"] for t in state["tasks"]) + 1)
    return state


def save_state(state):
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump({"tasks": state["tasks"], "next_id": state["next_id"]}, f)


def find_task(state, tid):
    for t in state["tasks"]:
        if t["id"] == tid:
            return t
    return None


def parse_id(arg):
    try:
        return int(arg)
    except ValueError:
        return None


def cmd_add(state, args):
    if not args:
        print(USAGE, file=sys.stderr)
        return 2
    text = " ".join(args)
    task = {"id": state["next_id"], "text": text, "done": False}
    state["tasks"].append(task)
    state["next_id"] += 1
    save_state(state)
    print(f"Added {task['id']}: {text}")
    return 0


def cmd_list(state, args):
    if args:
        print(USAGE, file=sys.stderr)
        return 2
    if not state["tasks"]:
        print("No tasks")
        return 0
    for t in sorted(state["tasks"], key=lambda t: t["id"]):
        mark = "[x] " if t["done"] else "[ ] "
        print(f"{mark}{t['id']}: {t['text']}")
    return 0


def cmd_done(state, args):
    if len(args) != 1:
        print(USAGE, file=sys.stderr)
        return 2
    tid = parse_id(args[0])
    if tid is None:
        print(USAGE, file=sys.stderr)
        return 2
    task = find_task(state, tid)
    if task is None:
        print(f"Error: no task {tid}", file=sys.stderr)
        return 1
    task["done"] = True
    save_state(state)
    print(f"Done {tid}")
    return 0


def cmd_remove(state, args):
    if len(args) != 1:
        print(USAGE, file=sys.stderr)
        return 2
    tid = parse_id(args[0])
    if tid is None:
        print(USAGE, file=sys.stderr)
        return 2
    task = find_task(state, tid)
    if task is None:
        print(f"Error: no task {tid}", file=sys.stderr)
        return 1
    state["tasks"].remove(task)
    save_state(state)
    print(f"Removed {tid}")
    return 0


def cmd_clear(state, args):
    if args:
        print(USAGE, file=sys.stderr)
        return 2
    remaining = [t for t in state["tasks"] if not t["done"]]
    cleared = len(state["tasks"]) - len(remaining)
    state["tasks"] = remaining
    save_state(state)
    print(f"Cleared {cleared}")
    return 0


def main(argv):
    if not argv:
        print(USAGE, file=sys.stderr)
        return 2
    command = argv[0]
    args = argv[1:]
    state = load_state()
    if command == "add":
        return cmd_add(state, args)
    if command == "list":
        return cmd_list(state, args)
    if command == "done":
        return cmd_done(state, args)
    if command == "remove":
        return cmd_remove(state, args)
    if command == "clear":
        return cmd_clear(state, args)
    print(USAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
