_Iteration 1 complete (12 runs). Iteration 2 targets it specifically._

**Style.** The weakest and noisiest model: brief 61% (slugify 15/22, scheduler 11/22). 11 to 21 steps per run, 13 to 32 tool calls, 2 to 4 tool errors per run, long marketing-style summaries ("The todo app is complete and working").

**Scores.** The spec lifts it a lot (slugify 22/22, scheduler 22/22, refactor 12/12) but not to the ceiling: bug-fix 15/16 (search must also match tags, it matched names only) and todo 14/16. Spec + verify did not help: todo 13/16 after 283 s, bug-fix 16/16 after 143 s and 24 tool calls.

**Quirks observed.**
- Assumes a Linux container: tried `/workspace/scheduler.py`, `/home/USER/...`, and `cat > /todo.py` at the filesystem root before discovering the real directory with `pwd`.
- Unquoted absolute paths containing a space (`cd C:\Users\...\eval opencode\...`) get blocked by the permission system (8 blocked bash calls); it then skips testing instead of fixing the quoting.
- Ignores an explicitly stated rule: both todo runs reuse ids after `remove`/`clear` although the spec says ids are never reused. nemotron-super-vl fails the exact same two tests, so this looks like a family trait.
- Spec todo run: 33 steps and 32 tool calls, the most thrashing of any run in the study.

**Recommendation.** Spell out the environment (already in the working directory, relative paths, quote paths), give worked examples of the exact outputs including the "never reuse ids" case, and ask it to walk through each rule explicitly. Iteration 2 tests `v10_spec_examples_env` and `v11_spec_env_edge` on the two tasks it still fails. Do not rely on a verify loop: it ran tests and still shipped the id bug.
