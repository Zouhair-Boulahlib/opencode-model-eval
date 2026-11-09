# opencode/beam-free: behaviour and prompting report

Generated 2026-11-09 20:33 from 19 runs. Best variant: `v1_spec` with mean score 100% (baseline `v0_brief`: 76%).

## 1. Scores

### Iteration 1

| task | v0_brief | v1_spec | v2_spec_verify |
|---|---|---|---|
| t1_slugify | 21/22 | 22/22 | 22/22 |
| t2_bugfix | 16/16 | 16/16 | 16/16 |
| t3_todo_cli | 0/16 | 16/16 | 16/16 |
| t4_scheduler | 20/22 | 22/22 | 22/22 |
| t5_refactor | 11/12 | 12/12 | 12/12 |
| t6_repo_bugfix | - | - | - |
| **mean** | 76% | 100% | 100% |

Legend: `passed/total`; `T` = timed out; `P!` = edited a protected test file (scored 0).

### Iteration 2

| task | v6_brief_verify |
|---|---|
| t1_slugify | 0/22 T |
| t2_bugfix | - |
| t3_todo_cli | - |
| t4_scheduler | 22/22 |
| t5_refactor | - |
| t6_repo_bugfix | - |
| **mean** | 50% |

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
| mean score (all runs) | 88% |
| perfect runs / zero runs | 14 / 2 |
| avg wall time | 98 s |
| avg tokens in / out / reasoning | 36385 / 1328 / 2032 |
| avg LLM steps per run | 9.2 |
| avg tool calls per run (errors) | 9.3 (0.32) |
| tool usage (total) | bash: 98, edit: 34, read: 21, write: 18, glob: 6 |
| tool errors by tool (total) | bash: 6 |
| bash calls blocked by permission (unquoted absolute path with a space) | 1 |
| ran pytest / wrote own tests | 63% / 32% |
| timeouts | 5% |
| edited protected test files | 0 |
| question-tool attempts / final message is a question | 0 / 0% |
| target file missing at end | 1 |
| avg final message length | 35 chars |
| runs with provider/tool errors | 0 |

### Behaviour by prompt variant

| variant | runs | mean score | wall s | tools/run | ran pytest | own tests | timeouts | final chars |
|---|---|---|---|---|---|---|---|---|
| v0_brief | 5 | 76% | 65 | 8.0 | 40% | 0% | 0% | 20 |
| v1_spec | 5 | 100% | 52 | 7.8 | 40% | 0% | 0% | 22 |
| v2_spec_verify | 5 | 100% | 78 | 10.6 | 100% | 100% | 0% | 18 |
| v6_brief_verify | 2 | 50% | 402 | 11.5 | 50% | 50% | 50% | 9 |
| g0_spec_env | 1 | 100% | 41 | 9.0 | 100% | 0% | 0% | 166 |
| g1_spec_env_graph | 1 | 100% | 48 | 13.0 | 100% | 0% | 0% | 187 |

## 3. Failure analysis

### t1_slugify

- iter1 `v0_brief`: **FAIL** 21/22 in 19.1s, 4 tool calls, never ran tests. failed: test_basic[Stra\xdfe \u65e5\u672c-stra-e] ([run folder](runs/iter1/t1_slugify/v0_brief))
- iter1 `v1_spec`: **PASS** 22/22 in 31.1s, 4 tool calls, never ran tests.  ([run folder](runs/iter1/t1_slugify/v1_spec))
- iter1 `v2_spec_verify`: **PASS** 22/22 in 48.1s, 10 tool calls, ran pytest.  ([run folder](runs/iter1/t1_slugify/v2_spec_verify))
- iter2 `v6_brief_verify`: **TIMEOUT** 0/22 in 420.9s, 6 tool calls, never ran tests. target file never created ([run folder](runs/iter2/t1_slugify/v6_brief_verify))

### t2_bugfix

- iter1 `v0_brief`: **PASS** 16/16 in 32.1s, 11 tool calls, ran pytest.  ([run folder](runs/iter1/t2_bugfix/v0_brief))
- iter1 `v1_spec`: **PASS** 16/16 in 46.1s, 9 tool calls, ran pytest.  ([run folder](runs/iter1/t2_bugfix/v1_spec))
- iter1 `v2_spec_verify`: **PASS** 16/16 in 35.1s, 9 tool calls, ran pytest.  ([run folder](runs/iter1/t2_bugfix/v2_spec_verify))

