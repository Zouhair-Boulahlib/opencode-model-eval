# OpenCode free models: coding evaluation and prompting guide

Generated 2026-11-09 20:33. 179 runs, 11 models, 6 tasks, 10 prompt variants, iterations [1, 2, 3].

Every model ran through `opencode run` inside its own folder under `agents/<model>/`, with its own `opencode.json` (model pinned, Ollama disabled, web and question tools denied). Scores are the fraction of hidden pytest cases passed; a run that edits a protected test file scores 0.

## 1. Leaderboard (best prompt variant per model)

| # | model | best variant (coverage) | best variant mean | ceiling (best per task) | baseline (v0) | lift | avg wall s | avg out tokens | timeouts |
|---|---|---|---|---|---|---|---|---|---|
| 1 | [beam-free](agents/beam-free/REPORT.md) | v1_spec (5 tasks) | 100% | 100% | 76% | +24% | 98 | 1328 | 5% |
| 2 | [big-pickle](agents/big-pickle/REPORT.md) | v1_spec (5 tasks) | 100% | 100% | 77% | +23% | 37 | 1323 | 0% |
| 3 | [crouton-alpha-free](agents/crouton-alpha-free/REPORT.md) | v1_spec (5 tasks) | 100% | 100% | 66% | +34% | 38 | 1151 | 0% |
| 4 | [deepseek-v4.1-flash-free](agents/deepseek-v4.1-flash-free/REPORT.md) | v1_spec (5 tasks) | 100% | 100% | 77% | +23% | 35 | 1315 | 0% |
| 5 | [flint-40b-free](agents/flint-40b-free/REPORT.md) | m_flint_env_tool (3 tasks) | 100% | 100% | 76% | +24% | 213 | 10090 | 11% |
| 6 | [glm-5.3-flash-free](agents/glm-5.3-flash-free/REPORT.md) | v1_spec (3 tasks) | 100% | 100% | 75% | +25% | 47 | 1333 | 0% |
| 7 | [mimo-v2.6-flash-free](agents/mimo-v2.6-flash-free/REPORT.md) | v1_spec (4 tasks) | 100% | 100% | 77% | +23% | 119 | 1883 | 0% |
| 8 | [nvidia__minimaxai__minimax-m3.1-flash](agents/nvidia__minimaxai__minimax-m3.1-flash/REPORT.md) | v1_spec (3 tasks) | 100% | 100% | 77% | +23% | 1182 | 2393 | 10% |
| 9 | [pulse-alpha-free](agents/pulse-alpha-free/REPORT.md) | v2_spec_verify (3 tasks) | 100% | 100% | 79% | +21% | 53 | 1449 | 0% |
| 10 | [nemotron-3.5-super-vl-free](agents/nemotron-3.5-super-vl-free/REPORT.md) | v1_spec (4 tasks) | 97% | 100% | 73% | +24% | 53 | 1646 | 0% |
| 11 | [nemotron-3.5-lightning-free](agents/nemotron-3.5-lightning-free/REPORT.md) | v1_spec (5 tasks) | 96% | 100% | 61% | +36% | 132 | 3138 | 0% |

Cells with fewer than all tasks exist because adaptive mode skips a variant on a task whose cheaper predecessor already scored 100%; the ceiling column is the fairest cross-model comparison.

## 2. Score matrix: model x prompt variant (mean over tasks run; task count in parentheses)

