# ledger

A small personal-finance ledger: import transactions (CSV or JSON), store them in a JSON file,
and produce monthly / category reports. Amounts are stored as integers in the currency's minor
unit (cents for USD, yen for JPY, fils for KWD) to avoid floating point errors.

    python -m ledger.cli import-csv sample_data/transactions_usd.csv --currency USD
    python -m ledger.cli report --currency USD
    python -m pytest tests -q
