import json
import os
import sys

USAGE = "Usage: todo.py <add|list|done|remove|clear> ..."


def todo_file():
    return os.environ.get("TODO_FILE", "todo.json")


def empty_state():
    return {"next_id": 1, "tasks": []}


def load_state():
    path = todo_file()
    if not os.path.exists(path):
        return empty_state()
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (ValueError, OSError):
        return empty_state()
    if not isinstance(data, dict):
        return empty_state()
    tasks = data.get("tasks")
    next_id = data.get("next_id")
    if not isinstance(tasks, list) or not isinstance(next_id, int):
        return empty_state()
    return {"next_id": next_id, "tasks": tasks}


def save_state(state):
    path = todo_file()
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(state, handle, ensure_ascii=False, indent=2)


def find_task(state, task_id):
    for task in state["tasks"]:
        if task.get("id") == task_id:
            return task
    return None


def parse_id(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def cmd_add(words):
    if not words:
        sys.stderr.write(USAGE + "\n")
        return 2
    state = load_state()
    task_id = state["next_id"]
    text = " ".join(words)
    state["tasks"].append({"id": task_id, "text": text, "done": False})
    state["next_id"] = task_id + 1
    save_state(state)
    print("Added %d: %s" % (task_id, text))
    return 0


def cmd_list():
    state = load_state()
    tasks = state["tasks"]
    if not tasks:
        print("No tasks")
        return 0
    for task in sorted(tasks, key=lambda t: t.get("id", 0)):
        marker = "x" if task.get("done") else " "
        print("[%s] %d: %s" % (marker, task.get("id"), task.get("text")))
    return 0


def cmd_done(args):
    task_id = parse_id(args[0])
    if task_id is None:
        sys.stderr.write(USAGE + "\n")
        return 2
    state = load_state()
    task = find_task(state, task_id)
    if task is None:
        sys.stderr.write("Error: no task %d\n" % task_id)
        return 1
    task["done"] = True
    save_state(state)
    print("Done %d" % task_id)
    return 0


def cmd_remove(args):
    task_id = parse_id(args[0])
    if task_id is None:
        sys.stderr.write(USAGE + "\n")
        return 2
    state = load_state()
    task = find_task(state, task_id)
    if task is None:
        sys.stderr.write("Error: no task %d\n" % task_id)
        return 1
    state["tasks"].remove(task)
    save_state(state)
    print("Removed %d" % task_id)
    return 0


def cmd_clear():
    state = load_state()
    remaining = [task for task in state["tasks"] if not task.get("done")]
    deleted = len(state["tasks"]) - len(remaining)
    if deleted:
        state["tasks"] = remaining
        save_state(state)
    print("Cleared %d" % deleted)
    return 0


def main(argv):
    if len(argv) < 2:
        sys.stderr.write(USAGE + "\n")
        return 2

    command = argv[1]
    args = argv[2:]

    if command == "add":
        if not args:
            sys.stderr.write(USAGE + "\n")
            return 2
        return cmd_add(args)
    if command == "list":
        if args:
            sys.stderr.write(USAGE + "\n")
            return 2
        return cmd_list()
    if command == "done":
        if len(args) != 1:
            sys.stderr.write(USAGE + "\n")
            return 2
        return cmd_done(args)
    if command == "remove":
        if len(args) != 1:
            sys.stderr.write(USAGE + "\n")
            return 2
        return cmd_remove(args)
    if command == "clear":
        if args:
            sys.stderr.write(USAGE + "\n")
            return 2
        return cmd_clear()

    sys.stderr.write(USAGE + "\n")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
