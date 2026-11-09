# opencode/mimo-v2.6-flash-free: behaviour and prompting report

Generated 2026-11-09 20:33 from 15 runs. Best variant: `v1_spec` with mean score 100% (baseline `v0_brief`: 77%).

## 1. Scores

### Iteration 1

| task | v0_brief | v1_spec | v2_spec_verify |
|---|---|---|---|
| t1_slugify | 21/22 | 22/22 | - |
| t2_bugfix | 16/16 | - | 16/16 |
| t3_todo_cli | 0/16 | 16/16 | - |
| t4_scheduler | 21/22 | 22/22 | - |
| t5_refactor | 11/12 | 12/12 | 12/12 |
| t6_repo_bugfix | - | - | - |
| **mean** | 77% | 100% | 100% |

Legend: `passed/total`; `T` = timed out; `P!` = edited a protected test file (scored 0).

### Iteration 2

| task | v6_brief_verify |
|---|---|
| t1_slugify | 22/22 |
| t2_bugfix | - |
| t3_todo_cli | - |
| t4_scheduler | 21/22 |
| t5_refactor | - |
| t6_repo_bugfix | - |
| **mean** | 98% |

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
| runs | 15 |
| mean score (all runs) | 92% |
| perfect runs / zero runs | 10 / 1 |
| avg wall time | 119 s |
| avg tokens in / out / reasoning | 12361 / 1883 / 1773 |
| avg LLM steps per run | 5.8 |
| avg tool calls per run (errors) | 6.8 (0.07) |
| tool usage (total) | bash: 40, read: 19, edit: 19, write: 15, glob: 8, grep: 1 |
| tool errors by tool (total) | bash: 1 |
| bash calls blocked by permission (unquoted absolute path with a space) | 1 |
| ran pytest / wrote own tests | 60% / 27% |
| timeouts | 0% |
| edited protected test files | 0 |
| question-tool attempts / final message is a question | 0 / 0% |
| target file missing at end | 0 |
| avg final message length | 419 chars |
| runs with provider/tool errors | 0 |

### Behaviour by prompt variant

| variant | runs | mean score | wall s | tools/run | ran pytest | own tests | timeouts | final chars |
|---|---|---|---|---|---|---|---|---|
| v0_brief | 5 | 77% | 75 | 5.6 | 40% | 0% | 0% | 323 |
| v1_spec | 4 | 100% | 125 | 5.5 | 25% | 0% | 0% | 577 |
| v2_spec_verify | 2 | 100% | 173 | 9.0 | 100% | 100% | 0% | 365 |
| v6_brief_verify | 2 | 98% | 232 | 7.5 | 100% | 100% | 0% | 368 |
| g0_spec_env | 1 | 100% | 49 | 11.0 | 100% | 0% | 0% | 452 |
| g1_spec_env_graph | 1 | 100% | 56 | 8.0 | 100% | 0% | 0% | 445 |

## 3. Failure analysis

### t1_slugify

- iter1 `v0_brief`: **FAIL** 21/22 in 33.2s, 4 tool calls, never ran tests. failed: test_basic[Stra\xdfe \u65e5\u672c-stra-e] ([run folder](runs/iter1/t1_slugify/v0_brief))
- iter1 `v1_spec`: **PASS** 22/22 in 67.5s, 3 tool calls, never ran tests.  ([run folder](runs/iter1/t1_slugify/v1_spec))
- iter2 `v6_brief_verify`: **PASS** 22/22 in 171.2s, 10 tool calls, ran pytest.  ([run folder](runs/iter2/t1_slugify/v6_brief_verify))

### t2_bugfix

- iter1 `v0_brief`: **PASS** 16/16 in 56.1s, 9 tool calls, ran pytest.  ([run folder](runs/iter1/t2_bugfix/v0_brief))
- iter1 `v2_spec_verify`: **PASS** 16/16 in 73.1s, 10 tool calls, ran pytest.  ([run folder](runs/iter1/t2_bugfix/v2_spec_verify))

### t3_todo_cli

