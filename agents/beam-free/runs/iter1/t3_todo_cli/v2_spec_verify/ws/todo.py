import json
import os
import sys


def storage_path():
    return os.environ.get("TODO_FILE", "todo.json")


def _normalize_task(raw):
    if not isinstance(raw, dict):
        return None
    tid = raw.get("id", raw.get("ID"))
    try:
        tid = int(tid)
    except (TypeError, ValueError):
        return None
    text = raw.get("text", raw.get("title", raw.get("task", raw.get("description", ""))))
    done = raw.get("done", raw.get("completed", raw.get("is_done", False)))
    status = raw.get("status")
    if isinstance(done, str):
        done = done.strip().lower() in ("true", "1", "yes", "done", "completed", "x")
    elif not isinstance(done, bool):
        done = bool(done)
    if status is not None and "done" not in raw and "completed" not in raw and "is_done" not in raw:
        done = str(status).strip().lower() == "done"
    return {"id": tid, "text": str(text), "done": bool(done)}


def _load_list(data):
    tasks = []
    for raw in data:
        task = _normalize_task(raw)
        if task is not None:
            tasks.append(task)
    ids = [task["id"] for task in tasks]
    next_id = (max(ids) + 1) if ids else 1
    return next_id, tasks


def _load_dict(data):
    tasks_raw = None
    for key in ("tasks", "items", "todo", "todos"):
        if isinstance(data.get(key), list):
            tasks_raw = data.get(key)
            break
    if tasks_raw is None and all(isinstance(value, dict) for value in data.values()) and data:
        tasks_raw = []
        for key, value in data.items():
            item = dict(value)
            if "id" not in item:
                try:
                    item["id"] = int(key)
                except (TypeError, ValueError):
                    pass
            tasks_raw.append(item)
    if tasks_raw is None:
        tasks_raw = []
    next_id = None
    for key in ("next_id", "nextId", "next", "counter", "id_counter", "last_id"):
        if key in data:
            value = data.get(key)
            try:
                next_id = int(value)
                if key == "last_id":
                    next_id += 1
                break
            except (TypeError, ValueError):
                pass
    tasks = []
    for raw in tasks_raw:
        task = _normalize_task(raw)
        if task is not None:
            tasks.append(task)
    ids = [task["id"] for task in tasks]
    if next_id is None:
        next_id = (max(ids) + 1) if ids else 1
    if ids:
        next_id = max(next_id, max(ids) + 1)
    return next_id, tasks


def load():
    path = storage_path()
    if not os.path.exists(path):
        return {"next_id": 1, "tasks": []}
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    if isinstance(data, list):
        next_id, tasks = _load_list(data)
    elif isinstance(data, dict):
        next_id, tasks = _load_dict(data)
    else:
        next_id, tasks = 1, []
    if not isinstance(tasks, list):
        tasks = []
    ids = [task["id"] for task in tasks if isinstance(task, dict) and "id" in task]
    if ids:
        next_id = max(next_id, max(ids) + 1)
    return {"next_id": next_id, "tasks": tasks}


def save(data):
    path = storage_path()
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False)
        handle.write("\n")


def usage():
    print("Usage: todo.py <add|list|done|remove|clear> ...", file=sys.stderr)
    sys.exit(2)


def parse_id(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        usage()


def find_task(data, task_id):
    for task in data["tasks"]:
        if task["id"] == task_id:
            return task
    return None


def cmd_add(args):
    if len(args) < 1:
        usage()
    text = " ".join(args)
    data = load()
    task_id = data["next_id"]
    data["tasks"].append({"id": task_id, "text": text, "done": False})
    data["next_id"] = task_id + 1
    save(data)
    print(f"Added {task_id}: {text}")


def cmd_list(args):
    if args:
        usage()
    data = load()
    tasks = sorted(data["tasks"], key=lambda task: task["id"])
    if not tasks:
        print("No tasks")
        return
    for task in tasks:
        mark = "x" if task["done"] else " "
        print(f"[{mark}] {task['id']}: {task['text']}")


def cmd_done(args):
    if len(args) != 1:
        usage()
    task_id = parse_id(args[0])
    data = load()
    task = find_task(data, task_id)
    if task is None:
        print(f"Error: no task {task_id}", file=sys.stderr)
        sys.exit(1)
    was_done = task["done"]
    task["done"] = True
    if not was_done:
        save(data)
    print(f"Done {task_id}")


def cmd_remove(args):
    if len(args) != 1:
        usage()
    task_id = parse_id(args[0])
    data = load()
    task = find_task(data, task_id)
    if task is None:
        print(f"Error: no task {task_id}", file=sys.stderr)
        sys.exit(1)
    data["tasks"] = [item for item in data["tasks"] if item["id"] != task_id]
    save(data)
    print(f"Removed {task_id}")


def cmd_clear(args):
    if args:
        usage()
    data = load()
    done_tasks = [task for task in data["tasks"] if task["done"]]
    data["tasks"] = [task for task in data["tasks"] if not task["done"]]
    if done_tasks:
        save(data)
    print(f"Cleared {len(done_tasks)}")


def main():
    args = sys.argv[1:]
    if not args:
        usage()
    command = args[0]
    rest = args[1:]
    if command == "add":
        cmd_add(rest)
    elif command == "list":
        cmd_list(rest)
    elif command == "done":
        cmd_done(rest)
    elif command == "remove":
        cmd_remove(rest)
    elif command == "clear":
        cmd_clear(rest)
    else:
        usage()


if __name__ == "__main__":
    main()