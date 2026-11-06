# Getting the most out of OpenCode's free models: prompting and graph-engineering guide

This guide turns the measurements in [REPORT.md](REPORT.md) and [results/FINDINGS.md](results/FINDINGS.md)
into something you can apply. Everything in sections 1 to 3 is backed by the iteration-1 data
(125 runs, 10 models, 5 tasks, 3 prompt variants). Section 4 (graph engineering) describes the setup;
its effect is measured in iteration 3, which is queued, and the guide says so where a claim is still a hypothesis.

## 1. The recipe, in order of impact

1. **Write the contract, not the wish.** From a one-line prompt the ten models average 73%. With a full
   specification seven of ten reach 100% on every task. The lift came from details, not from logic:
   exact file names, function signatures, parameter names, return types ("tuples, not lists" alone was
   worth 13 of 22 tests for one model), verbatim output strings, and the edge cases. If a program or a
   test will parse the output, quote the literal string in the prompt.
2. **Provide the tests you have.** On the one task that shipped with tests, nine of ten models were
   perfect from a one-line prompt. Asking the model to write and run its own tests ("do not stop until
   green") changed the score in only 3 of 25 paired cells (one timeout rescue, one +1, one -1) and cost a median 30% more wall time.
3. **Skip process scaffolding on small tasks.** Plan-first, role lines and verify loops added steps and
   wall time without changing results for the seven models that reach the ceiling. Keep guard rails
   only for the models that need them (section 3).
4. **State the environment, especially on Windows.** Three models wasted minutes assuming Linux paths,
   using unquoted paths containing a space, or searching the whole filesystem. One clause fixes the
   assumption: *you are already in the project directory; the directory may be empty; use relative
   paths; do not look outside it.*
5. **Pick the model by cost once correctness is tied.** With the full spec, four models reach 100% in
   under 35 seconds per task (big-pickle 23 s, crouton 27 s, deepseek 29 s, pulse 34 s). glm takes 54 s,
   mimo 125 s. nemotron-lightning (162 s) and flint (269 s) are slow and less reliable.

## 2. A prompt template you can copy

```text
Environment: you are already inside the project directory on Windows (Git Bash shell, Python 3.13
available as `python`). The directory may be empty; if a file does not exist, create it. Use relative
paths only, never `cd` to absolute paths, and do not look at or search any directory outside the
current one.

Create `<file>.py` in the current directory containing exactly:

    def <name>(<params with types>) -> <return type>

Rules, applied in this order:
1. <rule>
2. <rule>
...
Edge cases: <input> -> <output>; <input> -> <output>.

Examples (input -> output):
- <call> -> <exact result>

Create or modify ONLY the file(s) named above, with exactly those names. Use only the standard library.
```

Add these blocks only when they earn their place:

- **Provided tests exist:** "Run `python -m pytest -q` before you finish; do not modify the tests."
- **The model is flint-40b:** "The write tool takes exactly two arguments, `filePath` and `content`; the
  read tool takes `filePath`. If a tool call is rejected for invalid arguments, fix the argument names
  instead of retrying the same call."
- **The model is a nemotron:** add worked examples that exercise every stated rule, including the one
  that looks obvious. Both nemotrons ignored an explicit "ids are never reused" rule in every run.
- **Exact-output task:** paste the literal strings and exit codes. Every model built a working todo CLI
  from a one-line prompt and every one scored 0/16 because each invented its own output format.

The component texts used in the study are in `harness/prompts.py` (`env`, `files_exact`, `types_exact`,
`toolhint`, `edge`, `verify`, `contract`, `plan`, `role`).

## 3. Per-model cards

| model | with the full spec | what to add or avoid |
|---|---|---|
| big-pickle | 100% in 23 s avg, 3 to 7 steps | Spec only. Cheapest path to the ceiling. |
| deepseek-v4.1-flash | 100% in 29 s, 3 to 5 steps, zero tool errors in 15 runs | Spec only. |
| crouton-alpha | 100% in 27 s | State types and names explicitly; it follows them exactly and guesses differently when not told. |
| pulse-alpha | 100%; best from vague prompts (79%) | Spec only; tolerates under-specification best. |
| beam-free | 100% in 52 s; two-word final messages | Spec only; ask for a specific summary format if you need one. Searched the whole disk from a vague prompt. |
| glm-5.3-flash | 100% in 54 s | List the edge cases; avoid the verify loop (it doubles wall time). |
| mimo-v2.6-flash | 100% in 125 s, fewest steps | Spec only; do not force iteration, it deliberates per step. |
| nemotron-super-vl | 97% in 42 s | Worked examples for every stated rule; it reuses ids after remove/clear. |
| nemotron-lightning | 96% in 162 s, 15 to 33 tool calls | Environment clause (assumes `/workspace`, unquoted paths), examples, rule walkthrough. Verify loop did not help. |
| flint-40b | 100% ceiling, 269 s, two 7-minute timeouts | Tool-argument hint, environment clause, exact-files rule. Avoid for anything time-sensitive. |

Full behaviour reports with transcripts: `agents/<model>/REPORT.md` and `agents/<model>/notes.md`.

## 4. Graph engineering: giving the models a map with graphify

### Why

The measured failure mode of these models is orientation, not reasoning. When a prompt left them without
context they explored: `find /` and `grep -rl /` over the whole disk (beam, flint), listing the
filesystem root and mounts for seven minutes (flint), guessing `/workspace` (nemotron-lightning).
Exploration is where steps, tokens and free-tier quota go. An architecture map hands them the
orientation up front.

[graphify](https://github.com/safishamsi/graphify) builds a knowledge graph of a codebase (AST for code,
plus docs) with community detection and writes `graphify-out/GRAPH_REPORT.md`: god nodes (the most
connected symbols), communities with labels, surprising cross-module connections, and suggested
questions. For the repo task in this study the report already names the bug's neighbourhood: it lists
`to_minor_units()` as the bridge between the currency module and the importers, which is exactly the
call the buggy CSV importer is missing.

### Three ways to wire it into opencode

**A. Static map in every session (simplest).** Build once, then load the report as ambient instructions
from the repo's `opencode.json`:

```bash
graphify .            # or /graphify . inside Claude Code; writes graphify-out/GRAPH_REPORT.md
```

```json
{
  "$schema": "https://opencode.ai/config.json",
  "instructions": ["graphify-out/GRAPH_REPORT.md"]
}
```

Keep it current with `graphify . --update` after changes, or `graphify . --watch` to rebuild
automatically (code-only corpora need no LLM for the rebuild).

**B. Live graph tools the model can call.** graphify ships an MCP server and opencode mounts MCP
servers, so the model can query the graph instead of grepping:

```json
{
  "mcp": {
    "graphify": {
      "type": "local",
      "command": ["graphify", ".", "--mcp"],
      "enabled": true
    }
  }
}
```

Check the exact keys against `opencode mcp --help` for your version. Weaker models will not use a tool
they are not told about; add one line to the prompt: "Before editing, ask the graphify tools which
modules relate to the task."

**C. Per-task injection (what the harness does).** Query the graph for the task and paste the answer
into the prompt as a "relevant code map" block:

```bash
graphify query "<the task in one sentence>" --budget 1500
```

This keeps the prompt small, which also matters on a quota. In this repository the `graph` prompt
component (`harness/prompts.py`) injects `GRAPH_REPORT.md`, truncated to about 9,000 characters, with a
one-line instruction to use it instead of reading everything. The variants `g0_spec_env` (no map) and
`g1_spec_env_graph` (map) differ only in that block.

### What to expect, and what is still unmeasured

- On a small repo (the task here is 17 files, about 500 lines) a model can read everything in a dozen
  calls, so the expected effect of the map is fewer steps, fewer tool calls and less wall time at the
  same score, rather than a higher score. On a large repo the map is more likely to change the outcome.
- Iteration 3 runs the repo task for all ten models with and without the map (20 runs). Until it has
  run, treat the above as the hypothesis under test, not as a result.
- The graph has honesty limits of its own: the health check reported 29 dangling-endpoint edges
  (standard-library names with no node) and 27 collapsed parallel edges. It is a map, not the territory.

## 5. Windows and opencode specifics that bit us

- `opencode run` takes its session directory from the `PWD` environment variable, not the real cwd.
  Scripts that spawn it must set `PWD` and pass `--dir`, or files land in the parent shell's directory.
- A workspace path containing a space breaks models that build shell commands by concatenation.
  Keep project paths free of spaces, or include the environment clause.
- A project-level `opencode.json` with `"permission": {"external_directory": "deny"}` blocked every
  attempted read outside the workspace in this study; directory listings through bash are not blocked.
- Pin the model and disable providers you do not want touched, per project:
  `"model": "opencode/<name>", "small_model": "opencode/<name>", "disabled_providers": ["ollama"]`.

## 6. The free-tier quota

- The `opencode/*` free models share one allowance per account or IP, roughly 45 agentic runs in this
  study, in a daily window that resets at midnight local time (23:00 UTC).
- When it is exhausted the endpoint answers HTTP 429 with a `Retry-After` header in seconds, but
  `opencode run` hangs without output instead of exiting. `python harness/quota_probe.py` reads the header
  and prints the reset time; `--watch` sleeps until then. The harness pauses all workers on a zero-event
  run and resumes when a probe succeeds.
- Other providers plug in the same way: any provider in the models.dev catalog (for example NVIDIA NIM
  at build.nvidia.com with `NVIDIA_API_KEY`, 25 tool-capable models) works as `provider/model` once its
  key is configured with `opencode providers login`. The harness accepts extra ids in
  `harness/models_extra.json`.
