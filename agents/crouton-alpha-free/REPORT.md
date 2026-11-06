# opencode/crouton-alpha-free: behaviour and prompting report

Generated 2026-11-06 16:11 from 15 runs. Best variant: `v1_spec` with mean score 100% (baseline `v0_brief`: 66%).

## 1. Scores

### Iteration 1

| task | v0_brief | v1_spec | v2_spec_verify |
|---|---|---|---|
| t1_slugify | 21/22 | 22/22 | 22/22 |
| t2_bugfix | 16/16 | 16/16 | 16/16 |
| t3_todo_cli | 0/16 | 16/16 | 16/16 |
| t4_scheduler | 9/22 | 22/22 | 22/22 |
| t5_refactor | 11/12 | 12/12 | 12/12 |
| **mean** | 66% | 100% | 100% |

Legend: `passed/total`; `T` = timed out; `P!` = edited a protected test file (scored 0).

## 2. Behaviour profile

| metric | value |
|---|---|
| runs | 15 |
| mean score (all runs) | 89% |
| perfect runs / zero runs | 11 / 1 |
| avg wall time | 28 s |
| avg tokens in / out / reasoning | 39008 / 1140 / 0 |
| avg LLM steps per run | 6.3 |
| avg tool calls per run (errors) | 5.7 (0.07) |
| tool usage (total) | bash: 25, read: 23, write: 17, edit: 16, todowrite: 4, glob: 1 |
| tool errors by tool (total) | bash: 1 |
| bash calls blocked by permission (unquoted absolute path with a space) | 1 |
| ran pytest / wrote own tests | 60% / 33% |
| timeouts | 0% |
| edited protected test files | 0 |
| question-tool attempts / final message is a question | 0 / 0% |
| target file missing at end | 0 |
| avg final message length | 83 chars |
| runs with provider/tool errors | 0 |

### Behaviour by prompt variant

| variant | runs | mean score | wall s | tools/run | ran pytest | own tests | timeouts | final chars |
|---|---|---|---|---|---|---|---|---|
| v0_brief | 5 | 66% | 26 | 5.6 | 40% | 0% | 0% | 104 |
| v1_spec | 5 | 100% | 27 | 5.0 | 40% | 0% | 0% | 72 |
| v2_spec_verify | 5 | 100% | 30 | 6.6 | 100% | 100% | 0% | 71 |

## 3. Failure analysis

### t1_slugify

- iter1 `v0_brief`: **FAIL** 21/22 in 29.1s, 4 tool calls, never ran tests. failed: test_basic[Stra\xdfe \u65e5\u672c-stra-e] ([run folder](runs/iter1/t1_slugify/v0_brief))
- iter1 `v1_spec`: **PASS** 22/22 in 15.0s, 3 tool calls, never ran tests.  ([run folder](runs/iter1/t1_slugify/v1_spec))
- iter1 `v2_spec_verify`: **PASS** 22/22 in 22.1s, 4 tool calls, ran pytest.  ([run folder](runs/iter1/t1_slugify/v2_spec_verify))

### t2_bugfix

- iter1 `v0_brief`: **PASS** 16/16 in 36.1s, 10 tool calls, ran pytest.  ([run folder](runs/iter1/t2_bugfix/v0_brief))
- iter1 `v1_spec`: **PASS** 16/16 in 20.0s, 9 tool calls, ran pytest.  ([run folder](runs/iter1/t2_bugfix/v1_spec))
- iter1 `v2_spec_verify`: **PASS** 16/16 in 26.1s, 9 tool calls, ran pytest.  ([run folder](runs/iter1/t2_bugfix/v2_spec_verify))

### t3_todo_cli

- iter1 `v0_brief`: **FAIL** 0/16 in 20.1s, 4 tool calls, never ran tests. failed: test_list_empty, test_add_prints_exact_line, test_add_and_list, test_done_marks_task, test_done_twice_ok, test_remove, test_ids_never_reused_after_remove, test_ids_never_reused_after_clear ... ([run folder](runs/iter1/t3_todo_cli/v0_brief))
- iter1 `v1_spec`: **PASS** 16/16 in 44.1s, 5 tool calls, never ran tests.  ([run folder](runs/iter1/t3_todo_cli/v1_spec))
- iter1 `v2_spec_verify`: **PASS** 16/16 in 42.1s, 10 tool calls, ran pytest.  ([run folder](runs/iter1/t3_todo_cli/v2_spec_verify))

