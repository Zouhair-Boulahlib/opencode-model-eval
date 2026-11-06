_Iteration 1 complete (15 runs). Iteration 2/3 pending._

**Style.** The most economical model in the set: 3 to 7 steps per task, one `write` then one or two bash checks, 23 s average with the full spec. Summaries are one dense paragraph with file:line references and an explicit list of what changed.

**Scores.** Brief 77% -> spec 100% on all five tasks. The spec runs were *faster* than the brief runs (23 s vs 29 s) because it stops guessing. Spec + verify: still 100%, wall 42 s, steps 6.4 (vs 4.2).

**Quirks observed.**
- Brief todo: `Added task 1: buy milk` and a padded table layout, storage in `tasks.json`. Works, wrong contract.
- Brief refactor: produced a 24-line function (limit 20), everything else right.

**Recommendation.** Spec only. This is the model to use when latency and quota matter: it reached the ceiling on every task at the lowest cost in the group. Skip plan-first and verify instructions; they only add steps.
