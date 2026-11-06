# opencode/glm-5.3-flash-free: behaviour and prompting report

Generated 2026-11-06 16:11 from 10 runs. Best variant: `v1_spec` with mean score 100% (baseline `v0_brief`: 75%).

## 1. Scores

### Iteration 1

| task | v0_brief | v1_spec | v2_spec_verify |
|---|---|---|---|
| t1_slugify | 21/22 | 22/22 | - |
| t2_bugfix | 16/16 | - | 16/16 |
| t3_todo_cli | 0/16 | 16/16 | - |
| t4_scheduler | 18/22 | 22/22 | - |
| t5_refactor | 12/12 | - | 12/12 |
| **mean** | 75% | 100% | 100% |

Legend: `passed/total`; `T` = timed out; `P!` = edited a protected test file (scored 0).

## 2. Behaviour profile

| metric | value |
|---|---|
| runs | 10 |
| mean score (all runs) | 88% |
| perfect runs / zero runs | 7 / 1 |
| avg wall time | 53 s |
| avg tokens in / out / reasoning | 16793 / 1529 / 360 |
| avg LLM steps per run | 6.9 |
| avg tool calls per run (errors) | 6.9 (0.10) |
| tool usage (total) | bash: 23, edit: 21, read: 12, write: 10, glob: 3 |
| tool errors by tool (total) | edit: 1 |
| bash calls blocked by permission (unquoted absolute path with a space) | 0 |
| ran pytest / wrote own tests | 40% / 20% |
| timeouts | 0% |
| edited protected test files | 0 |
| question-tool attempts / final message is a question | 0 / 0% |
| target file missing at end | 0 |
| avg final message length | 436 chars |
| runs with provider/tool errors | 0 |

### Behaviour by prompt variant

| variant | runs | mean score | wall s | tools/run | ran pytest | own tests | timeouts | final chars |
|---|---|---|---|---|---|---|---|---|
| v0_brief | 5 | 75% | 34 | 5.4 | 40% | 0% | 0% | 414 |
| v1_spec | 3 | 100% | 54 | 5.3 | 0% | 0% | 0% | 489 |
| v2_spec_verify | 2 | 100% | 99 | 13.0 | 100% | 100% | 0% | 410 |

## 3. Failure analysis

### t1_slugify

- iter1 `v0_brief`: **FAIL** 21/22 in 31.1s, 5 tool calls, never ran tests. failed: test_basic[Stra\xdfe \u65e5\u672c-stra-e] ([run folder](runs/iter1/t1_slugify/v0_brief))
- iter1 `v1_spec`: **PASS** 22/22 in 20.1s, 2 tool calls, never ran tests.  ([run folder](runs/iter1/t1_slugify/v1_spec))

### t2_bugfix

- iter1 `v0_brief`: **PASS** 16/16 in 36.2s, 10 tool calls, ran pytest.  ([run folder](runs/iter1/t2_bugfix/v0_brief))
- iter1 `v2_spec_verify`: **PASS** 16/16 in 75.2s, 10 tool calls, ran pytest.  ([run folder](runs/iter1/t2_bugfix/v2_spec_verify))

### t3_todo_cli

- iter1 `v0_brief`: **FAIL** 0/16 in 27.0s, 3 tool calls, never ran tests. failed: test_list_empty, test_add_prints_exact_line, test_add_and_list, test_done_marks_task, test_done_twice_ok, test_remove, test_ids_never_reused_after_remove, test_ids_never_reused_after_clear ... ([run folder](runs/iter1/t3_todo_cli/v0_brief))
- iter1 `v1_spec`: **PASS** 16/16 in 91.4s, 9 tool calls, never ran tests.  ([run folder](runs/iter1/t3_todo_cli/v1_spec))

### t4_scheduler

- iter1 `v0_brief`: **FAIL** 18/22 in 25.0s, 3 tool calls, never ran tests. failed: test_merge_invalid_raises, test_free_empty_busy, test_free_empty_busy_day_too_short, test_free_busy_entirely_outside_ignored ([run folder](runs/iter1/t4_scheduler/v0_brief))
- iter1 `v1_spec`: **PASS** 22/22 in 50.3s, 5 tool calls, never ran tests.  ([run folder](runs/iter1/t4_scheduler/v1_spec))

### t5_refactor

- iter1 `v0_brief`: **PASS** 12/12 in 48.3s, 6 tool calls, ran pytest.  ([run folder](runs/iter1/t5_refactor/v0_brief))
- iter1 `v2_spec_verify`: **PASS** 12/12 in 122.2s, 16 tool calls, ran pytest.  ([run folder](runs/iter1/t5_refactor/v2_spec_verify))

## 4. Behaviour notes (hand-written)

_Iteration 1 complete (10 runs, adaptive skips). Iteration 2/3 pending._

**Style.** Methodical: write, quick check, one `edit` to tighten, rerun. Structured bullet summaries with file references (around 400 to 500 characters).

**Scores.** Brief 75% -> spec 100% on the tasks it ran (slugify 22/22 in 20 s, todo 16/16, scheduler 18 -> 22/22). Bug-fix and refactor were already 100% from the brief. Spec + verify on bug-fix and refactor: 100% but 2 to 2.5x the wall time (bug-fix 36 s -> 75 s, refactor 48 s -> 122 s, 16 steps).

**Quirks observed.**
- Edge-case coverage is its weak spot from a vague prompt: scheduler brief missed empty-busy, day-too-short and busy-outside-the-day cases.
- Expensive when asked to verify: it writes a real test file and iterates (the pilot run took 9 minutes on slugify for that reason).

**Recommendation.** Spec with the edge cases listed. Avoid the verify loop unless the task is large; a compact "walk through each rule" instruction is the cheaper alternative to test in iteration 2.

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

> Created `slugify.py` and verified all cases: NFKD accent stripping ('Crème Brûlée' → 'creme-brulee'), non-ASCII leftovers like 'ß' and '日本' treated as separators, run collapsing, hyphen stripping, `max_length` handling (including 0 → ""), and empty/separator-only input.

**worst run** (t3_todo_cli / iter1 / `v0_brief`, 0/16):

> Done. `todo.py` implements all five commands, persisting to `todos.json` next to the script (verified end-to-end above):
> 
> - `add <text>` — adds a task with auto-incrementing id
> - `list` — shows `[x]`/`[ ]` status per task
> - `done <id>` — marks a task complete
> - `remove <id>` — deletes a task (invalid/missing ids exit with an error)
> - `clear` — wipes all tasks, or only completed ones with `--completed`

