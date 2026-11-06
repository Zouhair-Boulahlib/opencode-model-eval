Bug report for the `ledger` project in the current directory (pure standard library, Python 3.13):

"After importing transactions from a CSV file in a zero-decimal currency such as JPY, the monthly report totals are 100 times too large. USD and EUR CSV imports look fine, and JSON imports are fine in every currency."

`python -m pytest tests -q` reproduces it: one test in `tests/test_reports.py` fails.

Your job: find the ROOT CAUSE and fix it there. Requirements:
- Do not modify anything under `tests/`.
- Fix the cause, not the symptom: reports, storage and the JSON importer must keep their current behaviour, and three-decimal currencies (KWD) must also come out right after the fix.
- Keep the change minimal and inside the `ledger` package. Reuse the project's existing helpers instead of re-implementing conversions. Do not add dependencies.
- Finish by running `python -m pytest tests -q` and reporting the result and the file(s) you changed.
