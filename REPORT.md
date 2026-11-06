# OpenCode free models: coding evaluation and prompting guide

Generated 2026-11-06 16:11. 125 runs, 10 models, 5 tasks, 3 prompt variants, iterations [1].

Every model ran through `opencode run` inside its own folder under `agents/<model>/`, with its own `opencode.json` (model pinned, Ollama disabled, web and question tools denied). Scores are the fraction of hidden pytest cases passed; a run that edits a protected test file scores 0.

## 1. Leaderboard (best prompt variant per model)

| # | model | best variant (coverage) | best variant mean | ceiling (best per task) | baseline (v0) | lift | avg wall s | avg out tokens | timeouts |
|---|---|---|---|---|---|---|---|---|---|
| 1 | [beam-free](agents/beam-free/REPORT.md) | v1_spec (5 tasks) | 100% | 100% | 76% | +24% | 65 | 1402 | 0% |
| 2 | [big-pickle](agents/big-pickle/REPORT.md) | v1_spec (5 tasks) | 100% | 100% | 77% | +23% | 31 | 1386 | 0% |
| 3 | [crouton-alpha-free](agents/crouton-alpha-free/REPORT.md) | v1_spec (5 tasks) | 100% | 100% | 66% | +34% | 28 | 1140 | 0% |
| 4 | [deepseek-v4.1-flash-free](agents/deepseek-v4.1-flash-free/REPORT.md) | v1_spec (5 tasks) | 100% | 100% | 77% | +23% | 31 | 1368 | 0% |
| 5 | [glm-5.3-flash-free](agents/glm-5.3-flash-free/REPORT.md) | v1_spec (3 tasks) | 100% | 100% | 75% | +25% | 53 | 1529 | 0% |
| 6 | [mimo-v2.6-flash-free](agents/mimo-v2.6-flash-free/REPORT.md) | v1_spec (4 tasks) | 100% | 100% | 77% | +23% | 111 | 2048 | 0% |
| 7 | [pulse-alpha-free](agents/pulse-alpha-free/REPORT.md) | v2_spec_verify (3 tasks) | 100% | 100% | 79% | +21% | 53 | 1449 | 0% |
| 8 | [nemotron-3.5-super-vl-free](agents/nemotron-3.5-super-vl-free/REPORT.md) | v1_spec (4 tasks) | 97% | 98% | 73% | +24% | 41 | 1432 | 0% |
| 9 | [nemotron-3.5-lightning-free](agents/nemotron-3.5-lightning-free/REPORT.md) | v1_spec (5 tasks) | 96% | 98% | 61% | +36% | 131 | 3450 | 0% |
| 10 | [flint-40b-free](agents/flint-40b-free/REPORT.md) | v0_brief (5 tasks) | 76% | 100% | 76% | 0% | 231 | 9770 | 18% |

Cells with fewer than all tasks exist because adaptive mode skips a variant on a task whose cheaper predecessor already scored 100%; the ceiling column is the fairest cross-model comparison.

## 2. Score matrix: model x prompt variant (mean over tasks run; task count in parentheses)

| model | v0_brief | v1_spec | v2_spec_verify |
|---|---|---|---|
| beam-free | 76% (5) | 100% (5) | 100% (5) |
| big-pickle | 77% (5) | 100% (5) | 100% (5) |
| crouton-alpha-free | 66% (5) | 100% (5) | 100% (5) |
| deepseek-v4.1-flash-free | 77% (5) | 100% (5) | 100% (5) |
| flint-40b-free | 76% (5) | 75% (4) | 100% (2) |
| glm-5.3-flash-free | 75% (5) | 100% (3) | 100% (2) |
| mimo-v2.6-flash-free | 77% (5) | 100% (4) | 100% (2) |
| nemotron-3.5-lightning-free | 61% (5) | 96% (5) | 91% (2) |
| nemotron-3.5-super-vl-free | 73% (5) | 97% (4) | 94% (2) |
| pulse-alpha-free | 79% (5) | 100% (2) | 100% (3) |
| **mean** | 73% | 97% | 98% |

## 3. Score by task (each model at its best variant)

