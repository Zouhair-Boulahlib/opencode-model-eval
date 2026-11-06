# Working rules for coding agents in this repository

These rules are loaded into every OpenCode session here. They come from a measured study of ten
coding models (https://github.com/Zouhair-Boulahlib/opencode-model-eval): the points below are the
behaviours that lost points or wasted minutes in that study, written as instructions.

## Orientation: use the map before exploring

- `graphify-out/GRAPH_REPORT.md` is an architecture map of this codebase: god nodes (most connected
  symbols), communities (groups of related modules) and surprising cross-module connections. Read it
  first. Go straight to the modules it points at instead of listing or grepping the whole tree.
- For a specific question, run `python scripts/task_context.py --query "<question>"`; it prints the
  subgraph around the matching symbols with file paths. Rebuild the map with `python scripts/graph_refresh.py`
  after structural changes.
- Never search outside the project directory. Never run `find /`, `grep -r /` or list parent folders.

## Environment

- You are already inside the project directory. Use relative paths only; never `cd` to an absolute
  path. Paths may contain spaces: always quote them in shell commands.
- The shell is Git Bash on Windows; Python is `python`. The write tool takes `filePath` and `content`;
  the read tool takes `filePath`. If a tool call is rejected for invalid arguments, fix the argument
  names, do not retry the same call.

## Contract discipline

- A task is defined by its contract file under `.opencode/tasks/`. Match it exactly: file names,
  function signatures, parameter names, return types (tuples are not lists), output strings, exit codes.
  If a program or a test will parse the output, reproduce the literal string.
- Create or modify only the files the contract names. No extra modules, packages or folders unless
  the contract allows them.
- Do not modify tests that already exist. Run the tests the project provides (`python -m pytest -q`
  unless the contract says otherwise) before you finish, and report the summary line.
- Do not write your own test files unless the contract asks for them; provided tests beat
  self-written ones.
- Do not ask questions. Make the most reasonable assumption, state it at the end, and proceed.

## Finishing

End with a short summary: files created or changed, how you verified them (the exact command and its
result), and any assumption you made. Keep it under ten lines.
