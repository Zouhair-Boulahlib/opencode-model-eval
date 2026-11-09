import sys
import os
import json


def get_todo_file():
    return os.environ.get("TODO_FILE", "todo.json")


def load():
    path = get_todo_file()
    if not os.path.exists(path):
        return {"max_id": 0, "tasks": []}
    with open(path, "r") as f:
        return json.load(f)


def save(data):
    path = get_todo_file()
    with open(path, "w") as f:
        json.dump(data, f)


def print_usage():
    sys.stderr.write("Usage: todo.py <add|list|done|remove|clear> ...\n")
    sys.exit(2)


def main():
    args = sys.argv[1:]

    if not args:
        print_usage()

    command = args[0]

    if command == "add":
        if len(args) < 2:
            print_usage()
        text = " ".join(args[1:])
        data = load()
        data["max_id"] += 1
        data["tasks"].append({"id": data["max_id"], "text": text, "done": False})
        save(data)
        print(f"Added {data['max_id']}: {text}")

    elif command == "list":
        data = load()
        if not data["tasks"]:
            print("No tasks")
        else:
            for task in sorted(data["tasks"], key=lambda t: t["id"]):
                status = "[x]" if task["done"] else "[ ]"
                print(f"{status} {task['id']}: {task['text']}")

    elif command == "done":
        if len(args) < 2:
            print_usage()
        try:
            task_id = int(args[1])
        except ValueError:
            print_usage()
        data = load()
        found = False
        for task in data["tasks"]:
            if task["id"] == task_id:
                task["done"] = True
                found = True
                break
        if not found:
            sys.stderr.write(f"Error: no task {task_id}\n")
            sys.exit(1)
        save(data)
        print(f"Done {task_id}")

    elif command == "remove":
        if len(args) < 2:
            print_usage()
        try:
            task_id = int(args[1])
        except ValueError:
            print_usage()
        data = load()
        found = False
        for i, task in enumerate(data["tasks"]):
            if task["id"] == task_id:
                del data["tasks"][i]
                found = True
                break
        if not found:
            sys.stderr.write(f"Error: no task {task_id}\n")
            sys.exit(1)
        save(data)
        print(f"Removed {task_id}")

    elif command == "clear":
        data = load()
        done_count = sum(1 for t in data["tasks"] if t["done"])
        data["tasks"] = [t for t in data["tasks"] if not t["done"]]
        save(data)
        print(f"Cleared {done_count}")

    else:
        print_usage()


if __name__ == "__main__":
    main()