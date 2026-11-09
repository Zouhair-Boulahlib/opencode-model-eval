#!/usr/bin/env bash
# Waits for the iteration-1 harness to exit, then runs iteration 3 (repo task, with/without graph)
# and iteration 2 (targeted per-model variants). One harness at a time: 2 workers, quota gate on.
cd "$(dirname "$0")/.." || exit 1  # run in repo root
export PYTHONIOENCODING=utf-8
until grep -q "ITER1 RESUME3 EXIT" results/iter1.log; do sleep 20; done
echo "=== ITER3 start $(date) ===" >> results/iter3.log
python harness/run_eval.py --iter 3 --models beam-free big-pickle crouton-alpha-free deepseek-v4.1-flash-free flint-40b-free glm-5.3-flash-free mimo-v2.6-flash-free nemotron-3.5-lightning-free nemotron-3.5-super-vl-free --tasks t6_repo_bugfix --variants g0_spec_env g1_spec_env_graph \
  --order model --workers 2 --timeout 480 --probe-first >> results/iter3.log 2>&1
echo "ITER3 EXIT $?" >> results/iter3.log
echo "=== ITER2 start $(date) ===" >> results/iter2.log
# flint: tool-reliability variants on its slow/failing tasks
python harness/run_eval.py --iter 2 --models flint-40b-free --tasks t3_todo_cli t4_scheduler t5_refactor \
  --variants m_flint_env_tool m_flint_env_tool_verify --order model --workers 2 --timeout 480 >> results/iter2.log 2>&1
# nemotron pair: examples + env + exact types, and env + edge-case walkthrough, on the tasks the spec did not fix
python harness/run_eval.py --iter 2 --models nemotron-3.5-lightning-free nemotron-3.5-super-vl-free --tasks t2_bugfix t3_todo_cli \
  --variants v10_spec_examples_env v11_spec_env_edge --order model --workers 2 --timeout 480 >> results/iter2.log 2>&1
# ceiling models: can a verify loop rescue a lazy one-line prompt? (slugify + scheduler have inferable rules)
python harness/run_eval.py --iter 2 --models beam-free big-pickle crouton-alpha-free deepseek-v4.1-flash-free glm-5.3-flash-free mimo-v2.6-flash-free \
  --tasks t1_slugify t4_scheduler --variants v6_brief_verify --order model --workers 2 --timeout 420 >> results/iter2.log 2>&1
echo "ITER2 EXIT $?" >> results/iter2.log
python harness/make_reports.py >> results/iter2.log 2>&1
echo "QUEUE DONE $(date)" >> results/iter2.log
