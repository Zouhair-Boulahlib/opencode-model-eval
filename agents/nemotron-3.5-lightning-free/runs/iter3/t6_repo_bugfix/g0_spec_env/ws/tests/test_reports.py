from decimal import Decimal
from pathlib import Path

from ledger import storage
from ledger.importers import import_csv, import_json
from ledger.reporting import monthly_totals

HERE = Path(__file__).resolve().parent
SAMPLES = HERE.parent / "sample_data"


def test_monthly_total_usd_from_csv(tmp_path):
    txs = import_csv(SAMPLES / "transactions_usd.csv", "USD")
    storage.upsert(tmp_path / "l.json", txs)
    totals = monthly_totals(storage.load(tmp_path / "l.json"), "USD")
    assert totals == {"2024-03": Decimal("3113.31"), "2024-04": Decimal("-1200.00")}


def test_monthly_total_jpy_from_csv(tmp_path):
    txs = import_csv(SAMPLES / "transactions_jpy.csv", "JPY")
    storage.upsert(tmp_path / "l.json", txs)
    totals = monthly_totals(storage.load(tmp_path / "l.json"), "JPY")
    assert totals == {"2024-03": Decimal("248000")}


def test_monthly_total_jpy_from_json(tmp_path):
    src = tmp_path / "in.json"
    src.write_text('{"currency": "JPY", "items": [{"date": "2024-03-01", "description": "Konbini", "amount": "-500"},'
                   ' {"date": "2024-03-02", "description": "Salary", "amount": "250000"}]}', encoding="utf-8")
    txs = import_json(src)
    totals = monthly_totals(txs, "JPY")
    assert totals == {"2024-03": Decimal("249500")}
