# opencode/big-pickle: behaviour and prompting report

Generated 2026-11-09 20:33 from 19 runs. Best variant: `v1_spec` with mean score 100% (baseline `v0_brief`: 77%).

## 1. Scores

### Iteration 1

| task | v0_brief | v1_spec | v2_spec_verify |
|---|---|---|---|
| t1_slugify | 21/22 | 22/22 | 22/22 |
| t2_bugfix | 16/16 | 16/16 | 16/16 |
| t3_todo_cli | 0/16 | 16/16 | 16/16 |
| t4_scheduler | 21/22 | 22/22 | 22/22 |
| t5_refactor | 11/12 | 12/12 | 12/12 |
| t6_repo_bugfix | - | - | - |
| **mean** | 77% | 100% | 100% |

Legend: `passed/total`; `T` = timed out; `P!` = edited a protected test file (scored 0).

### Iteration 2

| task | v6_brief_verify |
|---|---|
| t1_slugify | 21/22 |
| t2_bugfix | - |
| t3_todo_cli | - |
| t4_scheduler | 21/22 |
| t5_refactor | - |
| t6_repo_bugfix | - |
| **mean** | 95% |

Legend: `passed/total`; `T` = timed out; `P!` = edited a protected test file (scored 0).

### Iteration 3

| task | g0_spec_env | g1_spec_env_graph |
|---|---|---|
| t1_slugify | - | - |
| t2_bugfix | - | - |
| t3_todo_cli | - | - |
| t4_scheduler | - | - |
| t5_refactor | - | - |
| t6_repo_bugfix | 14/14 | 14/14 |
| **mean** | 100% | 100% |

Legend: `passed/total`; `T` = timed out; `P!` = edited a protected test file (scored 0).

## 2. Behaviour profile

| metric | value |
|---|---|
| runs | 19 |
| mean score (all runs) | 93% |
| perfect runs / zero runs | 13 / 1 |
| avg wall time | 37 s |
| avg tokens in / out / reasoning | 13984 / 1323 / 544 |
| avg LLM steps per run | 5.3 |
| avg tool calls per run (errors) | 5.8 (0.00) |
| tool usage (total) | bash: 45, edit: 22, write: 21, read: 20, glob: 2 |
| tool errors by tool (total) | - |
| bash calls blocked by permission (unquoted absolute path with a space) | 0 |
| ran pytest / wrote own tests | 68% / 37% |
| timeouts | 0% |
| edited protected test files | 0 |
| question-tool attempts / final message is a question | 0 / 0% |
| target file missing at end | 0 |
| avg final message length | 168 chars |
| runs with provider/tool errors | 0 |

### Behaviour by prompt variant

| variant | runs | mean score | wall s | tools/run | ran pytest | own tests | timeouts | final chars |
|---|---|---|---|---|---|---|---|---|
| v0_brief | 5 | 77% | 29 | 5.0 | 40% | 0% | 0% | 174 |
| v1_spec | 5 | 100% | 23 | 3.8 | 40% | 0% | 0% | 123 |
| v2_spec_verify | 5 | 100% | 42 | 7.2 | 100% | 100% | 0% | 191 |
| v6_brief_verify | 2 | 95% | 77 | 8.5 | 100% | 100% | 0% | 78 |
| g0_spec_env | 1 | 100% | 31 | 7.0 | 100% | 0% | 0% | 285 |
| g1_spec_env_graph | 1 | 100% | 39 | 6.0 | 100% | 0% | 0% | 304 |

## 3. Failure analysis

### t1_slugify

- iter1 `v0_brief`: **FAIL** 21/22 in 23.1s, 3 tool calls, never ran tests. failed: test_basic[Stra\xdfe \u65e5\u672c-stra-e] ([run folder](runs/iter1/t1_slugify/v0_brief))
- iter1 `v1_spec`: **PASS** 22/22 in 17.1s, 2 tool calls, never ran tests.  ([run folder](runs/iter1/t1_slugify/v1_spec))
- iter1 `v2_spec_verify`: **PASS** 22/22 in 35.1s, 9 tool calls, ran pytest.  ([run folder](runs/iter1/t1_slugify/v2_spec_verify))
- iter2 `v6_brief_verify`: **FAIL** 21/22 in 66.1s, 9 tool calls, ran pytest. failed: test_basic[Stra\xdfe \u65e5\u672c-stra-e] ([run folder](runs/iter2/t1_slugify/v6_brief_verify))

### t2_bugfix

