# Graph Report - starter  (2026-11-06)

## Corpus Check
- Corpus is ~1,939 words - fits in a single context window. You may not need a graph.

## Summary
- 123 nodes · 297 edges · 7 communities
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 24 edges (avg confidence: 0.93)
- Token cost: 53,656 input · 0 output

## Community Hubs (Navigation)
- File Importers (CSV/JSON/QIF)
- Budgets, Models and Utils
- CLI and Currency Conversion
- JSON Storage and Monthly Totals
- Transaction Model and Reporting
- README Concepts and Currencies
- Data File Resolution

## God Nodes (most connected - your core abstractions)
1. `Transaction` - 31 edges
2. `monthly_totals()` - 13 edges
3. `to_major_units()` - 12 edges
4. `import_json()` - 12 edges
5. `main()` - 11 edges
6. `to_minor_units()` - 11 edges
7. `import_csv()` - 10 edges
8. `category_breakdown()` - 9 edges
9. `upsert()` - 9 edges
10. `parse_date()` - 8 edges

## Surprising Connections (you probably didn't know these)
- `test_monthly_total_jpy_from_json()` --calls--> `import_json()`  [EXTRACTED]
  tests/test_reports.py → ledger/importers/json_importer.py
- `budget_usage()` --uses--> `Transaction`  [INFERRED]
  ledger/budgets.py → ledger/models.py
- `main()` --indirect_call--> `import_json()`  [INFERRED]
  ledger/cli.py → ledger/importers/json_importer.py
- `main()` --indirect_call--> `import_qif()`  [INFERRED]
  ledger/cli.py → ledger/importers/qif_importer.py
- `to_csv()` --uses--> `Transaction`  [INFERRED]
  ledger/export.py → ledger/models.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Ledger data pipeline: import -> JSON store -> reports, all in minor-unit integers** — readme_transaction_import, readme_json_file_storage, readme_monthly_category_reports, readme_minor_unit_integer_amounts [INFERRED 0.85]
- **Currencies with differing minor-unit exponents (USD=2, JPY=0, KWD=3) sharing one integer representation** — readme_currency_usd, readme_currency_jpy, readme_currency_kwd, readme_minor_unit_integer_amounts [EXTRACTED 1.00]

## Communities (7 total, 0 thin omitted)

### Community 0 - "File Importers (CSV/JSON/QIF)"
Cohesion: 0.14
Nodes (24): datetime, Runtime configuration resolved from environment variables., CSV importer. Expected columns: date, description, amount, category (optional),…, _row_to_transaction(), Importers turn external files into Transaction objects (not yet stored)., import_json(), Path, JSON importer for the exchange format used by the mobile app: {"currency":… (+16 more)

### Community 1 - "Budgets, Models and Utils"
Cohesion: 0.12
Nodes (16): dataclasses, decimal, hashlib, itertools, Budget, budget_usage(), Monthly budgets per category and how much of them is used., Percent (0-100+) of each budget consumed in the given 'YYYY-MM' month. (+8 more)

### Community 2 - "CLI and Currency Conversion"
Cohesion: 0.16
Nodes (16): argparse, csv, io, Command line entry point: python -m ledger.cli <command> ..., exponent(), format_amount(), Decimal, Currency helpers. The number of minor-unit digits differs per currency (ISO… (+8 more)

### Community 3 - "JSON Storage and Monthly Totals"
Cohesion: 0.21
Nodes (17): json, main(), import_csv(), Path, monthly_totals(), Net total per month ('YYYY-MM'), in major units of `currency`., _from_record(), load() (+9 more)

### Community 4 - "Transaction Model and Reporting"
Cohesion: 0.21
Nodes (13): collections, A single money movement. `amount_minor` is an integer in the currency's minor…, Transaction, category_breakdown(), monthly_expenses(), _only(), Decimal, Reports over stored transactions. All money values returned as Decimal major… (+5 more)

### Community 5 - "README Concepts and Currencies"
Cohesion: 0.26
Nodes (13): JPY (minor unit: yen, exponent 0), KWD (minor unit: fils, exponent 3), USD (minor unit: cents, exponent 2), import-csv CLI command (--currency), JSON file transaction store, ledger (personal-finance ledger project), ledger.cli entry point (python -m ledger.cli), Integer amounts in currency minor unit (+5 more)

### Community 6 - "Data File Resolution"
Cohesion: 0.67
Nodes (3): data_file(), Path, Resolve the data file: explicit argument wins, then LEDGER_DATA, then…

## Knowledge Gaps
- **3 isolated node(s):** `pytest test suite (tests/)`, `JPY (minor unit: yen, exponent 0)`, `KWD (minor unit: fils, exponent 3)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 48 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Transaction` connect `Transaction Model and Reporting` to `File Importers (CSV/JSON/QIF)`, `Budgets, Models and Utils`, `CLI and Currency Conversion`, `JSON Storage and Monthly Totals`?**
  _High betweenness centrality (0.223) - this node is a cross-community bridge._
- **Why does `to_minor_units()` connect `CLI and Currency Conversion` to `File Importers (CSV/JSON/QIF)`, `Budgets, Models and Utils`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Why does `import_json()` connect `File Importers (CSV/JSON/QIF)` to `CLI and Currency Conversion`, `JSON Storage and Monthly Totals`, `Transaction Model and Reporting`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Are the 15 inferred relationships involving `Transaction` (e.g. with `budget_usage()` and `to_csv()`) actually correct?**
  _`Transaction` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `main()` (e.g. with `import_csv()` and `import_json()`) actually correct?**
  _`main()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `pytest test suite (tests/)`, `JPY (minor unit: yen, exponent 0)`, `KWD (minor unit: fils, exponent 3)` to the rest of the system?**
  _3 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `File Importers (CSV/JSON/QIF)` be split into smaller, more focused modules?**
  _Cohesion score 0.135632183908046 - nodes in this community are weakly interconnected._