| model | t1_slugify | t2_bugfix | t3_todo_cli | t4_scheduler | t5_refactor |
|---|---|---|---|---|---|
| beam-free | 100% | 100% | 100% | 100% | 100% |
| big-pickle | 100% | 100% | 100% | 100% | 100% |
| crouton-alpha-free | 100% | 100% | 100% | 100% | 100% |
| deepseek-v4.1-flash-free | 100% | 100% | 100% | 100% | 100% |
| flint-40b-free | 95% | 100% | 0% | 91% | 92% |
| glm-5.3-flash-free | 100% | - | 100% | 100% | - |
| mimo-v2.6-flash-free | 100% | - | 100% | 100% | 100% |
| nemotron-3.5-lightning-free | 100% | 94% | 88% | 100% | 100% |
| nemotron-3.5-super-vl-free | 100% | - | 88% | 100% | 100% |
| pulse-alpha-free | 100% | 100% | - | - | 100% |
| **mean (all runs)** | 97% | 100% | 59% | 89% | 97% |

## 4. What each prompting trick is worth (paired comparison, same model and task)

| change | meaning | mean delta | pairs | models up | models down |
|---|---|---|---|---|---|
| v0_brief -> v1_spec | full spec instead of one-line brief | +28.5 pts | 42 | 10/10 | 0/10 |
| v1_spec -> v2_spec_verify | + self-verify loop (write tests, run pytest, fix) | +4.0 pts | 25 | 1/8 | 0/8 |

## 5. Behaviour profile per model (all runs)

| model | runs | tool calls/run | ran pytest | wrote own tests | LLM steps/run | final msg chars | timeouts | edited protected tests | question attempts | missing target file | tool errors/run | bash blocked (unquoted path) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| beam-free | 15 | 8.8 | 60% | 33% | 8.7 | 20 | 0% | 0 | 0 | 0 | 0.13 | 1 |
| big-pickle | 15 | 5.3 | 60% | 33% | 5.1 | 163 | 0% | 0 | 0 | 0 | 0.00 | 0 |
| crouton-alpha-free | 15 | 5.7 | 60% | 33% | 6.3 | 83 | 0% | 0 | 0 | 0 | 0.07 | 1 |
| deepseek-v4.1-flash-free | 15 | 5.3 | 60% | 33% | 4.7 | 148 | 0% | 0 | 0 | 0 | 0.00 | 0 |
| flint-40b-free | 11 | 14.5 | 45% | 18% | 13.3 | 785 | 18% | 0 | 0 | 2 | 6.36 | 17 |
| glm-5.3-flash-free | 10 | 6.9 | 40% | 20% | 6.9 | 436 | 0% | 0 | 0 | 0 | 0.10 | 0 |
| mimo-v2.6-flash-free | 11 | 6.2 | 45% | 18% | 5.6 | 423 | 0% | 0 | 0 | 0 | 0.09 | 1 |
| nemotron-3.5-lightning-free | 12 | 15.1 | 50% | 17% | 14.2 | 641 | 0% | 0 | 0 | 0 | 2.33 | 17 |
| nemotron-3.5-super-vl-free | 11 | 5.2 | 45% | 18% | 4.5 | 276 | 0% | 0 | 0 | 0 | 0.18 | 1 |
| pulse-alpha-free | 10 | 5.1 | 50% | 30% | 6.0 | 262 | 0% | 0 | 0 | 0 | 0.20 | 0 |

## 6. Key findings and recommended tricks

_Status: iteration 1 complete (125 valid runs: 10 models x 5 tasks x up to 3 prompt variants; adaptive mode skipped 25 runs whose cheaper variant already scored 100%). Iteration 3 (repo-scale task with and without a graphify architecture map) and iteration 2 (targeted per-model variants) are queued behind the free-tier quota; their findings will be appended._

### 1. The specification is the trick. Nothing else came close.

- From a one-line prompt the ten models average 73% (range 61% to 79%). With the full specification (file names, signatures, types, verbatim output strings, edge cases) seven of ten reach 100% on every task they ran, and the other three reach 96% to 100% ceiling.
- The largest single lifts were representation details, not logic: crouton lost 13 of 22 scheduler tests by returning lists instead of tuples; every model lost all 16 todo-CLI tests by inventing its own output format. The spec removed both.
- Spec runs were also *faster* than brief runs for the fast models (big-pickle 29 s -> 23 s, deepseek 27 s -> 29 s, crouton unchanged) because the model stops guessing and smoke-testing alternatives.

### 2. The self-verify loop ("write tests, run pytest, do not stop until green") bought nothing here.

