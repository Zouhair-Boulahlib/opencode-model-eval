Example session (each line is a separate process invocation):
    $ python todo.py list
    No tasks
    $ python todo.py add buy milk
    Added 1: buy milk
    $ python todo.py add call mom
    Added 2: call mom
    $ python todo.py done 1
    Done 1
    $ python todo.py list
    [x] 1: buy milk
    [ ] 2: call mom
    $ python todo.py remove 2
    Removed 2
    $ python todo.py add walk dog
    Added 3: walk dog
    $ python todo.py done 42        (stderr: "Error: no task 42", exit 1)
    $ python todo.py clear
    Cleared 1
