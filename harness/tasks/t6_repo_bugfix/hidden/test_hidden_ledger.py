import json
from decimal import Decimal
from pathlib import Path

from ledger import storage
from ledger.budgets import Budget, budget_usage
from ledger.currency import to_major_units, to_minor_units
from ledger.export import to_csv
from ledger.importers import import_csv, import_json, import_qif
from ledger.models import Transaction
from ledger.reporting import category_breakdown, monthly_totals

HERE = Path(__file__).resolve().parent
SAMPLES = HERE / "sample_data"


def _csv(tmp_path, name, rows):
    p = tmp_path / name
    p.write_text("date,description,amount,category,tags\n" + "\n".join(rows) + "\n", encoding="utf-8")
    return p


# --- the reported symptom ---
def test_jpy_csv_totals(tmp_path):
    txs = import_csv(SAMPLES / "transactions_jpy.csv", "JPY")
    storage.upsert(tmp_path / "l.json", txs)
    assert monthly_totals(storage.load(tmp_path / "l.json"), "JPY") == {"2024-03": Decimal("248000")}


def test_usd_csv_totals_unchanged(tmp_path):
    txs = import_csv(SAMPLES / "transactions_usd.csv", "USD")
    assert monthly_totals(txs, "USD") == {"2024-03": Decimal("3113.31"), "2024-04": Decimal("-1200.00")}


# --- root cause: csv importer must convert with the currency exponent ---
def test_csv_import_stores_minor_units_jpy(tmp_path):
    p = _csv(tmp_path, "j.csv", ["2024-05-01,Train,-1500,transport,"])
    (tx,) = import_csv(p, "JPY")
    assert tx.amount_minor == -1500 and isinstance(tx.amount_minor, int)


def test_csv_import_stores_minor_units_kwd(tmp_path):
    p = _csv(tmp_path, "k.csv", ["2024-05-01,Souq,-12.345,food,"])
    (tx,) = import_csv(p, "KWD")
    assert tx.amount_minor == -12345


def test_csv_import_stores_minor_units_usd(tmp_path):
    p = _csv(tmp_path, "u.csv", ["2024-05-01,Shop,-12.34,food,", "2024-05-02,Pay,1000.5,income,"])
    a, b = import_csv(p, "USD")
    assert (a.amount_minor, b.amount_minor) == (-1234, 100050)


def test_csv_import_rounds_half_up_usd(tmp_path):
    p = _csv(tmp_path, "r.csv", ["2024-05-01,Odd,-0.005,misc,"])
    (tx,) = import_csv(p, "USD")
    assert tx.amount_minor == -1


# --- the symptom must not be "fixed" downstream ---
def test_reporting_unchanged_for_manual_transactions():
    txs = [
        Transaction("a", __import__("datetime").date(2024, 3, 1), "x", -500, "JPY", "food"),
        Transaction("b", __import__("datetime").date(2024, 3, 2), "y", 250000, "JPY", "income"),
        Transaction("c", __import__("datetime").date(2024, 3, 3), "z", -1234, "USD", "food"),
    ]
    assert monthly_totals(txs, "JPY") == {"2024-03": Decimal("249500")}
    assert monthly_totals(txs, "USD") == {"2024-03": Decimal("-12.34")}
    assert category_breakdown(txs, "JPY") == [("food", Decimal("500"), 100.0)]


def test_json_import_unchanged(tmp_path):
    src = tmp_path / "in.json"
    src.write_text(json.dumps({"currency": "KWD", "items": [{"date": "2024-03-01", "description": "a", "amount": "1.5"}]}), encoding="utf-8")
    (tx,) = import_json(src)
    assert tx.amount_minor == 1500 and tx.currency == "KWD"


def test_qif_import_unchanged(tmp_path):
    src = tmp_path / "in.qif"
    src.write_text("!Type:Bank\nD2024-03-01\nT-1500\nPTrain\nLtransport\n^\n", encoding="utf-8")
    (tx,) = import_qif(src, "JPY")
    assert tx.amount_minor == -1500


def test_storage_round_trip(tmp_path):
    txs = import_csv(SAMPLES / "transactions_jpy.csv", "JPY")
    storage.save(tmp_path / "l.json", txs)
    back = storage.load(tmp_path / "l.json")
    assert [t.amount_minor for t in back] == [t.amount_minor for t in txs]
    raw = json.loads((tmp_path / "l.json").read_text(encoding="utf-8"))
    assert all(isinstance(r["amount_minor"], int) for r in raw["transactions"])


def test_export_formats_by_currency(tmp_path):
    txs = import_csv(SAMPLES / "transactions_jpy.csv", "JPY")
    out = to_csv(txs)
    assert "Train,-1500,JPY" in out
    assert "-1500.00" not in out


def test_currency_helpers_unchanged():
    assert to_minor_units(Decimal("12.34"), "USD") == 1234
    assert to_minor_units(Decimal("1500"), "JPY") == 1500
    assert to_minor_units(Decimal("12.345"), "KWD") == 12345
    assert to_major_units(1234, "USD") == Decimal("12.34")
    assert to_major_units(1500, "JPY") == Decimal("1500")


def test_budget_usage_unchanged():
    import datetime as dt
    txs = [Transaction("a", dt.date(2024, 3, 1), "x", -5000, "USD", "food")]
    usage = budget_usage(txs, [Budget("food", Decimal("100.00"), "USD")], "2024-03")
    assert usage == {"food": 50.0}


def test_visible_suite_passes():
    import subprocess, sys
    r = subprocess.run([sys.executable, "-m", "pytest", "tests", "-q", "-p", "no:cacheprovider"], cwd=str(HERE),
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stdout[-800:]
