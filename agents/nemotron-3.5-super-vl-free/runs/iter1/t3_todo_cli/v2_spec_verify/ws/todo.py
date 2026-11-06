import json
import os
import sys


USAGE = "Usage: todo.py <add|list|done|remove|clear> ..."


def todo_file():
    return os.environ.get("TODO_FILE", "todo.json")


def load_tasks():
    path = todo_file()
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except ValueError:
            return []
    if not isinstance(data, list):
        return []
    return data


def save_tasks(tasks):
    path = todo_file()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(tasks, f)


def next_id(tasks):
    if not tasks:
        return 1
    return max(task["id"] for task in tasks) + 1


def find_task(tasks, task_id):
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None


def cmd_add(words):
    tasks = load_tasks()
    text = " ".join(words)
    task = {"id": next_id(tasks), "text": text, "done": False}
    tasks.append(task)
    save_tasks(tasks)
    print("Added %d: %s" % (task["id"], text))
    return 0


def cmd_list():
    tasks = load_tasks()
    if not tasks:
        print("No tasks")
        return 0
    for task in sorted(tasks, key=lambda t: t["id"]):
        mark = "x" if task.get("done") else " "
        print("[%s] %d: %s" % (mark, task["id"], task["text"]))
    return 0


def cmd_done(task_id):
    tasks = load_tasks()
    task = find_task(tasks, task_id)
    if task is None:
        sys.stderr.write("Error: no task %d\n" % task_id)
        return 1
    task["done"] = True
    save_tasks(tasks)
    print("Done %d" % task_id)
    return 0


def cmd_remove(task_id):
    tasks = load_tasks()
    task = find_task(tasks, task_id)
    if task is None:
        sys.stderr.write("Error: no task %d\n" % task_id)
        return 1
    tasks = [t for t in tasks if t["id"] != task_id]
    save_tasks(tasks)
    print("Removed %d" % task_id)
    return 0


def cmd_clear():
    tasks = load_tasks()
    done_tasks = [t for t in tasks if t.get("done")]
    tasks = [t for t in tasks if not t.get("done")]
    save_tasks(tasks)
    print("Cleared %d" % len(done_tasks))
    return 0


def main(argv):
    if not argv:
        sys.stderr.write(USAGE + "\n")
        return 2

    command = argv[0]

    if command == "add":
        if len(argv) < 2:
            sys.stderr.write(USAGE + "\n")
            return 2
        return cmd_add(argv[1:])

    if command == "list":
        if len(argv) != 1:
            sys.stderr.write(USAGE + "\n")
            return 2
        return cmd_list()

    if command == "done":
        if len(argv) != 2:
            sys.stderr.write(USAGE + "\n")
            return 2
        try:
            task_id = int(argv[1])
        except ValueError:
            sys.stderr.write(USAGE + "\n")
            return 2
        return cmd_done(task_id)

    if command == "remove":
        if len(argv) != 2:
            sys.stderr.write(USAGE + "\n")
            return 2
        try:
            task_id = int(argv[1])
        except ValueError:
            sys.stderr.write(USAGE + "\n")
            return 2
        return cmd_remove(task_id)

    if command == "clear":
        if len(argv) != 1:
            sys.stderr.write(USAGE + "\n")
            return 2
        return cmd_clear()

    sys.stderr.write(USAGE + "\n")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
