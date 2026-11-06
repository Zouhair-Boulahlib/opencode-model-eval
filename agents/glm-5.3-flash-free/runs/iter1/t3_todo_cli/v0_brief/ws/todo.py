import argparse
import json
import os
import sys

TODO_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "todos.json")


def load_tasks():
    if not os.path.exists(TODO_FILE):
        return []
    try:
        with open(TODO_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        return []
    except (json.JSONDecodeError, OSError):
        return []


def save_tasks(tasks):
    with open(TODO_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)


def next_id(tasks):
    if not tasks:
        return 1
    return max(t["id"] for t in tasks) + 1


def cmd_add(args):
    tasks = load_tasks()
    task = {"id": next_id(tasks), "task": args.text, "done": False}
    tasks.append(task)
    save_tasks(tasks)
    print(f"Added task {task['id']}: {task['task']}")


def cmd_list(args):
    tasks = load_tasks()
    if not tasks:
        print("No tasks.")
        return
    for t in tasks:
        status = "x" if t["done"] else " "
        print(f"[{status}] {t['id']}: {t['task']}")


def find_task(tasks, id_str):
    try:
        task_id = int(id_str)
    except ValueError:
        print(f"Invalid id: {id_str}")
        sys.exit(1)
    for t in tasks:
        if t["id"] == task_id:
            return t
    print(f"Task {task_id} not found.")
    sys.exit(1)


def cmd_done(args):
    tasks = load_tasks()
    task = find_task(tasks, args.id)
    task["done"] = True
    save_tasks(tasks)
    print(f"Marked task {task['id']} as done: {task['task']}")


def cmd_remove(args):
    tasks = load_tasks()
    task = find_task(tasks, args.id)
    tasks.remove(task)
    save_tasks(tasks)
    print(f"Removed task {task['id']}: {task['task']}")


def cmd_clear(args):
    tasks = load_tasks()
    if args.completed:
        remaining = [t for t in tasks if not t["done"]]
        removed = len(tasks) - len(remaining)
    else:
        removed = len(tasks)
        remaining = []
    save_tasks(remaining)
    print(f"Cleared {removed} task(s).")


def main():
    parser = argparse.ArgumentParser(description="Simple command-line todo app")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="Add a new task")
    p_add.add_argument("text", nargs="+", help="Task description")
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list", help="List all tasks")
    p_list.set_defaults(func=cmd_list)

    p_done = sub.add_parser("done", help="Mark a task as done")
    p_done.add_argument("id", help="Task id")
    p_done.set_defaults(func=cmd_done)

    p_remove = sub.add_parser("remove", help="Remove a task")
    p_remove.add_argument("id", help="Task id")
    p_remove.set_defaults(func=cmd_remove)

    p_clear = sub.add_parser("clear", help="Remove all tasks")
    p_clear.add_argument("--completed", action="store_true", help="Only remove completed tasks")
    p_clear.set_defaults(func=cmd_clear)

    args = parser.parse_args()
    if args.command == "add":
        args.text = " ".join(args.text)
    args.func(args)


if __name__ == "__main__":
    main()
