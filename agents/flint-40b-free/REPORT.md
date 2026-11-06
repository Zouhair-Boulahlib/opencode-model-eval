# opencode/flint-40b-free: behaviour and prompting report

Generated 2026-11-06 16:11 from 11 runs. Best variant: `v0_brief` with mean score 76% (baseline `v0_brief`: 76%).

## 1. Scores

### Iteration 1

| task | v0_brief | v1_spec | v2_spec_verify |
|---|---|---|---|
| t1_slugify | 21/22 | 22/22 | - |
| t2_bugfix | 16/16 | - | 16/16 |
| t3_todo_cli | 0/16 T | 16/16 | - |
| t4_scheduler | 20/22 | 0/22 T | 22/22 |
| t5_refactor | 11/12 | 12/12 | - |
| **mean** | 76% | 75% | 100% |

Legend: `passed/total`; `T` = timed out; `P!` = edited a protected test file (scored 0).

## 2. Behaviour profile

| metric | value |
|---|---|
| runs | 11 |
| mean score (all runs) | 80% |
| perfect runs / zero runs | 6 / 2 |
| avg wall time | 231 s |
| avg tokens in / out / reasoning | 17810 / 9770 / 0 |
| avg LLM steps per run | 13.3 |
| avg tool calls per run (errors) | 14.5 (6.36) |
| tool usage (total) | bash: 90, write: 28, read: 23, edit: 11, glob: 8 |
| tool errors by tool (total) | bash: 19, edit: 11, read: 18, write: 22 |
| bash calls blocked by permission (unquoted absolute path with a space) | 17 |
| ran pytest / wrote own tests | 45% / 18% |
| timeouts | 18% |
| edited protected test files | 0 |
| question-tool attempts / final message is a question | 0 / 0% |
| target file missing at end | 2 |
| avg final message length | 785 chars |
| runs with provider/tool errors | 0 |

### Behaviour by prompt variant

| variant | runs | mean score | wall s | tools/run | ran pytest | own tests | timeouts | final chars |
|---|---|---|---|---|---|---|---|---|
| v0_brief | 5 | 76% | 230 | 16.6 | 40% | 0% | 20% | 712 |
| v1_spec | 4 | 75% | 269 | 12.5 | 25% | 0% | 25% | 958 |
| v2_spec_verify | 2 | 100% | 159 | 13.5 | 100% | 100% | 0% | 622 |

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

### t4_scheduler

- iter1 `v0_brief`: **FAIL** 20/22 in 75.1s, 4 tool calls, never ran tests. failed: test_merge_invalid_raises, test_free_busy_entirely_outside_ignored ([run folder](runs/iter1/t4_scheduler/v0_brief))
- iter1 `v1_spec`: **TIMEOUT** 0/22 in 421.8s, 12 tool calls, never ran tests. target file never created ([run folder](runs/iter1/t4_scheduler/v1_spec))
- iter1 `v2_spec_verify`: **PASS** 22/22 in 180.5s, 13 tool calls, ran pytest.  ([run folder](runs/iter1/t4_scheduler/v2_spec_verify))

### t5_refactor

- iter1 `v0_brief`: **FAIL** 11/12 in 411.5s, 16 tool calls, ran pytest. failed: test_no_function_longer_than_20_lines ([run folder](runs/iter1/t5_refactor/v0_brief))
- iter1 `v1_spec`: **PASS** 12/12 in 336.5s, 16 tool calls, ran pytest.  ([run folder](runs/iter1/t5_refactor/v1_spec))

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

Best-performing variant `v0_brief` = components `brief`. Rendered for `t3_todo_cli`:

```text
Build a command-line todo app in todo.py (commands: add, list, done, remove, clear) that saves tasks to a JSON file.
```

## 6. Sample final messages

**best run** (t1_slugify / iter1 / `v1_spec`, 22/22):

> All rules verified — the two "FAIL" lines were mistakes in my hand-written expectations, not in the implementation:
> 
> - `slugify("Hello World", 5)` → `"hello"` ✓ (cut to 5 chars, then strip trailing hyphen)
> - `slugify("Hello World", 7)` → `"hello-w"` ✓ (cut to 7 chars, strip trailing hyphen → none left)
> 
> Created `slugify.py` in the current directory with the requested `slugify(text: str, max_length: int | None = None) -> str` function, using only the standard library (`unicodedata` and `re`):
> 
> - **Step 1:** `unicodedata.normalize("NFKD", ...)` + dropping combining marks via `unicodedata.combining`, so `"Crème Brûlée"` → `"Creme Brulee"`.
> - **Step 2:** `.lower()` applied before the separator replacement, so the regex `[^a-z0-9]+` correctly treats any remaining non-ASCII letter/digit (e.g. `ß`, `日`) as a separator.
> - **Steps 3–4:** the regex collapses runs of separators into a single `-`, then `.strip("-")` removes leading/trailing hyphens.
> - **Step 5:** `max_length <= 0` returns `""`; otherwise the slug is truncated with slicing and trailing hyphens stripped again.
> - **Step 6:** empty/separators-only input naturally yields `""`.
> 
> No other source files were created.

**worst run** (t3_todo_cli / iter1 / `v0_brief`, 0/16):

> _(no final text)_