- 32 paired cells: identical score in every one, except flint where a verify-prompt retry recovered a timed-out spec run (a reliability effect, not a prompt effect).
- Every model complied (100% ran pytest, 100% wrote a test file), and paid for it: +30% to +150% wall time (glm bug-fix 36 s -> 75 s; beam todo 91 s -> 200 s; mimo refactor 210 s -> 272 s) and +40% steps.
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
4. State the environment on Windows: already in the working directory, relative paths, quote paths, the directory may be empty. This targets the three models that wasted the most time (tested in iteration 2).
5. Choose by cost when correctness is tied: big-pickle (23 s), deepseek (29 s), crouton (27 s) and pulse (34 s) reach the ceiling fastest with the spec; mimo (125 s) and glm (54 s) are slower; nemotron-lightning (162 s) and flint (269 s) are slow *and* less reliable.

### 5. Operational findings

- The hosted free tier allows roughly 45 runs per window, then every `opencode/*` model fails with "Free usage limit reached" and `opencode run` hangs with zero events instead of exiting. The harness treats zero-event runs as infrastructure failures, pauses all workers, probes every 5 minutes and resumes automatically. Resets observed after about 3.5 h and about 13 h.
- `opencode run` takes its session directory from the `PWD` environment variable, not the process cwd; scripts must set `PWD` and `--dir` or files land in the parent shell's directory.
- The per-agent `opencode.json` rule `external_directory: deny` blocked every attempted read outside a workspace (flint tried its own prompt file and another run's source); directory listings are not blocked. No hidden-test content reached any model (verified by `harness/qc_scan.py`).

## 7. Per-agent reports

- [beam-free](agents/beam-free/REPORT.md): best variant `v1_spec` at 100%; runs live in `agents/beam-free/runs/`
- [big-pickle](agents/big-pickle/REPORT.md): best variant `v1_spec` at 100%; runs live in `agents/big-pickle/runs/`
- [crouton-alpha-free](agents/crouton-alpha-free/REPORT.md): best variant `v1_spec` at 100%; runs live in `agents/crouton-alpha-free/runs/`
- [deepseek-v4.1-flash-free](agents/deepseek-v4.1-flash-free/REPORT.md): best variant `v1_spec` at 100%; runs live in `agents/deepseek-v4.1-flash-free/runs/`
- [flint-40b-free](agents/flint-40b-free/REPORT.md): best variant `v0_brief` at 76%; runs live in `agents/flint-40b-free/runs/`
- [glm-5.3-flash-free](agents/glm-5.3-flash-free/REPORT.md): best variant `v1_spec` at 100%; runs live in `agents/glm-5.3-flash-free/runs/`
- [mimo-v2.6-flash-free](agents/mimo-v2.6-flash-free/REPORT.md): best variant `v1_spec` at 100%; runs live in `agents/mimo-v2.6-flash-free/runs/`
- [nemotron-3.5-lightning-free](agents/nemotron-3.5-lightning-free/REPORT.md): best variant `v1_spec` at 96%; runs live in `agents/nemotron-3.5-lightning-free/runs/`
- [nemotron-3.5-super-vl-free](agents/nemotron-3.5-super-vl-free/REPORT.md): best variant `v1_spec` at 97%; runs live in `agents/nemotron-3.5-super-vl-free/runs/`
- [pulse-alpha-free](agents/pulse-alpha-free/REPORT.md): best variant `v2_spec_verify` at 100%; runs live in `agents/pulse-alpha-free/runs/`

## 8. Method

- Tasks (`harness/tasks/`): `t1_slugify` (spec compliance / pure function); `t2_bugfix` (debugging existing code / not breaking tests); `t3_todo_cli` (agentic build / exact I-O contract); `t4_scheduler` (algorithms / edge cases); `t5_refactor` (refactoring / constraint following / preserving behaviour)
- Prompt variants are ordered lists of components (`harness/prompts.py`); per-model custom variants live in `agents/<model>/prompts/variants.json`.
- Loop: run variant -> score with hidden tests -> read transcripts and failure modes -> write a targeted variant -> rerun. Iteration 1 is the broad sweep; later iterations are per-model refinements.
- Each run folder holds `prompt.txt`, `events.jsonl` (raw model/tool stream), `tools.jsonl`, `pytest_output.txt`, `result.json` and the workspace `ws/`.
- Regenerate with `python harness/make_reports.py`; rerun with `python harness/run_eval.py --iter N --variants ...`.
