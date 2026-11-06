# opencode/pulse-alpha-free: behaviour and prompting report

Generated 2026-11-06 16:11 from 10 runs. Best variant: `v2_spec_verify` with mean score 100% (baseline `v0_brief`: 79%).

## 1. Scores

### Iteration 1

| task | v0_brief | v1_spec | v2_spec_verify |
|---|---|---|---|
| t1_slugify | 22/22 | - | 22/22 |
| t2_bugfix | 16/16 | - | 16/16 |
| t3_todo_cli | 0/16 | 16/16 | - |
| t4_scheduler | 21/22 | 22/22 | - |
| t5_refactor | 12/12 | - | 12/12 |
| **mean** | 79% | 100% | 100% |

Legend: `passed/total`; `T` = timed out; `P!` = edited a protected test file (scored 0).

## 2. Behaviour profile

| metric | value |
|---|---|
| runs | 10 |
| mean score (all runs) | 90% |
| perfect runs / zero runs | 8 / 1 |
| avg wall time | 53 s |
| avg tokens in / out / reasoning | 14631 / 1449 / 886 |
| avg LLM steps per run | 6.0 |
| avg tool calls per run (errors) | 5.1 (0.20) |
| tool usage (total) | bash: 23, write: 13, read: 12, edit: 2, glob: 1 |
| tool errors by tool (total) | write: 2 |
| bash calls blocked by permission (unquoted absolute path with a space) | 0 |
| ran pytest / wrote own tests | 50% / 30% |
| timeouts | 0% |
| edited protected test files | 0 |
| question-tool attempts / final message is a question | 0 / 0% |
| target file missing at end | 0 |
| avg final message length | 262 chars |
| runs with provider/tool errors | 0 |

### Behaviour by prompt variant

| variant | runs | mean score | wall s | tools/run | ran pytest | own tests | timeouts | final chars |
|---|---|---|---|---|---|---|---|---|
| v0_brief | 5 | 79% | 43 | 4.4 | 40% | 0% | 0% | 292 |
| v1_spec | 2 | 100% | 34 | 3.0 | 0% | 0% | 0% | 150 |
| v2_spec_verify | 3 | 100% | 82 | 7.7 | 100% | 100% | 0% | 289 |

## 3. Failure analysis

### t1_slugify

- iter1 `v0_brief`: **PASS** 22/22 in 24.0s, 3 tool calls, never ran tests.  ([run folder](runs/iter1/t1_slugify/v0_brief))
- iter1 `v2_spec_verify`: **PASS** 22/22 in 57.1s, 4 tool calls, ran pytest.  ([run folder](runs/iter1/t1_slugify/v2_spec_verify))

### t2_bugfix

- iter1 `v0_brief`: **PASS** 16/16 in 30.1s, 5 tool calls, ran pytest.  ([run folder](runs/iter1/t2_bugfix/v0_brief))
- iter1 `v2_spec_verify`: **PASS** 16/16 in 68.2s, 8 tool calls, ran pytest.  ([run folder](runs/iter1/t2_bugfix/v2_spec_verify))

### t3_todo_cli

- iter1 `v0_brief`: **FAIL** 0/16 in 38.1s, 4 tool calls, never ran tests. failed: test_list_empty, test_add_prints_exact_line, test_add_and_list, test_done_marks_task, test_done_twice_ok, test_remove, test_ids_never_reused_after_remove, test_ids_never_reused_after_clear ... ([run folder](runs/iter1/t3_todo_cli/v0_brief))
- iter1 `v1_spec`: **PASS** 16/16 in 45.1s, 4 tool calls, never ran tests.  ([run folder](runs/iter1/t3_todo_cli/v1_spec))

### t4_scheduler

- iter1 `v0_brief`: **FAIL** 21/22 in 54.1s, 4 tool calls, never ran tests. failed: test_merge_invalid_raises ([run folder](runs/iter1/t4_scheduler/v0_brief))
- iter1 `v1_spec`: **PASS** 22/22 in 23.1s, 2 tool calls, never ran tests.  ([run folder](runs/iter1/t4_scheduler/v1_spec))

### t5_refactor

- iter1 `v0_brief`: **PASS** 12/12 in 69.2s, 6 tool calls, ran pytest.  ([run folder](runs/iter1/t5_refactor/v0_brief))
- iter1 `v2_spec_verify`: **PASS** 12/12 in 120.4s, 11 tool calls, ran pytest.  ([run folder](runs/iter1/t5_refactor/v2_spec_verify))

## 4. Behaviour notes (hand-written)

_Iteration 1 complete (10 runs, adaptive skips). Iteration 2/3 pending._

**Style.** Best brief-prompt model in the study (79%): the only perfect brief slugify (inferred the hardest Unicode rule), a perfect brief refactor, and a bug-fix done by rewriting via bash without opening an editor tool. Final messages are one dense sentence listing exactly what was handled.

**Scores.** Brief 79% -> spec 100% on the tasks that needed it (todo 0 -> 16/16 in 45 s, scheduler 21 -> 22/22 in 23 s). Spec + verify on the already-perfect tasks: still 100%, about twice the wall time (slugify 24 s -> 57 s, refactor 69 s -> 120 s).

**Quirks observed.**
- Brief todo: `Added: buy milk` with no id and `1. [ ] buy milk`; the one place a vague prompt cost it everything.
- Prefers bash for file operations when it can.

**Recommendation.** Spec only. Among the ceiling models it needs the least prompting and tolerates vague prompts best; add process scaffolding only for tasks much larger than these.

## 5. Recommended prompt recipe

Best-performing variant `v2_spec_verify` = components `spec + verify`. Rendered for `t3_todo_cli`:

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

After implementing, verify your work: write a quick test file named test_own.py covering the rules above (or use the tests already provided), run `python -m pytest -q`, and fix anything that fails. Do not finish until the tests pass. Include the final pytest summary line in your last message.
```

## 6. Sample final messages

**best run** (t4_scheduler / iter1 / `v1_spec`, 22/22):

> All cases pass, including the half-open touch `(1,3)+(3,5)` merging but `max_concurrent` counting them as non-overlapping.
> 
> Created `scheduler.py:1` with `merge_intervals`, `find_free_slots`, and `max_concurrent`.

**worst run** (t3_todo_cli / iter1 / `v0_brief`, 0/16):

> Created `todo.py` with `add`, `list`, `done`, `remove`, `clear` commands, persisting to `todos.json` next to the script. Verified all commands work.

