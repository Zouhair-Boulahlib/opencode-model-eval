_Iteration 1 complete (11 runs, adaptive skips). Iteration 2 targets it specifically._

**Style.** Very few steps (2 to 6), writes once and checks once, "Done." plus a bullet list (about 200 to 350 characters). Fast: about 40 s per task on every variant.

**Scores.** Brief 73% -> spec 97%: slugify 18 -> 22/22, scheduler 20 -> 22/22, refactor 11 -> 12/12, todo 0 -> 14/16. Spec + verify did not move the todo result (14/16 again).

**Quirks observed.**
- Both todo runs fail `test_ids_never_reused_after_remove` and `..._after_clear`: it computes the next id from the current maximum instead of keeping a counter, despite the spec saying ids are never reused. Same miss as nemotron-lightning.
- Brief slugify: kept separator-only and non-ASCII input instead of returning "".

**Recommendation.** Spec plus worked examples that show the tricky rule in action (`remove 2` then `add` -> `Added 3`), or an explicit "walk through every rule" instruction. Iteration 2 tests both. Verify loops are not the fix here.
