import json
import os
import sys


USAGE = "Usage: todo.py <add|list|done|remove|clear> ..."


def get_file_path():
    return os.environ.get("TODO_FILE", "todo.json")


def load_state():
    path = get_file_path()
    if not os.path.exists(path):
        return [], 1
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (ValueError, OSError):
        return [], 1
    if not isinstance(data, dict):
        return [], 1
    tasks = data.get("tasks", [])
    next_id = data.get("next_id", 1)
    if not isinstance(next_id, int) or isinstance(next_id, bool):
        next_id = 1
    if not isinstance(tasks, list):
        tasks = []
    tasks = [t for t in tasks if isinstance(t, dict)]
    tasks.sort(key=lambda t: t.get("id", 0))
    for t in tasks:
        if not isinstance(t.get("id"), int) or isinstance(t.get("id"), bool):
            t["id"] = 0
        if "done" not in t:
            t["done"] = False
        if not isinstance(t.get("text"), str):
            t["text"] = ""
    if tasks:
        next_id = max(next_id, max(t.get("id", 0) for t in tasks) + 1)
    return tasks, next_id


def save_state(tasks, next_id):
    path = get_file_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"tasks": tasks, "next_id": next_id}, f)


def find_task(tasks, task_id):
    for task in tasks:
        if task.get("id") == task_id:
            return task
    return None


def cmd_add(words):
    tasks, next_id = load_state()
    text = " ".join(words)
    task = {"id": next_id, "text": text, "done": False}
    tasks.append(task)
    save_state(tasks, next_id + 1)
    print("Added {}: {}".format(task["id"], text))


def cmd_list():
    tasks, _ = load_state()
    if not tasks:
        print("No tasks")
        return
    for task in tasks:
        marker = "x" if task.get("done") else " "
        print("[{}] {}: {}".format(marker, task["id"], task["text"]))


def cmd_done(task_id):
    tasks, next_id = load_state()
    task = find_task(tasks, task_id)
    if task is None:
        sys.stderr.write("Error: no task {}\n".format(task_id))
        sys.exit(1)
    task["done"] = True
    save_state(tasks, next_id)
    print("Done {}".format(task_id))


def cmd_remove(task_id):
    tasks, next_id = load_state()
    task = find_task(tasks, task_id)
    if task is None:
        sys.stderr.write("Error: no task {}\n".format(task_id))
        sys.exit(1)
    tasks = [t for t in tasks if t.get("id") != task_id]
    save_state(tasks, next_id)
    print("Removed {}".format(task_id))


def cmd_clear():
    tasks, next_id = load_state()
    kept = [t for t in tasks if not t.get("done")]
    deleted = len(tasks) - len(kept)
    save_state(kept, next_id)
    print("Cleared {}".format(deleted))


def usage_error():
    sys.stderr.write(USAGE + "\n")
    sys.exit(2)


def main(argv):
    if len(argv) < 2:
        usage_error()
    command = argv[1]
    if command == "add":
        if len(argv) < 3:
            usage_error()
        cmd_add(argv[2:])
    elif command == "list":
        if len(argv) != 2:
            usage_error()
        cmd_list()
    elif command == "done":
        if len(argv) != 3:
            usage_error()
        try:
            task_id = int(argv[2])
        except ValueError:
            usage_error()
        cmd_done(task_id)
    elif command == "remove":
        if len(argv) != 3:
            usage_error()
        try:
            task_id = int(argv[2])
        except ValueError:
            usage_error()
        cmd_remove(task_id)
    elif command == "clear":
        if len(argv) != 2:
            usage_error()
        cmd_clear()
    else:
        usage_error()


if __name__ == "__main__":
    main(sys.argv)
