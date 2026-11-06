# OpenCode free models: an evaluation-driven prompting study

This repository evaluates the 10 free hosted models that ship with [OpenCode](https://opencode.ai) (the
`opencode/*` models, driven through `opencode run`) on small coding tasks. Each model works in its own isolated
folder and is scored with hidden pytest suites on 5 coding tasks and 3 prompt variants, which gives 125 valid runs
in iteration 1. Every run keeps its full prompt, raw event stream, tool-call log, hidden-test output and final
workspace. The data is turned into per-model behaviour reports and a prompting recipe per model. Everything ran on
Windows 11 (Git Bash shell, Python 3.13), including a Windows path that contains a space. The local Ollama model
is deliberately excluded.

The method is a loop: run a prompt variant, score it with hidden tests, read the transcripts for failure modes,
write a targeted variant for that model, and rerun.

## Headline findings

All numbers come from [`REPORT.md`](REPORT.md) and [`results/FINDINGS.md`](results/FINDINGS.md).

- **The specification is the trick.** From a one-line prompt the ten models average 73% (range 61% to 79%). With the
  full specification (file names, signatures, types, verbatim output strings, edge cases) seven of ten reach 100% on
  every task they ran and the other three reach a 96% to 100% ceiling. In the paired comparison the spec beats the
  one-line brief by +28.5 points on average, and all 10 models improve.
- **The biggest lifts were representation details, not logic.** crouton lost 13 of 22 scheduler tests by returning
  lists instead of tuples, and every model lost all 16 todo-CLI tests by inventing its own output format. The spec
  removed both. Spec runs were also about as fast as or faster than brief runs for the fast models (big-pickle 29 s to
  23 s, deepseek 27 s to 29 s, crouton unchanged), because the model stops guessing.
- **The self-verify loop bought nothing.** Asking the model to write tests, run pytest and not stop until green left
  the score identical in every paired cell except one flint run, where a retry recovered a timed-out spec run (a
  reliability effect, not a prompt effect). Every model complied and paid +30% to +150% wall time and about +40%
  steps. Where tests were provided (the bug-fix task), nine of ten models were perfect from a one-line prompt.
- **Models differ far more in process than in result.** Five models are one-shot (3 to 6 steps, no wasted calls),
  three look around first and edit surgically, and two thrash (15 to 33 tool calls, repeated tool errors).
  Only flint has broken tool calling; only nemotron-lightning assumed Linux paths; both nemotrons ignored an
  explicitly stated rule (ids never reused), even after writing and running their own tests.
- **The environment clause matters on Windows.** The two slowest models account for 17 blocked bash calls each
  (unquoted path) and 6.36 (flint) and 2.33 (nemotron-lightning) tool errors per run, against 0.00 to 0.20 for the
  rest. A short "you are already in the project directory, use relative paths, quote paths" clause is the proposed
  fix; testing it is part of iteration 2.
- **Choose by cost when correctness is tied.** With the spec, big-pickle (23 s), crouton (27 s), deepseek (29 s) and
  pulse (34 s) reach the ceiling fastest. glm (54 s) and mimo (125 s) are slower; nemotron-lightning (162 s) and
  flint (269 s) are slow and less reliable.
- **Skip scaffolding on single-file tasks.** Plan, verify and role scaffolding is unnecessary for the ceiling
  models (big-pickle, deepseek, pulse, beam, mimo, glm, crouton); keep guard rails for flint and the nemotrons.

### Leaderboard (best prompt variant per model)

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

Cells with fewer than all tasks exist because adaptive mode skips a variant on a task whose cheaper predecessor
already scored 100%. The ceiling column (best result per task) is the fairest cross-model comparison.
`REPORT.md` also has the model by variant score matrix, the per-task scores, the paired value of each prompting
trick and a behaviour profile per model.

## What is in this repository

