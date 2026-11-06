import json
import os
import sys


def storage_path():
    return os.environ.get("TODO_FILE", os.path.join(os.getcwd(), "todo.json"))


def load_tasks():
    path = storage_path()
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)


def save_tasks(tasks):
    path = storage_path()
    with open(path, "w") as f:
        json.dump(tasks, f)


def next_id(tasks):
    if not tasks:
        return 1
    return max(t["id"] for t in tasks) + 1


def find_task(tasks, task_id):
    for t in tasks:
        if t["id"] == task_id:
            return t
    return None


def main(argv):
    if len(argv) < 2:
        sys.stderr.write("Usage: todo.py <add|list|done|remove|clear> ...\n")
        return 2

    command = argv[1]

    if command == "add":
        if len(argv) < 3:
            sys.stderr.write("Usage: todo.py <add|list|done|remove|clear> ...\n")
            return 2
        text = " ".join(argv[2:])
        tasks = load_tasks()
        task_id = next_id(tasks)
        tasks.append({"id": task_id, "text": text, "done": False})
        save_tasks(tasks)
        print("Added %d: %s" % (task_id, text))
        return 0

    if command == "list":
        if len(argv) != 2:
            sys.stderr.write("Usage: todo.py <add|list|done|remove|clear> ...\n")
            return 2
        tasks = load_tasks()
        if not tasks:
            print("No tasks")
            return 0
        for t in sorted(tasks, key=lambda x: x["id"]):
            mark = "x" if t.get("done") else " "
            print("[%s] %d: %s" % (mark, t["id"], t["text"]))
        return 0

    if command == "done":
        if len(argv) != 3:
            sys.stderr.write("Usage: todo.py <add|list|done|remove|clear> ...\n")
            return 2
        try:
            task_id = int(argv[2])
        except ValueError:
            sys.stderr.write("Usage: todo.py <add|list|done|remove|clear> ...\n")
            return 2
        tasks = load_tasks()
        task = find_task(tasks, task_id)
        if task is None:
            sys.stderr.write("Error: no task %d\n" % task_id)
            return 1
        task["done"] = True
        save_tasks(tasks)
        print("Done %d" % task_id)
        return 0

    if command == "remove":
        if len(argv) != 3:
            sys.stderr.write("Usage: todo.py <add|list|done|remove|clear> ...\n")
            return 2
        try:
            task_id = int(argv[2])
        except ValueError:
            sys.stderr.write("Usage: todo.py <add|list|done|remove|clear> ...\n")
            return 2
        tasks = load_tasks()
        task = find_task(tasks, task_id)
        if task is None:
            sys.stderr.write("Error: no task %d\n" % task_id)
            return 1
        tasks = [t for t in tasks if t["id"] != task_id]
        save_tasks(tasks)
        print("Removed %d" % task_id)
        return 0

    if command == "clear":
        if len(argv) != 2:
            sys.stderr.write("Usage: todo.py <add|list|done|remove|clear> ...\n")
            return 2
        tasks = load_tasks()
        done_tasks = [t for t in tasks if t.get("done")]
        tasks = [t for t in tasks if not t.get("done")]
        save_tasks(tasks)
        print("Cleared %d" % len(done_tasks))
        return 0

    sys.stderr.write("Usage: todo.py <add|list|done|remove|clear> ...\n")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
