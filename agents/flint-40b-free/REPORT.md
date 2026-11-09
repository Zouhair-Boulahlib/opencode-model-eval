# opencode/flint-40b-free: behaviour and prompting report

Generated 2026-11-09 20:33 from 19 runs. Best variant: `m_flint_env_tool` with mean score 100% (baseline `v0_brief`: 76%).

## 1. Scores

### Iteration 1

| task | v0_brief | v1_spec | v2_spec_verify |
|---|---|---|---|
| t1_slugify | 21/22 | 22/22 | - |
| t2_bugfix | 16/16 | - | 16/16 |
| t3_todo_cli | 0/16 T | 16/16 | - |
| t4_scheduler | 20/22 | 0/22 T | 22/22 |
| t5_refactor | 11/12 | 12/12 | - |
| t6_repo_bugfix | - | - | - |
| **mean** | 76% | 75% | 100% |

Legend: `passed/total`; `T` = timed out; `P!` = edited a protected test file (scored 0).

### Iteration 2

| task | m_flint_env_tool | m_flint_env_tool_verify |
|---|---|---|
| t1_slugify | - | - |
| t2_bugfix | - | - |
| t3_todo_cli | 16/16 | 16/16 |
| t4_scheduler | 22/22 | 22/22 |
| t5_refactor | 12/12 | 12/12 |
| t6_repo_bugfix | - | - |
| **mean** | 100% | 100% |

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
| avg wall time | 213 s |
| avg tokens in / out / reasoning | 20638 / 10090 / 0 |
| avg LLM steps per run | 12.6 |
| avg tool calls per run (errors) | 14.7 (5.84) |
| tool usage (total) | bash: 154, read: 51, write: 44, edit: 22, glob: 8 |
| tool errors by tool (total) | bash: 23, edit: 22, read: 34, write: 32 |
| bash calls blocked by permission (unquoted absolute path with a space) | 21 |
| ran pytest / wrote own tests | 58% / 26% |
| timeouts | 11% |
| edited protected test files | 0 |
| question-tool attempts / final message is a question | 0 / 0% |
| target file missing at end | 2 |
| avg final message length | 878 chars |
| runs with provider/tool errors | 0 |

### Behaviour by prompt variant

| variant | runs | mean score | wall s | tools/run | ran pytest | own tests | timeouts | final chars |
|---|---|---|---|---|---|---|---|---|
| v0_brief | 5 | 76% | 230 | 16.6 | 40% | 0% | 20% | 712 |
| v1_spec | 4 | 75% | 269 | 12.5 | 25% | 0% | 25% | 958 |
| v2_spec_verify | 2 | 100% | 159 | 13.5 | 100% | 100% | 0% | 622 |
| g0_spec_env | 1 | 100% | 95 | 23.0 | 100% | 0% | 0% | 1200 |
| g1_spec_env_graph | 1 | 100% | 152 | 27.0 | 100% | 0% | 0% | 1502 |
| m_flint_env_tool | 3 | 100% | 166 | 9.0 | 33% | 0% | 0% | 1107 |
| m_flint_env_tool_verify | 3 | 100% | 255 | 14.0 | 100% | 100% | 0% | 677 |

## 3. Failure analysis

### t1_slugify

- iter1 `v0_brief`: **FAIL** 21/22 in 76.2s, 8 tool calls, never ran tests. failed: test_basic[Stra\xdfe \u65e5\u672c-stra-e] ([run folder](runs/iter1/t1_slugify/v0_brief))
- iter1 `v1_spec`: **PASS** 22/22 in 95.3s, 6 tool calls, never ran tests.  ([run folder](runs/iter1/t1_slugify/v1_spec))

### t2_bugfix

- iter1 `v0_brief`: **PASS** 16/16 in 166.2s, 17 tool calls, ran pytest.  ([run folder](runs/iter1/t2_bugfix/v0_brief))
- iter1 `v2_spec_verify`: **PASS** 16/16 in 138.2s, 14 tool calls, ran pytest.  ([run folder](runs/iter1/t2_bugfix/v2_spec_verify))

### t3_todo_cli

- iter1 `v0_brief`: **TIMEOUT** 0/16 in 421.2s, 38 tool calls, never ran tests. target file never created ([run folder](runs/iter1/t3_todo_cli/v0_brief))
- iter1 `v1_spec`: **PASS** 16/16 in 220.6s, 16 tool calls, never ran tests.  ([run folder](runs/iter1/t3_todo_cli/v1_spec))
- iter2 `m_flint_env_tool`: **PASS** 16/16 in 135.1s, 10 tool calls, never ran tests.  ([run folder](runs/iter2/t3_todo_cli/m_flint_env_tool))
- iter2 `m_flint_env_tool_verify`: **PASS** 16/16 in 297.3s, 18 tool calls, ran pytest.  ([run folder](runs/iter2/t3_todo_cli/m_flint_env_tool_verify))

### t4_scheduler

- iter1 `v0_brief`: **FAIL** 20/22 in 75.1s, 4 tool calls, never ran tests. failed: test_merge_invalid_raises, test_free_busy_entirely_outside_ignored ([run folder](runs/iter1/t4_scheduler/v0_brief))
- iter1 `v1_spec`: **TIMEOUT** 0/22 in 421.8s, 12 tool calls, never ran tests. target file never created ([run folder](runs/iter1/t4_scheduler/v1_spec))
- iter1 `v2_spec_verify`: **PASS** 22/22 in 180.5s, 13 tool calls, ran pytest.  ([run folder](runs/iter1/t4_scheduler/v2_spec_verify))
- iter2 `m_flint_env_tool`: **PASS** 22/22 in 168.1s, 9 tool calls, never ran tests.  ([run folder](runs/iter2/t4_scheduler/m_flint_env_tool))
- iter2 `m_flint_env_tool_verify`: **PASS** 22/22 in 131.2s, 11 tool calls, ran pytest.  ([run folder](runs/iter2/t4_scheduler/m_flint_env_tool_verify))