```
README.md                      this file
REPORT.md                      main report: leaderboard, score matrices, trick effects, behaviour profiles, findings
LICENSE                        MIT
results/
  FINDINGS.md                  hand-written findings, merged into REPORT.md
  summary.csv                  one row per valid run (125 rows): score, wall time, steps, tool calls, tokens, flags
  runs.jsonl                   append-only log with the full metrics of every attempt (includes redone runs)
  iter1.log, iter3.log         harness logs (iter3.log shows the harness waiting on the free-tier quota)
agents/<model>/                one isolated space per model (10 folders)
  opencode.json                pins the model, disables Ollama, denies web and question tools
  REPORT.md                    generated per-model report: scores, behaviour profile, recommended prompt
  notes.md                     hand-written behaviour notes merged into the report
  prompts/variants.json        model-specific prompt variants (empty for most models)
  runs/iter<N>/<task>/<variant>/
    prompt.txt                 exact prompt sent
    events.jsonl               raw JSON event stream from `opencode run --format json`
    tools.jsonl                one line per tool call (name, input summary, status)
    pytest_output.txt          hidden-test output (junit.xml has the same in XML)
    result.json                all metrics for this run
    stderr.txt                 opencode stderr
    ws/                        the workspace the model worked in
harness/
  run_eval.py                  runner: isolated workspaces, parallel workers, quota gate, hidden-test scoring
  make_reports.py              regenerates REPORT.md and agents/<model>/REPORT.md from result.json files
  prompts.py                   prompt components and variants
  inspect_run.py               readable transcript of one run folder
  qc_scan.py                   integrity and leakage scan over all runs
  quota_probe.py               checks the free-tier quota and the reset time without launching opencode
  anonymize.py                 replaces the machine user name in text files with USER
  queue_after_iter1.sh         waits for iteration 1, then runs iterations 3 and 2
  tasks/<task>/                spec.md, brief.txt, examples.md, starter/ files, hidden/ tests, task.json
  reference/<task>/            reference solutions, used by --selftest to validate the hidden tests
```

The ten models are `beam-free`, `big-pickle`, `crouton-alpha-free`, `deepseek-v4.1-flash-free`, `flint-40b-free`,
`glm-5.3-flash-free`, `mimo-v2.6-flash-free`, `nemotron-3.5-lightning-free`, `nemotron-3.5-super-vl-free` and
`pulse-alpha-free`, each addressed as `opencode/<name>`.

## The tasks

Each task has a one-line brief, a full specification, starter files and a hidden pytest suite. A score is the
fraction of hidden tests passed; a run that edits a protected test file scores 0.

| task | what the model does | skill tested | hidden tests |
|---|---|---|---|
| `t1_slugify` | Implement slugify() to spec | spec compliance / pure function | 22 |
| `t2_bugfix` | Fix 5 bugs in inventory.py so the tests pass | debugging existing code / not breaking tests | 16 |
| `t3_todo_cli` | Build a todo CLI with JSON persistence | agentic build / exact I-O contract | 16 |
| `t4_scheduler` | Interval scheduler utilities | algorithms / edge cases | 22 |
| `t5_refactor` | Refactor legacy process_orders under hard constraints | refactoring / constraint following / preserving behaviour | 12 |
| `t6_repo_bugfix` | Repo-scale root-cause bug fix across modules (ledger) | codebase navigation / root-cause debugging across files | 14 |

`t1` to `t5` make up iteration 1. `t6_repo_bugfix` is built for iteration 3 and has not been run yet.

## Prompt variants

A variant is an ordered list of components, assembled by `harness/prompts.py`. Three components are task-specific
and read from `harness/tasks/<task>/`: `brief` (one-line prompt), `spec` (full specification) and `examples`
(worked examples); a fourth, `graph`, loads the graphify architecture report for the repo-scale task.

Fixed-text components:

| component | what it adds |
|---|---|
| `role` | "senior Python engineer" persona |
| `plan` | write a numbered plan of at most 5 short steps first |
| `verify` | write test_own.py (or use provided tests), run pytest, fix until green, quote the pytest summary |
| `contract` | work only in the current directory, standard library only, no questions, do not touch provided tests, short summary |
| `edge` | walk through every rule and edge case in the spec one by one before finishing |
| `readfirst` | list and read every file in the directory before changing anything |
| `nofluff` | no commentary, 3-line summary at the end |
| `oneshot` | write the complete file in a single write, run the tests once |
| `files_exact` | create or modify only the named files, with exactly those names |
| `env` | Windows environment clause: already in the project directory, Git Bash, relative paths only, directory may be empty |
| `toolhint` | exact argument names of the write and read tools (`filePath`, `content`) |
| `types_exact` | return tuples where tuples are specified, use exact names and output strings |

Variants (global ones in `harness/prompts.py`; per-model ones in `agents/<model>/prompts/variants.json`):

- `v0_brief`: brief
- `v1_spec`: spec
- `v2_spec_verify`: spec, verify
- `v3_spec_plan_verify`: spec, plan, verify
- `v4_spec_contract`: spec, contract
- `v5_full`: role, spec, examples, plan, verify, contract
- `v6_brief_verify`: brief, verify
- `v7_spec_examples`: spec, examples
- `v8_spec_examples_verify_contract`: spec, examples, verify, contract
- `v9_spec_env_verify`: env, spec, verify (iteration-2 candidate)
- `v10_spec_examples_env`: env, spec, examples, types_exact (iteration-2 candidate)
- `v11_spec_env_edge`: env, spec, edge (iteration-2 candidate)
- `g0_spec_env`: env, spec (iteration 3, no architecture map)
- `g1_spec_env_graph`: env, spec, graph (iteration 3, with a graphify architecture map)
- `m_flint_env_tool`, `m_flint_env_tool_verify`: flint-specific variants

