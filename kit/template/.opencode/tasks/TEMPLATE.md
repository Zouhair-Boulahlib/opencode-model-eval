# Task: <short title>

<!-- Copy this file to .opencode/tasks/<name>.md and fill every section. The sections mirror the
     prompt components that reached 100% in the eval study: contract, examples, edge cases, verification. -->

## Goal (one paragraph)

<What must be true when the task is done, in plain words.>

## Files

- Create: `<path/to/new_file.py>`
- Modify: `<path/to/existing.py>` (only the parts listed below)
- Do not touch: `tests/`, `<anything else>`

## Contract

<Exact signatures, parameter names, return types, output strings, exit codes. Quote literal strings.>

    def example(items: list[tuple[int, int]], limit: int | None = None) -> list[tuple[int, int]]

Rules, applied in this order:
1. <rule>
2. <rule>

## Examples (input -> output)

- `example([(1, 3), (3, 5)])` -> `[(1, 5)]`
- `<command>` -> `<exact stdout>` (exit 0)

## Edge cases

- <empty input> -> <result>
- <boundary condition> -> <result>

## Verification

- Run: `python -m pytest tests -q` (or the project's command). Expected: all green.
- Do not add dependencies. Do not modify existing tests.

## Context hints (optional)

<Modules or symbols to start from, taken from `python scripts/task_context.py --query "<goal>"`.>
