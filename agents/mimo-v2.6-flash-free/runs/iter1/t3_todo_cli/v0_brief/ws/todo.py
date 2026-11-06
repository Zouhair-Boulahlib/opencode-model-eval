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
        return tasks if isinstance(tasks, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_tasks(tasks):
    tmp = DATA_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA_FILE)


def find_task(tasks, key):
    if not tasks:
        print("No tasks found.", file=sys.stderr)
        return None, None
    if key.isdigit():
        idx = int(key)
        if 1 <= idx <= len(tasks):
            return idx - 1, tasks[idx - 1]
        print(f"Invalid task number: {key}", file=sys.stderr)
        return None, None
    key_lower = key.lower()
    matches = [i for i, t in enumerate(tasks) if t.get("text", "").lower() == key_lower]
    if len(matches) == 1:
        return matches[0], tasks[matches[0]]
    if len(matches) > 1:
        print(f"Ambiguous task name: {key} (use its number)", file=sys.stderr)
        return None, None
    print(f"No task matching: {key}", file=sys.stderr)
    return None, None


def cmd_add(args):
    tasks = load_tasks()
    task = {"text": args.text, "done": False}
    tasks.append(task)
    save_tasks(tasks)
    print(f"Added task {len(tasks)}: {args.text}")


def cmd_list(args):
    tasks = load_tasks()
    if not tasks:
        print("No tasks.")
        return
    for i, t in enumerate(tasks, 1):
        mark = "x" if t.get("done") else " "
        print(f"[{mark}] {i}. {t.get('text', '')}")


def cmd_done(args):
    tasks = load_tasks()
    idx, task = find_task(tasks, args.key)
    if idx is None:
        sys.exit(1)
    if task.get("done"):
        print(f"Task {idx + 1} is already done.")
        return
    task["done"] = True
    save_tasks(tasks)
    print(f"Done: {idx + 1}. {task['text']}")


def cmd_remove(args):
    tasks = load_tasks()
    idx, task = find_task(tasks, args.key)
    if idx is None:
        sys.exit(1)
    removed = tasks.pop(idx)
    save_tasks(tasks)
    print(f"Removed {idx + 1}. {removed['text']}")


def cmd_clear(args):
    tasks = load_tasks()
    remaining = [t for t in tasks if not t.get("done")]
    if args.all:
        removed = len(tasks)
        save_tasks([])
        print(f"Cleared all {removed} task(s).")
    else:
        removed = len(tasks) - len(remaining)
        save_tasks(remaining)
        print(f"Cleared {removed} completed task(s).")


def main():
    parser = argparse.ArgumentParser(prog="todo", description="Simple JSON-backed todo list.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="Add a new task")
    p_add.add_argument("text", help="Task description")
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list", help="List all tasks")
    p_list.set_defaults(func=cmd_list)

    p_done = sub.add_parser("done", help="Mark a task as completed")
    p_done.add_argument("key", help="Task number or exact text")
    p_done.set_defaults(func=cmd_done)

    p_remove = sub.add_parser("remove", help="Remove a task")
    p_remove.add_argument("key", help="Task number or exact text")
    p_remove.set_defaults(func=cmd_remove)

    p_clear = sub.add_parser("clear", help="Remove completed tasks")
    p_clear.add_argument("--all", action="store_true", help="Remove all tasks, not just completed ones")
    p_clear.set_defaults(func=cmd_clear)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