Iteration 1 used `v0_brief`, `v1_spec` and `v2_spec_verify`; the others are built for iterations 2 and 3.

## Reproduce

Requirements: Windows (or any OS with a bash-compatible shell), Python 3.13 with `pytest`, and OpenCode 1.19.x
installed and on the path. No API keys are needed for the free models. Each `agents/<model>/opencode.json` pins its
model, disables the local Ollama provider and denies web and question tools, and `external_directory: deny` blocks
reads outside the workspace.

```
# score the reference solutions (expected 100%) and the bare starter files with the hidden tests
python harness/run_eval.py --selftest

# iteration 1: the broad sweep (adaptive mode skips a variant when the cheaper one already scored 100%)
python harness/run_eval.py --iter 1 --variants v0_brief v1_spec v2_spec_verify --workers 2 --adaptive --order model --probe-first

# regenerate REPORT.md and every agents/<model>/REPORT.md
python harness/make_reports.py

# read one run as a transcript (add --full for untruncated output)
python harness/inspect_run.py agents/big-pickle/runs/iter1/t1_slugify/v1_spec

# check the free-tier quota and when it resets
python harness/quota_probe.py
```

Useful runner flags: `--tasks`, `--models`, `--reps`, `--timeout`, `--force`, `--dry-run`, `--redo-infra`,
`--order {variant,model}`, `--probe-first` and `--adaptive`. A targeted per-model rerun looks like
`python harness/run_eval.py --iter 2 --models <model> --variants <variant> --tasks <task>`.
After producing new transcripts on your own machine, `python harness/anonymize.py` replaces the local user name
(edit the name in that script first).

## Free-tier quota and operational notes

- The hosted free tier allows roughly 45 runs per window. After that every `opencode/*` model fails with "Free usage
  limit reached" and `opencode run` hangs with zero events instead of exiting. Observed resets came after about
  3.5 h and about 13 h; the current window resets at local midnight, and `quota_probe.py` prints the announced reset
  time.
- The harness treats zero-event runs as infrastructure failures: it pauses all workers, probes every 5 minutes and
  resumes automatically. Such attempts are redone, which is why `runs.jsonl` has more lines than `summary.csv`.
- `opencode run` takes its session directory from the `PWD` environment variable, not the process working
  directory. Scripts must set `PWD` and pass `--dir`, otherwise files land in the parent shell's directory.
- Isolation rule: the per-agent `external_directory: deny` blocked every attempted read outside a workspace (flint
  tried its own prompt file and another run's source); directory listings are not blocked. No hidden-test content
  reached any model, which `harness/qc_scan.py` verifies.

## Status

- Iteration 1 is complete: 125 valid runs (10 models x 5 tasks x up to 3 prompt variants; adaptive mode skipped 25
  runs whose cheaper variant already scored 100%).
- Iteration 2 (targeted per-model variants) is built and queued: flint tool-reliability variants, environment and
  edge-case variants for the nemotron pair, and a verify loop on a one-line prompt for the ceiling models.
- Iteration 3 (repo-scale bug fix, `t6_repo_bugfix`, with and without a graphify architecture map in the prompt)
  is built and queued.
- Both are waiting on the free-tier daily quota. Their results will be appended to `REPORT.md` and
  `results/FINDINGS.md` when they run.

## Caveats

- One run per cell: there are no repetitions, so small differences between cells are within noise. The spec versus
  brief gap is large and consistent across all 10 models; fine ranking among models at 100% is not supported.
- The Windows path containing a space is part of the environment under test, and some failures (blocked unquoted
  paths) are specific to it.
- The todo-CLI brief is a floor effect: with no output format given, every model scored 0 of 16 from the one-line
  prompt, so that cell measures guessing the format rather than coding ability.
- The hidden tests are public in this repository (`harness/tasks/*/hidden/`). If you reuse the tasks, treat them as
  no longer hidden.
- Machine paths in the transcripts and logs were replaced by `USER` with `harness/anonymize.py`; commands and
  outputs in `events.jsonl` otherwise appear as they were produced.
- Results describe the free-tier models as served at the time of the runs and may change.

## License

MIT. See [`LICENSE`](LICENSE).