| model | v0_brief | v10_spec_examples_env | v11_spec_env_edge | v1_spec | v2_spec_verify | v6_brief_verify | g0_spec_env | g1_spec_env_graph | m_flint_env_tool | m_flint_env_tool_verify |
|---|---|---|---|---|---|---|---|---|---|---|
| beam-free | 76% (5) | - | - | 100% (5) | 100% (5) | 50% (2) | 100% (1) | 100% (1) | - | - |
| big-pickle | 77% (5) | - | - | 100% (5) | 100% (5) | 95% (2) | 100% (1) | 100% (1) | - | - |
| crouton-alpha-free | 66% (5) | - | - | 100% (5) | 100% (5) | 95% (2) | 100% (1) | 100% (1) | - | - |
| deepseek-v4.1-flash-free | 77% (5) | - | - | 100% (5) | 100% (5) | 95% (2) | 100% (1) | 100% (1) | - | - |
| flint-40b-free | 76% (5) | - | - | 75% (4) | 100% (2) | - | 100% (1) | 100% (1) | 100% (3) | 100% (3) |
| glm-5.3-flash-free | 75% (5) | - | - | 100% (3) | 100% (2) | 95% (2) | 100% (1) | 100% (1) | - | - |
| mimo-v2.6-flash-free | 77% (5) | - | - | 100% (4) | 100% (2) | 98% (2) | 100% (1) | 100% (1) | - | - |
| nemotron-3.5-lightning-free | 61% (5) | 100% (2) | 100% (2) | 96% (5) | 91% (2) | - | 100% (1) | 100% (1) | - | - |
| nemotron-3.5-super-vl-free | 73% (5) | 100% (2) | 100% (2) | 97% (4) | 94% (2) | - | 100% (1) | 100% (1) | - | - |
| nvidia__minimaxai__minimax-m3.1-flash | 77% (5) | - | - | 100% (3) | 100% (2) | - | - | - | - | - |
| pulse-alpha-free | 79% (5) | - | - | 100% (2) | 100% (3) | - | - | - | - | - |
| **mean** | 74% | 100% | 100% | 97% | 99% | 88% | 100% | 100% | 100% | 100% |

## 3. Score by task (each model at its best variant)

| model | t1_slugify | t2_bugfix | t3_todo_cli | t4_scheduler | t5_refactor | t6_repo_bugfix |
|---|---|---|---|---|---|---|
| beam-free | 100% | 100% | 100% | 100% | 100% | - |
| big-pickle | 100% | 100% | 100% | 100% | 100% | - |
| crouton-alpha-free | 100% | 100% | 100% | 100% | 100% | - |
| deepseek-v4.1-flash-free | 100% | 100% | 100% | 100% | 100% | - |
| flint-40b-free | - | - | 100% | 100% | 100% | - |
| glm-5.3-flash-free | 100% | - | 100% | 100% | - | - |
| mimo-v2.6-flash-free | 100% | - | 100% | 100% | 100% | - |
| nemotron-3.5-lightning-free | 100% | 94% | 88% | 100% | 100% | - |
| nemotron-3.5-super-vl-free | 100% | - | 88% | 100% | 100% | - |
| nvidia__minimaxai__minimax-m3.1-flash | - | - | 100% | 100% | 100% | - |
| pulse-alpha-free | 100% | 100% | - | - | 100% | - |
| **mean (all runs)** | 94% | 100% | 66% | 91% | 97% | 100% |

## 4. What each prompting trick is worth (paired comparison, same model and task)

| change | meaning | mean delta | pairs | models up | models down |
|---|---|---|---|---|---|
| v0_brief -> v1_spec | full spec instead of one-line brief | +29.1 pts | 45 | 11/11 | 0/11 |
| v1_spec -> v2_spec_verify | + self-verify loop (write tests, run pytest, fix) | +4.0 pts | 25 | 1/8 | 0/8 |
| v0_brief -> v6_brief_verify | + verify loop on the one-line brief | -1.1 pts | 12 | 3/6 | 1/6 |

## 5. Behaviour profile per model (all runs)

| model | runs | tool calls/run | ran pytest | wrote own tests | LLM steps/run | final msg chars | timeouts | edited protected tests | question attempts | missing target file | tool errors/run | bash blocked (unquoted path) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| beam-free | 19 | 9.3 | 63% | 32% | 9.2 | 35 | 5% | 0 | 0 | 1 | 0.32 | 1 |
| big-pickle | 19 | 5.8 | 68% | 37% | 5.3 | 168 | 0% | 0 | 0 | 0 | 0.00 | 0 |
| crouton-alpha-free | 19 | 7.2 | 68% | 37% | 6.8 | 92 | 0% | 0 | 0 | 0 | 0.05 | 1 |
| deepseek-v4.1-flash-free | 19 | 5.8 | 68% | 37% | 4.9 | 164 | 0% | 0 | 0 | 0 | 0.00 | 0 |
| flint-40b-free | 19 | 14.7 | 58% | 26% | 12.6 | 878 | 11% | 0 | 0 | 2 | 5.84 | 21 |
| glm-5.3-flash-free | 14 | 6.6 | 57% | 29% | 6.6 | 413 | 0% | 0 | 0 | 0 | 0.07 | 0 |
| mimo-v2.6-flash-free | 15 | 6.8 | 60% | 27% | 5.8 | 419 | 0% | 0 | 0 | 0 | 0.07 | 1 |
| nemotron-3.5-lightning-free | 18 | 17.9 | 56% | 11% | 16.3 | 662 | 0% | 0 | 0 | 0 | 1.67 | 18 |
| nemotron-3.5-super-vl-free | 17 | 7.9 | 53% | 12% | 5.5 | 387 | 0% | 0 | 0 | 0 | 0.24 | 3 |
| nvidia__minimaxai__minimax-m3.1-flash | 10 | 12.1 | 60% | 20% | 9.6 | 467 | 10% | 0 | 0 | 0 | 0.50 | 4 |
| pulse-alpha-free | 10 | 5.1 | 50% | 30% | 6.0 | 262 | 0% | 0 | 0 | 0 | 0.20 | 0 |