### t3_todo_cli

- iter1 `v0_brief`: **FAIL** 0/16 in 182.2s, 11 tool calls, never ran tests. failed: test_list_empty, test_add_prints_exact_line, test_add_and_list, test_done_marks_task, test_done_twice_ok, test_remove, test_ids_never_reused_after_remove, test_ids_never_reused_after_clear ... ([run folder](runs/iter1/t3_todo_cli/v0_brief))
- iter1 `v1_spec`: **PASS** 16/16 in 91.2s, 13 tool calls, never ran tests.  ([run folder](runs/iter1/t3_todo_cli/v1_spec))
- iter1 `v2_spec_verify`: **PASS** 16/16 in 200.4s, 17 tool calls, ran pytest.  ([run folder](runs/iter1/t3_todo_cli/v2_spec_verify))

### t4_scheduler

- iter1 `v0_brief`: **FAIL** 20/22 in 30.1s, 3 tool calls, never ran tests. failed: test_merge_invalid_raises, test_free_empty_busy ([run folder](runs/iter1/t4_scheduler/v0_brief))
- iter1 `v1_spec`: **PASS** 22/22 in 12.0s, 2 tool calls, never ran tests.  ([run folder](runs/iter1/t4_scheduler/v1_spec))
- iter1 `v2_spec_verify`: **PASS** 22/22 in 41.1s, 8 tool calls, ran pytest.  ([run folder](runs/iter1/t4_scheduler/v2_spec_verify))
- iter2 `v6_brief_verify`: **PASS** 22/22 in 382.4s, 17 tool calls, ran pytest.  ([run folder](runs/iter2/t4_scheduler/v6_brief_verify))

### t5_refactor

- iter1 `v0_brief`: **FAIL** 11/12 in 63.1s, 11 tool calls, ran pytest. failed: test_no_function_longer_than_20_lines ([run folder](runs/iter1/t5_refactor/v0_brief))
- iter1 `v1_spec`: **PASS** 12/12 in 79.2s, 11 tool calls, ran pytest.  ([run folder](runs/iter1/t5_refactor/v1_spec))
- iter1 `v2_spec_verify`: **PASS** 12/12 in 63.1s, 9 tool calls, ran pytest.  ([run folder](runs/iter1/t5_refactor/v2_spec_verify))

### t6_repo_bugfix

- iter3 `g0_spec_env`: **PASS** 14/14 in 41.1s, 9 tool calls, ran pytest.  ([run folder](runs/iter3/t6_repo_bugfix/g0_spec_env))
- iter3 `g1_spec_env_graph`: **PASS** 14/14 in 48.1s, 13 tool calls, ran pytest.  ([run folder](runs/iter3/t6_repo_bugfix/g1_spec_env_graph))

## 4. Behaviour notes (hand-written)

_Iteration 1 complete (15 runs). Iteration 2/3 pending._

**Style.** Looks around first (`glob`/`ls`), writes the whole file in one `write`, smoke-tests with inline `python -c`, edits surgically (5 small `edit` calls on the bug-fix task). Final messages are two words ("Done.", "Created `todo.py`.") even when the prompt asks for a summary: 20 characters on average across all variants.

**Scores.** Brief 76% -> full spec 100% on every task (todo CLI 0 -> 16/16, scheduler 20 -> 22, refactor 11 -> 12). Spec + verify also 100% but costs more: steps 7.8 -> 10.6 per run, wall 52 s -> 78 s, todo CLI 91 s -> 200 s.

**Quirks observed.**
- From the brief todo prompt it searched the whole filesystem (`grep -rl "todo.py" /`, `find / -name "*todo*test*"`) for hidden tests; the tool killed the command. It then spent 3 minutes byte-debugging its own file with `xxd` after a heredoc glitch.
- Chose `1. [ ] Buy milk` / `Marked task 1 as done.` as output format from the brief; any exact-contract task needs the strings spelled out.
- Scheduler brief: missed only the ValueError rule and the empty-busy case, both absent from the brief.

**Recommendation.** Give it the contract and nothing else. Do not add a verify loop for single-file tasks; it complies (100% ran pytest, wrote test files) but gains nothing. If you need a readable summary at the end, you must ask for a specific format; "short summary" yields two words.

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

**best run** (t4_scheduler / iter1 / `v1_spec`, 22/22):

> Done.

**worst run** (t3_todo_cli / iter1 / `v0_brief`, 0/16):

> todo.py created and verified.

