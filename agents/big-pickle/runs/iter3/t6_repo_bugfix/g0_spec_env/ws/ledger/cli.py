"""Command line entry point: python -m ledger.cli <command> ..."""
import argparse
import sys
from pathlib import Path

from . import storage
from .config import DEFAULT_CURRENCY, data_file
from .currency import format_amount, to_minor_units
from .export import to_csv
from .importers import import_csv, import_json, import_qif
from .reporting import category_breakdown, monthly_totals
from .validation import validate_all


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="ledger")
    p.add_argument("--data", help="path of the ledger JSON file")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("import-csv", "import-json", "import-qif"):
        sp = sub.add_parser(name)
        sp.add_argument("file")
        sp.add_argument("--currency", default=DEFAULT_CURRENCY)
    rp = sub.add_parser("report")
    rp.add_argument("--currency", default=DEFAULT_CURRENCY)
    sub.add_parser("export")
    a = p.parse_args(argv)
    path = data_file(a.data)

    if a.cmd.startswith("import-"):
        importer = {"import-csv": import_csv, "import-json": import_json, "import-qif": import_qif}[a.cmd]
        txs = importer(Path(a.file), a.currency)
        problems = validate_all(txs)
        if problems:
            print(f"refusing to import: {problems}", file=sys.stderr)
            return 1
        added = storage.upsert(path, txs)
        print(f"imported {added} new transaction(s) into {path}")
        return 0
    txs = storage.load(path)
    if a.cmd == "report":
        for month, total in monthly_totals(txs, a.currency).items():
            print(f"{month}  {total} {a.currency}")
        for cat, spent, pct in category_breakdown(txs, a.currency):
            print(f"  {cat:20} {spent:>12} {pct:5.1f}%")
        return 0
    if a.cmd == "export":
        sys.stdout.write(to_csv(txs))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