## 6. Key findings and recommended tricks

_Status: three iterations complete. Iteration 1: 125 valid runs (10 models x 5 tasks x up to 3 prompt variants; adaptive mode skipped 25 runs whose cheaper variant already scored 100%). Iteration 2: 26 runs of targeted per-model variants (sections 6). Iteration 3: 18 runs of a repo-scale task with and without a graphify architecture map (section 7). `pulse-alpha-free` was retired by the provider before iterations 2 and 3, so they cover nine models. Every run was checked against the laptop's sleep log (section 8)._

### 1. The specification is the trick. Nothing else came close.

- From a one-line prompt the ten models average 73% (range 61% to 79%). With the full specification (file names, signatures, types, verbatim output strings, edge cases) seven of ten reach 100% on every task they ran, and the other three reach 96% to 100% ceiling.
- The largest single lifts were representation details, not logic: crouton lost 13 of 22 scheduler tests by returning lists instead of tuples; every model lost all 16 todo-CLI tests by inventing its own output format. The spec removed both.
- Spec runs were also *faster* than brief runs for the fast models (big-pickle 29 s -> 23 s, deepseek 27 s -> 29 s, crouton unchanged) because the model stops guessing and smoke-testing alternatives.

### 2. The self-verify loop ("write tests, run pytest, do not stop until green") bought nothing here.

- 25 paired cells (same model, same task, spec vs spec+verify): identical score in 22. The three exceptions: flint scheduler 0 -> 22 (its spec run had timed out after seven minutes of path confusion and the retry did not; a reliability effect, not a prompt effect), nemotron-lightning bug-fix 15 -> 16 and todo 14 -> 13 (noise in both directions).
- Every model complied (33 of 33 verify runs ran pytest and wrote a test file), and paid for it: wall time rose by a median of 30% per pair (range -57% to +243%; e.g. glm bug-fix 36 s -> 75 s, beam todo 91 s -> 200 s, mimo refactor 210 s -> 272 s) with about 40% more steps.
- It did not fix the one real spec-adherence bug in the set (the nemotron pair reusing ids): both ran their own tests and still shipped it.
- Conclusion for single-file tasks: provide tests instead of asking for them. On the bug-fix task, where tests were provided, nine of ten models were perfect from a one-line prompt.

### 3. Models differ far more in process than in result.

| trait | models |
|---|---|
| one-shot, 3 to 6 steps, no wasted calls | big-pickle, deepseek, mimo, nemotron-super-vl, pulse |
| look-around-first, surgical edits | beam, crouton, glm |
| thrashing (15 to 33 tool calls, repeated tool errors) | nemotron-lightning, flint |
| broken tool calling (wrong argument names, heredoc fallback) | flint only |
| searched the whole filesystem when the prompt was vague | beam, flint |
| assumed Linux paths (`/workspace`, `/home/<user>`, `/todo.py`) | nemotron-lightning |
| ignored an explicitly stated rule (ids never reused) | both nemotrons |

### 4. What works in the optimal scenario for software-engineering use

1. Write the contract: exact file names, function signatures, parameter names, return types, verbatim output strings, and the edge cases, in the prompt. If something will be parsed by a program or a test, quote the literal string.
2. Provide the tests you have. Asking the model to write its own tests costs time and did not change a single outcome.
3. Skip plan/verify/role scaffolding on single-file tasks with the ceiling models (big-pickle, deepseek, pulse, beam, mimo, glm, crouton). Keep guard rails for flint and the nemotrons.
4. State the environment on Windows: already in the working directory, relative paths, quote paths, the directory may be empty. Iteration 2 confirmed it for the two slowest models: tool errors per run fell from 6.36 to 4.00 (flint) and from 2.33 to 0.50 (nemotron-lightning), with no score lost.
5. Choose by cost when correctness is tied: big-pickle (23 s), deepseek (29 s), crouton (27 s) and pulse (34 s) reach the ceiling fastest with the spec; mimo (125 s) and glm (54 s) are slower; nemotron-lightning (162 s) and flint (269 s) are slow *and* less reliable.

