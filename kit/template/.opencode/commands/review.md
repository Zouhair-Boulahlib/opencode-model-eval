---
description: Review the current changes against a task contract: /review <name>
agent: reviewer
---
Task contract:

@.opencode/tasks/$ARGUMENTS.md

Current diff:

!`git diff`

Test run:

!`python -m pytest -q 2>&1 | tail -15`

Review the changes against the contract as described in your instructions.
