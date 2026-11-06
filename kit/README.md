# Graph-engineered development kit for OpenCode

A reusable setup that turns the findings of this evaluation into a working environment for complex
development with coding agents. Drop it into any project in one command; it gives every OpenCode
session an architecture map of the codebase, three specialised agents, four slash commands, a
contract template, and a scripted runner with transcripts.

```
python kit/init_project.py /path/to/your/project            # copies the template, builds the map
python kit/init_project.py /path/to/your/project --model nvidia/minimaxai/minimax-m3.1-flash
```

## Why it looks like this

Every piece answers a measured failure from the study (see `../REPORT.md` and `../GUIDE.md`):

| finding | what the kit does about it |
|---|---|
| Models lose points on unstated details (names, types, strings), not on logic | `.opencode/tasks/TEMPLATE.md` forces a contract: files, signatures, literal strings, edge cases, verification |
| Models waste minutes exploring when they lack orientation (`find /`, listing parents, guessing `/workspace`) | `graphify-out/GRAPH_REPORT.md` is loaded into every session as ambient instructions, and `scripts/task_context.py` prints the subgraph for a task |
| Self-written tests never changed a result; provided tests did | AGENTS.md: run the provided tests, do not write your own unless asked |
| Windows paths with spaces and wrong tool-argument names cost whole runs | AGENTS.md environment rules; tool-argument reminder |
| Fast models reach the same ceiling as slow ones | navigator on the fastest model, builder on the most reliable one, reviewer on the best vague-prompt model; all free, all swappable |
| Process scaffolding (plan, verify loops) is overhead on small tasks | the navigator is a separate, optional, read-only agent instead of a plan-first instruction baked into every prompt |

## What gets installed in the project

```
AGENTS.md                         ambient rules for every session (orientation, environment, contract discipline)
opencode.json                     model, default agent, instructions = [AGENTS.md, graphify-out/GRAPH_REPORT.md], permissions
.opencode/agents/navigator.md     read-only: map + files -> plan with file paths (big-pickle, 12 steps)
.opencode/agents/builder.md       default primary agent: implements the contract (deepseek-v4.1-flash, 40 steps)
.opencode/agents/reviewer.md      read-only: diff + tests vs contract (pulse-alpha, 10 steps)
.opencode/commands/task.md        /task <name>   contract + code map -> builder
.opencode/commands/map.md         /map <question> code map for a question
.opencode/commands/graph.md       /graph         rebuild the map
.opencode/commands/review.md      /review <name> contract + diff + tests -> reviewer
.opencode/tasks/TEMPLATE.md       the contract template
scripts/graph_refresh.py          headless graphify build (AST only, no LLM, seconds)
scripts/task_context.py           subgraph printer used by /task, /map and run_task.py
scripts/run_task.py               scripted run with transcript, timeout and test command
graphify-out/                     GRAPH_REPORT.md + graph.json (rebuild after structural changes)
```

## Daily workflow

1. Write the contract: copy `.opencode/tasks/TEMPLATE.md` to `.opencode/tasks/<name>.md` and fill it.
   Literal strings for anything a program will parse. Name the files to create and modify.
2. Orient: `/map <what you are about to change>` shows the symbols, files and cross-module edges
   involved. For a bigger change, `@navigator <task>` returns a file-level plan without touching code.
3. Build: `/task <name>`. The builder gets the contract, the subgraph, and AGENTS.md, works only in the
   named files, runs the provided tests and ends with a short summary.
4. Check: `/review <name>` runs the read-only reviewer over the diff and the tests.
5. After structural changes (new modules, moved functions): `/graph`.

Scripted equivalent, for batches or CI: `python scripts/run_task.py .opencode/tasks/<name>.md`
(transcript under `.opencode/runs/`).

## Models

Defaults are the free OpenCode models that reached 100% with a spec in the study, chosen by speed:
big-pickle (23 s per task) navigates, deepseek-v4.1-flash (29 s, no tool errors in 15 runs) builds,
pulse-alpha (best from vague prompts) reviews. Change `model:` in the agent files or pass `--model`
to `init_project.py` for the project default. Any provider in the models.dev catalog works once its
key is configured (`opencode providers login`), for example `nvidia/minimaxai/minimax-m3.1-flash`.

Avoid, for anything time-sensitive: flint-40b (broken tool calling) and nemotron-3.5-lightning
(Linux-path assumptions, unquoted paths). Both are documented in `../agents/<model>/notes.md`.

## Caveats

- The free tier allows roughly 45 agentic runs per day per account; `python ../harness/quota_probe.py`
  shows when it resets. `run_task.py` stops after 300 s without any event, which is how an exhausted
  quota looks from the outside.
- The map is AST-based: imports, calls, definitions. It knows nothing about what docs say unless you
  build it with the full `/graphify` skill, which adds semantic extraction.
- Slash-command templates use OpenCode's `!`command`` and `@file` substitutions; check
  `opencode --version` is 1.19 or later if a command prints the raw template.
- The effect of the map on complex tasks is measured in iteration 3 of the study; until those runs
  complete, the orientation benefit is the hypothesis the kit is built on, not a settled number.