- iter1 `v0_brief`: **PASS** 16/16 in 39.1s, 10 tool calls, ran pytest.  ([run folder](runs/iter1/t2_bugfix/v0_brief))
- iter1 `v1_spec`: **PASS** 16/16 in 24.1s, 7 tool calls, ran pytest.  ([run folder](runs/iter1/t2_bugfix/v1_spec))
- iter1 `v2_spec_verify`: **PASS** 16/16 in 54.1s, 10 tool calls, ran pytest.  ([run folder](runs/iter1/t2_bugfix/v2_spec_verify))

### t3_todo_cli

- iter1 `v0_brief`: **FAIL** 0/16 in 39.1s, 4 tool calls, never ran tests. failed: test_list_empty, test_add_prints_exact_line, test_add_and_list, test_done_marks_task, test_done_twice_ok, test_remove, test_ids_never_reused_after_remove, test_ids_never_reused_after_clear ... ([run folder](runs/iter1/t3_todo_cli/v0_brief))
- iter1 `v1_spec`: **PASS** 16/16 in 28.1s, 3 tool calls, never ran tests.  ([run folder](runs/iter1/t3_todo_cli/v1_spec))
- iter1 `v2_spec_verify`: **PASS** 16/16 in 32.1s, 4 tool calls, ran pytest.  ([run folder](runs/iter1/t3_todo_cli/v2_spec_verify))

### t4_scheduler

- iter1 `v0_brief`: **FAIL** 21/22 in 24.1s, 3 tool calls, never ran tests. failed: test_merge_invalid_raises ([run folder](runs/iter1/t4_scheduler/v0_brief))
- iter1 `v1_spec`: **PASS** 22/22 in 21.0s, 2 tool calls, never ran tests.  ([run folder](runs/iter1/t4_scheduler/v1_spec))
- iter1 `v2_spec_verify`: **PASS** 22/22 in 25.1s, 4 tool calls, ran pytest.  ([run folder](runs/iter1/t4_scheduler/v2_spec_verify))
- iter2 `v6_brief_verify`: **FAIL** 21/22 in 88.1s, 8 tool calls, ran pytest. failed: test_merge_invalid_raises ([run folder](runs/iter2/t4_scheduler/v6_brief_verify))

### t5_refactor

- iter1 `v0_brief`: **FAIL** 11/12 in 19.0s, 5 tool calls, ran pytest. failed: test_no_function_longer_than_20_lines ([run folder](runs/iter1/t5_refactor/v0_brief))
- iter1 `v1_spec`: **PASS** 12/12 in 27.1s, 5 tool calls, ran pytest.  ([run folder](runs/iter1/t5_refactor/v1_spec))
- iter1 `v2_spec_verify`: **PASS** 12/12 in 61.1s, 9 tool calls, ran pytest.  ([run folder](runs/iter1/t5_refactor/v2_spec_verify))

### t6_repo_bugfix

- iter3 `g0_spec_env`: **PASS** 14/14 in 31.0s, 7 tool calls, ran pytest.  ([run folder](runs/iter3/t6_repo_bugfix/g0_spec_env))
- iter3 `g1_spec_env_graph`: **PASS** 14/14 in 39.1s, 6 tool calls, ran pytest.  ([run folder](runs/iter3/t6_repo_bugfix/g1_spec_env_graph))

## 4. Behaviour notes (hand-written)

_Iteration 1 complete (15 runs). Iteration 2/3 pending._

**Style.** The most economical model in the set: 3 to 7 steps per task, one `write` then one or two bash checks, 23 s average with the full spec. Summaries are one dense paragraph with file:line references and an explicit list of what changed.

**Scores.** Brief 77% -> spec 100% on all five tasks. The spec runs were *faster* than the brief runs (23 s vs 29 s) because it stops guessing. Spec + verify: still 100%, wall 42 s, steps 6.4 (vs 4.2).

**Quirks observed.**
- Brief todo: `Added task 1: buy milk` and a padded table layout, storage in `tasks.json`. Works, wrong contract.
- Brief refactor: produced a 24-line function (limit 20), everything else right.

**Recommendation.** Spec only. This is the model to use when latency and quota matter: it reached the ceiling on every task at the lowest cost in the group. Skip plan-first and verify instructions; they only add steps.

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

> Created `slugify.py` with the function. Verified against accents, non-ASCII separators, whitespace/punctuation, and `max_length` edge cases.

**worst run** (t3_todo_cli / iter1 / `v0_brief`, 0/16):

> Created `todo.py` with `add`, `list`, `done`, `remove`, and `clear`, persisting to `tasks.json` (configurable via `-f` or `TODO_FILE`). Tasks have IDs, done status, and creation timestamps. Verified all commands end-to-end.

