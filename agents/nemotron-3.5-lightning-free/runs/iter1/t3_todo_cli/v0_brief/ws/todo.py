import json
import os
import sys

TODO_FILE = "tasks.json"


def load_tasks():
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, "r") as f:
            return json.load(f)
    return []


def save_tasks(tasks):
    with open(TODO_FILE, "w") as f:
        json.dump(tasks, f, indent=2)


def add_task(description):
    tasks = load_tasks()
    tasks.append({"description": description, "done": False})
    save_tasks(tasks)
    print(f"Added task: {description}")


def list_tasks():
    tasks = load_tasks()
    if not tasks:
        print("No tasks found.")
        return
    for i, task in enumerate(tasks, 1):
        status = "✓" if task["done"] else " "
        print(f"{i}. [{status}] {task['description']}")


def mark_done(index):
    tasks = load_tasks()
    if 1 <= index <= len(tasks):
        tasks[index - 1]["done"] = True
        save_tasks(tasks)
        print(f"Marked task {index} as done.")
    else:
        print("Invalid task number.")


def remove_task(index):
    tasks = load_tasks()
    if 1 <= index <= len(tasks):
        removed = tasks.pop(index - 1)
        save_tasks(tasks)
        print(f"Removed task: {removed['description']}")
    else:
        print("Invalid task number.")


def clear_tasks():
    tasks = load_tasks()
    if not tasks:
        print("No tasks to clear.")
        return
    save_tasks([])
    print("All tasks cleared.")


def main():
    if len(sys.argv) < 2:
        print("Usage: todo.py <command> [argument]")
        print("Commands: add, list, done, remove, clear")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "add":
        if len(sys.argv) < 3:
            print("Error: Description required for 'add' command.")
            sys.exit(1)
        add_task(" ".join(sys.argv[2:]))
    elif command == "list":
        list_tasks()
    elif command == "done":
        if len(sys.argv) < 3:
            print("Error: Task number required for 'done' command.")
            sys.exit(1)
        try:
            mark_done(int(sys.argv[2]))
        except ValueError:
            print("Error: Task number must be an integer.")
            sys.exit(1)
    elif command == "remove":
        if len(sys.argv) < 3:
            print("Error: Task number required for 'remove' command.")
            sys.exit(1)
        try:
            remove_task(int(sys.argv[2]))
        except ValueError:
            print("Error: Task number must be an integer.")
            sys.exit(1)
    elif command == "clear":
        clear_tasks()
    else:
        print(f"Unknown command: {command}")
        print("Usage: todo.py <command> [argument]")
        sys.exit(1)


if __name__ == "__main__":
    main()