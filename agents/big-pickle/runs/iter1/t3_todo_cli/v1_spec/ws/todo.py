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
    except (OSError, ValueError):
        return {"next_id": 1, "tasks": []}
    if not isinstance(data, dict):
        return {"next_id": 1, "tasks": []}
    tasks = data.get("tasks")
    if not isinstance(tasks, list):
        tasks = []
    next_id = data.get("next_id")
    if not isinstance(next_id, int) or isinstance(next_id, bool):
        next_id = 1
    if tasks:
        next_id = max(next_id, max(t.get("id", 0) for t in tasks if isinstance(t, dict)) + 1)
    return {"next_id": next_id, "tasks": tasks}


def save(data):
    path = storage_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
        f.write("\n")


def parse_id(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def find_task(data, task_id):
    for task in data["tasks"]:
        if task.get("id") == task_id:
            return task
    return None


def cmd_add(args):
    if not args:
        usage()
    text = " ".join(args)
    data = load()
    task_id = data["next_id"]
    data["tasks"].append({"id": task_id, "text": text, "done": False})
    data["next_id"] = task_id + 1
    save(data)
    print("Added {}: {}".format(task_id, text))


def cmd_list(args):
    if args:
        usage()
    data = load()
    tasks = sorted(data["tasks"], key=lambda t: t.get("id", 0))
    if not tasks:
        print("No tasks")
        return
    for task in tasks:
        mark = "x" if task.get("done") else " "
        print("[{}] {}: {}".format(mark, task["id"], task["text"]))


def cmd_done(args):
    if len(args) != 1:
        usage()
    task_id = parse_id(args[0])
    if task_id is None:
        usage()
    data = load()
    task = find_task(data, task_id)
    if task is None:
        fail("Error: no task {}".format(task_id))
    task["done"] = True
    save(data)
    print("Done {}".format(task_id))


def cmd_remove(args):
    if len(args) != 1:
        usage()
    task_id = parse_id(args[0])
    if task_id is None:
        usage()
    data = load()
    task = find_task(data, task_id)
    if task is None:
        fail("Error: no task {}".format(task_id))
    data["tasks"] = [t for t in data["tasks"] if t.get("id") != task_id]
    save(data)
    print("Removed {}".format(task_id))


def cmd_clear(args):
    if args:
        usage()
    data = load()
    done = [t for t in data["tasks"] if t.get("done")]
    data["tasks"] = [t for t in data["tasks"] if not t.get("done")]
    if done:
        save(data)
    print("Cleared {}".format(len(done)))


def usage():
    sys.stderr.write(USAGE + "\n")
    sys.exit(2)


def fail(message):
    sys.stderr.write(message + "\n")
    sys.exit(1)


def main():
    argv = sys.argv[1:]
    if not argv:
        usage()
    command = argv[0]
    args = argv[1:]
    commands = {
        "add": cmd_add,
        "list": cmd_list,
        "done": cmd_done,
        "remove": cmd_remove,
        "clear": cmd_clear,
    }
    handler = commands.get(command)
    if handler is None:
        usage()
    handler(args)


if __name__ == "__main__":
    main()