### 5. Operational findings

- The hosted free tier allows roughly 45 runs per window, then every `opencode/*` model fails with "Free usage limit reached" and `opencode run` hangs with zero events instead of exiting. The harness treats zero-event runs as infrastructure failures, pauses all workers, probes every 5 minutes and resumes automatically. Resets observed after about 3.5 h and about 13 h.
- `opencode run` takes its session directory from the `PWD` environment variable, not the process cwd; scripts must set `PWD` and `--dir` or files land in the parent shell's directory.
- The per-agent `opencode.json` rule `external_directory: deny` blocked every attempted read outside a workspace (flint tried its own prompt file and another run's source); directory listings are not blocked. No hidden-test content reached any model (verified by `harness/qc_scan.py`).

### 6. Iteration 2: targeted prompts per model

**A verify loop cannot rescue a one-line prompt, because self-written tests only check the model's own assumptions.**
Six ceiling models got the one-line brief plus "write tests, run pytest, do not stop until green" on the slugify and
scheduler tasks (12 runs). Nine scored 21 of 22, two scored 22 of 22, and beam timed out once (0 of 22, 421 s).
The misses were identical across models: four of the five slugify misses were the same test (what happens to
non-ASCII input such as "Straße 日本"), and all five scheduler misses were the same test (invalid intervals must raise).
Neither rule is in the brief, so no amount of self-testing could find it; every one of those runs wrote and ran its own
tests. The same models reached 22 of 22 in iteration 1 from the specification, and faster (big-pickle 17 s with the spec
against 66 s with brief plus verify; deepseek 14 s against 67 s; crouton 15 s against 110 s).

**Worked examples and edge cases fixed the nemotron pair.** Both nemotrons had shipped the "ids are never reused" bug in
iteration 1 even after testing their own code (todo CLI, 14 of 16 from the spec). With the spec plus environment plus
either worked examples (`v10`) or an explicit edge-case walkthrough (`v11`), all four runs scored 16 of 16. The bug-fix
task stayed at 16 of 16. The price is time: nemotron-super-vl went from 39 s to 125-136 s on the todo task, and
nemotron-lightning used 27 and 48 steps.

**Environment and tool hints made flint reliable and faster.** With the environment clause plus a reminder of the tool
argument names (`m_flint_env_tool`), flint scored 100% on all three tasks it used to struggle with, and was faster than its
best iteration-1 run on two of them (todo 221 s -> 135 s, refactor 336 s -> 196 s; scheduler 180 s -> 168 s). Adding a
verify loop on top (`m_flint_env_tool_verify`) kept 100% but was slower on two of three tasks (297 s and 337 s).

### 7. Iteration 3: an architecture map did not change the outcome on a small repo

Nine models fixed a cross-module bug in a 17-file package (`t6_repo_bugfix`) with the specification and environment
clause, once without (`g0`) and once with (`g1`) the graphify architecture report in the prompt. All 18 runs scored 14 of
14, so the map could not raise scores here. It mostly cost time: the map run was slower for 7 of 9 models (median +7 s;
flint +57 s, nemotron-lightning +49 s, nemotron-super-vl +54 s) and faster for crouton (-20 s) and deepseek (-5 s). Step
counts went up for four models, stayed equal for three and went down for two. On a codebase a model can read in a dozen
calls, the extra 9,000 characters of map are overhead. The hypothesis that a map helps on repositories too large to read
remains untested here.

### 8. Data integrity: timings checked against the laptop's sleep log

The study ran on a laptop that entered standby or sleep 30 times between 5 and 9 November, for up to three hours at a
time, and wall-clock timers keep counting through it. `harness/standby_check.py` reads the Windows power log
(Kernel-Power events 42/107/506/507) and flags every run whose time window overlaps standby. Of 180 runs, two overlap,
both NVIDIA MiniMax runs that are not part of these findings; none of the 169 runs above is affected, and none of the
timeouts is a sleep artifact.

### 9. Data integrity: workspace isolation, one leak found and fixed

`harness/isolation_scan.py` lists every tool call that named a path outside the run's own `ws/` folder.

- Iteration 1 (the published core): no file outside a workspace was read; the few attempts were directory listings,
  several of them blocked by `external_directory: deny`.
- Iterations 2 and 3: no hidden test and no other model's solution was read. Six iteration-2 runs read only their own
  `prompt.txt` or their own transcript one folder up, and mimo listed the task folder (it saw the hidden test's file
  name, not its content; its slugify uses the standard Unicode-normalise-then-drop-non-ASCII approach). Iteration 3 made
  no outside access at all. Their scores stand.
- One NVIDIA MiniMax run (slugify, one-line prompt, 6 November) read the task's spec, examples and hidden test, then ran
  the hidden test. It is marked invalid (`invalid_reason` in its `result.json`) and excluded from every report.
- Root cause: OpenCode treats the enclosing git repository as the project, and `external_directory` only denies paths
  outside the project. This folder became a git repository on 6 November, after iteration 1, which silently widened
  every agent's reach to the whole repository. Fix: each run's `ws/` is now its own git repository with a copy of the
  agent's `opencode.json` (`isolate_workspace` in `harness/run_eval.py`). A verification run that told a model to read a
  hidden test and its parent folder's prompt got both reads refused.
- Lesson for anyone running agent evals: a permission rule is only as good as its notion of "outside". Re-check
  isolation whenever the folder layout or version control around the workspaces changes.

## 7. Per-agent reports

- [beam-free](agents/beam-free/REPORT.md): best variant `v1_spec` at 100%; runs live in `agents/beam-free/runs/`
- [big-pickle](agents/big-pickle/REPORT.md): best variant `v1_spec` at 100%; runs live in `agents/big-pickle/runs/`
- [crouton-alpha-free](agents/crouton-alpha-free/REPORT.md): best variant `v1_spec` at 100%; runs live in `agents/crouton-alpha-free/runs/`
- [deepseek-v4.1-flash-free](agents/deepseek-v4.1-flash-free/REPORT.md): best variant `v1_spec` at 100%; runs live in `agents/deepseek-v4.1-flash-free/runs/`
- [flint-40b-free](agents/flint-40b-free/REPORT.md): best variant `m_flint_env_tool` at 100%; runs live in `agents/flint-40b-free/runs/`
- [glm-5.3-flash-free](agents/glm-5.3-flash-free/REPORT.md): best variant `v1_spec` at 100%; runs live in `agents/glm-5.3-flash-free/runs/`
- [mimo-v2.6-flash-free](agents/mimo-v2.6-flash-free/REPORT.md): best variant `v1_spec` at 100%; runs live in `agents/mimo-v2.6-flash-free/runs/`
- [nemotron-3.5-lightning-free](agents/nemotron-3.5-lightning-free/REPORT.md): best variant `v1_spec` at 96%; runs live in `agents/nemotron-3.5-lightning-free/runs/`
- [nemotron-3.5-super-vl-free](agents/nemotron-3.5-super-vl-free/REPORT.md): best variant `v1_spec` at 97%; runs live in `agents/nemotron-3.5-super-vl-free/runs/`
- [nvidia__minimaxai__minimax-m3.1-flash](agents/nvidia__minimaxai__minimax-m3.1-flash/REPORT.md): best variant `v1_spec` at 100%; runs live in `agents/nvidia__minimaxai__minimax-m3.1-flash/runs/`
- [pulse-alpha-free](agents/pulse-alpha-free/REPORT.md): best variant `v2_spec_verify` at 100%; runs live in `agents/pulse-alpha-free/runs/`

## 8. Method

- Tasks (`harness/tasks/`): `t1_slugify` (spec compliance / pure function); `t2_bugfix` (debugging existing code / not breaking tests); `t3_todo_cli` (agentic build / exact I-O contract); `t4_scheduler` (algorithms / edge cases); `t5_refactor` (refactoring / constraint following / preserving behaviour); `t6_repo_bugfix` (codebase navigation / root-cause debugging across files)
- Prompt variants are ordered lists of components (`harness/prompts.py`); per-model custom variants live in `agents/<model>/prompts/variants.json`.
- Loop: run variant -> score with hidden tests -> read transcripts and failure modes -> write a targeted variant -> rerun. Iteration 1 is the broad sweep; later iterations are per-model refinements.
- Each run folder holds `prompt.txt`, `events.jsonl` (raw model/tool stream), `tools.jsonl`, `pytest_output.txt`, `result.json` and the workspace `ws/`.
- Regenerate with `python harness/make_reports.py`; rerun with `python harness/run_eval.py --iter N --variants ...`.