### t5_refactor

- iter1 `v0_brief`: **FAIL** 11/12 in 411.5s, 16 tool calls, ran pytest. failed: test_no_function_longer_than_20_lines ([run folder](runs/iter1/t5_refactor/v0_brief))
- iter1 `v1_spec`: **PASS** 12/12 in 336.5s, 16 tool calls, ran pytest.  ([run folder](runs/iter1/t5_refactor/v1_spec))
- iter2 `m_flint_env_tool`: **PASS** 12/12 in 196.2s, 8 tool calls, ran pytest.  ([run folder](runs/iter2/t5_refactor/m_flint_env_tool))
- iter2 `m_flint_env_tool_verify`: **PASS** 12/12 in 337.3s, 13 tool calls, ran pytest.  ([run folder](runs/iter2/t5_refactor/m_flint_env_tool_verify))

### t6_repo_bugfix

- iter3 `g0_spec_env`: **PASS** 14/14 in 95.1s, 23 tool calls, ran pytest.  ([run folder](runs/iter3/t6_repo_bugfix/g0_spec_env))
- iter3 `g1_spec_env_graph`: **PASS** 14/14 in 152.1s, 27 tool calls, ran pytest.  ([run folder](runs/iter3/t6_repo_bugfix/g1_spec_env_graph))

## 4. Behaviour notes (hand-written)

_Iteration 1 complete (11 runs, 2 timeouts). Iteration 2 targets it specifically._

**Style.** Verbose (700 to 950 character summaries), exploratory, and the only model with a tool-reliability problem. Average 230 s per task on the brief, 269 s with the spec; 12 to 17 tool calls per run with 5 to 8 tool *errors* per run.

**Scores.** Capable when the file lands: slugify 22/22, todo CLI 16/16, refactor 12/12, bug-fix 16/16 with the spec or verify prompts. Ceiling 100%. But two 7-minute timeouts: brief todo (never created the file) and spec scheduler (0/22).

**Quirks observed.**
- Calls `write` and `read` with wrong argument names (`path` instead of `filePath`, or missing the path), 2 to 5 rejected calls in a row, then falls back to `cat > file << 'EOF'` in bash.
- Mangles the workspace path containing a space (`eval/opencode` instead of `eval opencode`), then probes the filesystem root, mounts and sibling folders for minutes.
- From the brief todo prompt: searched `/` for an existing todo.py, listed sibling run folders, tried to read its own prompt file (blocked by the directory rule), and looped on `python -c` probes until the timeout.
- Verify-prompt scheduler run (22/22 in 180 s) shows that once it writes the file, the code is right.

**Recommendation.** Guard rails, not guidance: tell it the directory may be empty and it must create the file, forbid looking outside the directory, use relative paths, and remind it of the write tool's two argument names (or tell it to write files via bash heredoc). Iteration 2 tests exactly that (`m_flint_env_tool`, with and without verify). Avoid for time-sensitive work regardless.

## 5. Recommended prompt recipe

Best-performing variant `m_flint_env_tool` = components `env + toolhint + spec + files_exact`. Rendered for `t3_todo_cli`:

```text
Environment: you are already inside the project directory on Windows (Git Bash shell, Python 3.13 available as `python`). The directory may be empty; if a file does not exist, create it. Use relative paths only, never `cd` to absolute paths, and do not look at or search any directory outside the current one.

Tool usage: the write tool takes exactly two arguments, `filePath` and `content`; the read tool takes `filePath`. If a tool call is rejected for invalid arguments, fix the argument names instead of retrying the same call.

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

Create or modify ONLY the file(s) named in the task, with exactly those names, in the current directory. Do not create packages, folders or extra modules.
```

## 6. Sample final messages

**best run** (t6_repo_bugfix / iter3 / `g0_spec_env`, 14/14):

> **Result: `python -m pytest tests -q` → 3 passed, 0 failed.**
> 
> **Root cause:** The CSV importer (`ledger/importers/csv_importer.py`) converted amounts to minor units with a hardcoded `int(amount * 100)` — an implicit two-decimal (USD/EUR-style) assumption. For zero-decimal currencies like JPY, this multiplied the value by 100 twice the needed scale, inflating monthly totals by 100× (e.g. JPY total of `248000` became `24800000`). The JSON and QIF importers already used the correct currency-aware helper, which is why only CSV imports in JPY broke.
> 
> **Fix:** Replaced the hardcoded shift with the project's existing helper `to_minor_units(amount, currency)` from `ledger/currency.py`, which scales by the ISO 4217 exponent for the given currency (×100 for 2-decimal, ×1 for 0-decimal like JPY, ×1000 for 3-decimal like KWD).
> 
> **Verification:**
> - JPY CSV import now totals `248000` ✓
> - KWD (3-decimal) CSV import now totals `3.250` correctly ✓
> - USD CSV totals unchanged (`3195.50`) ✓
> - JSON imports in all currencies unaffected ✓
> 
> **Files changed:** `ledger/importers/csv_importer.py` (single file; one import added, one line replaced — no behaviour changes to reports, storage, or JSON importer).

**worst run** (t3_todo_cli / iter1 / `v0_brief`, 0/16):

> _(no final text)_

