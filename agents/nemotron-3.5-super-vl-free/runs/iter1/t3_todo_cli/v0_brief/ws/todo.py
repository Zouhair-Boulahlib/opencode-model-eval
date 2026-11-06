import argparse
import json
import os

TODO_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "todos.json")


def load_tasks():
    if not os.path.exists(TODO_FILE):
        return []
    try:
        with open(TODO_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_tasks(tasks):
    with open(TODO_FILE, "w") as f:
        json.dump(tasks, f, indent=2)


def add_task(title):
    tasks = load_tasks()
    task_id = max((t["id"] for t in tasks), default=0) + 1
    tasks.append({"id": task_id, "title": title, "completed": False})
    save_tasks(tasks)
    print(f"Added: [{task_id}] {title}")


def list_tasks():
    tasks = load_tasks()
    if not tasks:
        print("No tasks.")
        return
    for t in tasks:
        status = "x" if t["completed"] else " "
        print(f"[{status}] {t['id']}: {t['title']}")


def done_task(task_id):
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            t["completed"] = True
            save_tasks(tasks)
            print(f"Marked done: [{task_id}] {t['title']}")
            return
    print(f"Task [{task_id}] not found.")


def remove_task(task_id):
    tasks = load_tasks()
    filtered = [t for t in tasks if t["id"] != task_id]
    if len(filtered) == len(tasks):
        print(f"Task [{task_id}] not found.")
        return
    save_tasks(filtered)
    print(f"Removed task [{task_id}].")


def clear_tasks():
    save_tasks([])
    print("Cleared all tasks.")


def main():
    parser = argparse.ArgumentParser(description="CLI todo app")
    subparsers = parser.add_subparsers(dest="command")

    p_add = subparsers.add_parser("add", help="Add a new task")
    p_add.add_argument("title", help="Task title")

    subparsers.add_parser("list", help="List all tasks")

    p_done = subparsers.add_parser("done", help="Mark a task as done")
    p_done.add_argument("id", type=int, help="Task ID")

    p_remove = subparsers.add_parser("remove", help="Remove a task")
    p_remove.add_argument("id", type=int, help="Task ID")

    subparsers.add_parser("clear", help="Clear all tasks")

    args = parser.parse_args()

    if args.command == "add":
        add_task(args.title)
    elif args.command == "list":
        list_tasks()
    elif args.command == "done":
        done_task(args.id)
    elif args.command == "remove":
        remove_task(args.id)
    elif args.command == "clear":
        clear_tasks()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
