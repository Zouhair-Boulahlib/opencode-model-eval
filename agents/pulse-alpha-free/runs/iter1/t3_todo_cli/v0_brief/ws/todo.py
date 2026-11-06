import argparse
import json
import os
import sys

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "todos.json")


def load_tasks():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            tasks = json.load(f)
        if not isinstance(tasks, list):
            return []
        return tasks
    except (json.JSONDecodeError, OSError):
        return []


def save_tasks(tasks):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2)


def cmd_add(args):
    tasks = load_tasks()
    text = " ".join(args.text).strip()
    if not text:
        print("Error: task text cannot be empty")
        return 1
    tasks.append({"text": text, "done": False})
    save_tasks(tasks)
    print(f"Added: {text}")
    return 0


def cmd_list(args):
    tasks = load_tasks()
    if not tasks:
        print("No tasks.")
        return 0
    for i, task in enumerate(tasks, 1):
        mark = "x" if task.get("done") else " "
        print(f"{i}. [{mark}] {task.get('text', '')}")
    return 0


def cmd_done(args):
    tasks = load_tasks()
    idx = args.index - 1
    if idx < 0 or idx >= len(tasks):
        print(f"Error: no task with index {args.index}")
        return 1
    tasks[idx]["done"] = True
    save_tasks(tasks)
    print(f"Done: {tasks[idx]['text']}")
    return 0


def cmd_remove(args):
    tasks = load_tasks()
    idx = args.index - 1
    if idx < 0 or idx >= len(tasks):
        print(f"Error: no task with index {args.index}")
        return 1
    removed = tasks.pop(idx)
    save_tasks(tasks)
    print(f"Removed: {removed['text']}")
    return 0


def cmd_clear(args):
    save_tasks([])
    print("All tasks cleared.")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Simple command-line todo app")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="Add a new task")
    p_add.add_argument("text", nargs="+", help="Task description")
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list", help="List all tasks")
    p_list.set_defaults(func=cmd_list)

    p_done = sub.add_parser("done", help="Mark a task as done")
    p_done.add_argument("index", type=int, help="Task index (1-based)")
    p_done.set_defaults(func=cmd_done)

    p_remove = sub.add_parser("remove", help="Remove a task")
    p_remove.add_argument("index", type=int, help="Task index (1-based)")
    p_remove.set_defaults(func=cmd_remove)

    p_clear = sub.add_parser("clear", help="Remove all tasks")
    p_clear.set_defaults(func=cmd_clear)

    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
