import json
import os
import sys


def get_todo_file():
    return os.environ.get("TODO_FILE", "todo.json")


def load_tasks(path):
    if not os.path.exists(path):
        return [], 1
    with open(path, "r") as f:
        data = json.load(f)
    tasks = data.get("tasks", [])
    next_id = data.get("next_id", 1)
    return tasks, next_id


def save_tasks(path, tasks, next_id):
    with open(path, "w") as f:
        json.dump({"tasks": tasks, "next_id": next_id}, f)


def cmd_add(args):
    text = " ".join(args)
    path = get_todo_file()
    tasks, next_id = load_tasks(path)
    tasks.append({"id": next_id, "text": text, "done": False})
    next_id += 1
    save_tasks(path, tasks, next_id)
    print(f"Added {next_id - 1}: {text}")


def cmd_list(args):
    path = get_todo_file()
    tasks, _ = load_tasks(path)
    if not tasks:
        print("No tasks")
        return
    for t in tasks:
        marker = "x" if t["done"] else " "
        print(f"[{marker}] {t['id']}: {t['text']}")


def cmd_done(args):
    if not args:
        print_usage()
        sys.exit(2)
    id_str = args[0]
    try:
        task_id = int(id_str)
    except ValueError:
        print_usage()
        sys.exit(2)
    path = get_todo_file()
    tasks, _ = load_tasks(path)
    for t in tasks:
        if t["id"] == task_id:
            t["done"] = True
            save_tasks(path, tasks, _)
            print(f"Done {task_id}")
            return
    print(f"Error: no task {task_id}", file=sys.stderr)
    sys.exit(1)


def cmd_remove(args):
    if not args:
        print_usage()
        sys.exit(2)
    id_str = args[0]
    try:
        task_id = int(id_str)
    except ValueError:
        print_usage()
        sys.exit(2)
    path = get_todo_file()
    tasks, _ = load_tasks(path)
    for i, t in enumerate(tasks):
        if t["id"] == task_id:
            tasks.pop(i)
            save_tasks(path, tasks, _)
            print(f"Removed {task_id}")
            return
    print(f"Error: no task {task_id}", file=sys.stderr)
    sys.exit(1)


def cmd_clear(args):
    path = get_todo_file()
    tasks, _ = load_tasks(path)
    done_tasks = [t for t in tasks if t["done"]]
    tasks = [t for t in tasks if not t["done"]]
    save_tasks(path, tasks, _)
    print(f"Cleared {len(done_tasks)}")


def print_usage():
    print("Usage: todo.py <add|list|done|remove|clear> ...", file=sys.stderr)


def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(2)

    command = sys.argv[1]
    args = sys.argv[2:]

    if command == "add":
        cmd_add(args)
    elif command == "list":
        cmd_list(args)
    elif command == "done":
        cmd_done(args)
    elif command == "remove":
        cmd_remove(args)
    elif command == "clear":
        cmd_clear(args)
    else:
        print_usage()
        sys.exit(2)


if __name__ == "__main__":
    main()