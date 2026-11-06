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