- iter1 `v0_brief`: **FAIL** 0/16 in 88.1s, 3 tool calls, never ran tests. failed: test_list_empty, test_add_prints_exact_line, test_add_and_list, test_done_marks_task, test_done_twice_ok, test_remove, test_ids_never_reused_after_remove, test_ids_never_reused_after_clear ... ([run folder](runs/iter1/t3_todo_cli/v0_brief))
- iter1 `v1_spec`: **PASS** 16/16 in 78.2s, 4 tool calls, never ran tests.  ([run folder](runs/iter1/t3_todo_cli/v1_spec))

### t4_scheduler

- iter1 `v0_brief`: **FAIL** 21/22 in 42.1s, 2 tool calls, never ran tests. failed: test_merge_invalid_raises ([run folder](runs/iter1/t4_scheduler/v0_brief))
- iter1 `v1_spec`: **PASS** 22/22 in 142.8s, 8 tool calls, never ran tests.  ([run folder](runs/iter1/t4_scheduler/v1_spec))
- iter2 `v6_brief_verify`: **FAIL** 21/22 in 292.3s, 5 tool calls, ran pytest. failed: test_merge_invalid_raises ([run folder](runs/iter2/t4_scheduler/v6_brief_verify))

### t5_refactor

- iter1 `v0_brief`: **FAIL** 11/12 in 153.9s, 10 tool calls, ran pytest. failed: test_no_function_longer_than_20_lines ([run folder](runs/iter1/t5_refactor/v0_brief))
- iter1 `v1_spec`: **PASS** 12/12 in 209.7s, 7 tool calls, ran pytest.  ([run folder](runs/iter1/t5_refactor/v1_spec))
- iter1 `v2_spec_verify`: **PASS** 12/12 in 272.0s, 8 tool calls, ran pytest.  ([run folder](runs/iter1/t5_refactor/v2_spec_verify))

### t6_repo_bugfix

- iter3 `g0_spec_env`: **PASS** 14/14 in 49.1s, 11 tool calls, ran pytest.  ([run folder](runs/iter3/t6_repo_bugfix/g0_spec_env))
- iter3 `g1_spec_env_graph`: **PASS** 14/14 in 56.1s, 8 tool calls, ran pytest.  ([run folder](runs/iter3/t6_repo_bugfix/g1_spec_env_graph))

## 4. Behaviour notes (hand-written)

_Iteration 1 complete (11 runs, adaptive skips). Iteration 2/3 pending._

**Style.** Fewest steps in the set (3 to 6) but the longest thinking per step: 75 s average on the brief, 125 s with the spec, 210 to 270 s on the refactor. A "get it right in one shot" model.

**Scores.** Brief 77% -> spec 100% on everything it ran (todo 16/16, slugify 22/22, scheduler 22/22, refactor 12/12). Spec + verify 100% at higher cost (refactor 272 s).

**Quirks observed.**
- Brief todo: `Added task 1: buy milk`, `[ ] 1. buy milk`; working but off-contract.
- No tool errors, no exploration outside the directory, never asked questions.

**Recommendation.** Spec only, and accept the latency. Do not force iteration (plan, verify): it already deliberates internally, and the extra loop only adds wall time.

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

**best run** (t6_repo_bugfix / iter3 / `g0_spec_env`, 14/14):

> Root cause: `ledger/importers/csv_importer.py:18` hardcoded a ×100 minor-unit shift (`int(amount * 100)`), which is only correct for 2-decimal currencies — JPY amounts became 100× too large.
> 
> Fix: replaced it with the existing `to_minor_units(amount, currency)` helper (same one the JSON importer uses), so scaling follows the ISO 4217 exponent per currency.
> 
> `python -m pytest tests -q` → **3 passed**
> 
> Changed file: `ledger/importers/csv_importer.py`

**worst run** (t3_todo_cli / iter1 / `v0_brief`, 0/16):

> `todo.py` created and verified:
> 
> - **add** `text` — append a task
> - **list** — show numbered tasks with `[x]` for done
> - **done** `#|text` — mark complete (accepts number or exact text)
> - **remove** `#|text` — delete a task
> - **clear** (`--all` optional) — clear completed, or everything
> 
> Data persists in `todos.json` (atomic writes). All commands tested above.