### t4_scheduler

- iter1 `v0_brief`: **FAIL** 9/22 in 18.0s, 4 tool calls, never ran tests. failed: test_merge_basic, test_merge_touching, test_merge_contained, test_merge_single, test_merge_returns_tuples_sorted, test_merge_invalid_raises, test_free_basic, test_free_min_filter ... ([run folder](runs/iter1/t4_scheduler/v0_brief))
- iter1 `v1_spec`: **PASS** 22/22 in 21.1s, 3 tool calls, never ran tests.  ([run folder](runs/iter1/t4_scheduler/v1_spec))
- iter1 `v2_spec_verify`: **PASS** 22/22 in 26.1s, 4 tool calls, ran pytest.  ([run folder](runs/iter1/t4_scheduler/v2_spec_verify))

### t5_refactor

- iter1 `v0_brief`: **FAIL** 11/12 in 27.1s, 6 tool calls, ran pytest. failed: test_no_function_longer_than_20_lines ([run folder](runs/iter1/t5_refactor/v0_brief))
- iter1 `v1_spec`: **PASS** 12/12 in 34.1s, 5 tool calls, ran pytest.  ([run folder](runs/iter1/t5_refactor/v1_spec))
- iter1 `v2_spec_verify`: **PASS** 12/12 in 34.1s, 6 tool calls, ran pytest.  ([run folder](runs/iter1/t5_refactor/v2_spec_verify))

## 4. Behaviour notes (hand-written)

_Iteration 1 complete (15 runs). Iteration 2/3 pending._

**Style.** Reads first, writes once, checks once; 15 to 44 s per task with the spec. Short factual summaries (about 70 characters).

**Scores.** Brief 66% (lowest of the ceiling group) -> spec 100% on everything. The brief loss was almost entirely one representation choice: scheduler 9/22 because it returned lists `[480, 1020]` where the tests expected tuples. The spec says "tuple" and the problem vanished (22/22, 21 s).

**Quirks observed.**
- Sensitive to unstated representation details (types, file names: `tasks.json` instead of `todo.json`, `Added task 1:` instead of `Added 1:`).
- Spec + verify costs little here (30 s vs 27 s) but adds nothing.

**Recommendation.** State types and names exactly, in the prompt; this model follows them precisely when told and guesses differently from the tests when not. Examples of exact outputs are probably worth more than process instructions (tested in iteration 2 only if quota allows).

## 5. Recommended prompt recipe

Best-performing variant `v1_spec` = components `spec`. Rendered for `t3_todo_cli`:

```text
Create `todo.py` in the current directory: a command-line to-do manager using only the Python standard library.

Storage: a JSON file. Its path is the environment variable `TODO_FILE` if set, otherwise `todo.json` in the current working directory. Create the file on first write. A missing file means "no tasks".

Commands (`python todo.py <command> ...`):
- `add <word> [<word> ...]`  Appends a task whose text is the words joined by single spaces. Prints `Added <id>: <text>`.
- `list`  Prints one line per task in id order: `[ ] <id>: <text>` for open tasks, `[x] <id>: <text>` for done tasks. If there are no tasks prints exactly `No tasks`.
- `done <id>`  Marks the task done. Prints `Done <id>`. Marking an already-done task is fine (same output, exit 0).
- `remove <id>`  Deletes the task. Prints `Removed <id>`.
- `clear`  Deletes all done tasks. Prints `Cleared <n>` where n is how many were deleted.

Rules:
- IDs start at 1 and always increase; an id is never reused, even after `remove` or `clear`.
- `done`/`remove` with an id that does not exist: print `Error: no task <id>` to stderr, print nothing to stdout, exit code 1.
- Unknown command, missing command, missing/invalid arguments: print `Usage: todo.py <add|list|done|remove|clear> ...` to stderr, exit code 2.
- All successful commands exit with code 0 and print exactly one line (or one line per task for list), with no extra output.
- Do not create any other source files.
```

## 6. Sample final messages

**best run** (t1_slugify / iter1 / `v1_spec`, 22/22):

> Created `slugify.py` with the specified `slugify` function.

**worst run** (t3_todo_cli / iter1 / `v0_brief`, 0/16):

> Created `todo.py` with `add`, `list`, `done`, `remove`, and `clear` commands, persisting tasks to `tasks.json`.

