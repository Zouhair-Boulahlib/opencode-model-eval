"""Export stored transactions back to CSV (major units, like the bank exports)."""
import csv
import io

from .currency import to_major_units
from .models import Transaction

COLUMNS = ["date", "description", "amount", "currency", "category", "tags"]


def to_csv(transactions: list[Transaction]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(COLUMNS)
    for t in sorted(transactions, key=lambda t: (t.posted_on, t.id)):
        writer.writerow([t.posted_on.isoformat(), t.description, str(to_major_units(t.amount_minor, t.currency)),
                         t.currency, t.category, ";".join(t.tags)])
    return buf.getvalue()
