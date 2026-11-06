_Iteration 1 complete (15 runs). Iteration 2/3 pending._

**Style.** Reads first, writes once, checks once; 15 to 44 s per task with the spec. Short factual summaries (about 70 characters).

**Scores.** Brief 66% (lowest of the ceiling group) -> spec 100% on everything. The brief loss was almost entirely one representation choice: scheduler 9/22 because it returned lists `[480, 1020]` where the tests expected tuples. The spec says "tuple" and the problem vanished (22/22, 21 s).

**Quirks observed.**
- Sensitive to unstated representation details (types, file names: `tasks.json` instead of `todo.json`, `Added task 1:` instead of `Added 1:`).
- Spec + verify costs little here (30 s vs 27 s) but adds nothing.

**Recommendation.** State types and names exactly, in the prompt; this model follows them precisely when told and guesses differently from the tests when not. Examples of exact outputs are probably worth more than process instructions (tested in iteration 2 only if quota allows).
