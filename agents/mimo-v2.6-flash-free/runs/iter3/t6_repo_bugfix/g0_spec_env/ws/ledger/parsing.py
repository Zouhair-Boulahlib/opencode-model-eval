"""Parsing of user-supplied strings into typed values."""
import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

_DATE_FORMATS = ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d", "%d.%m.%Y")
_AMOUNT_CLEAN = re.compile(r"[,\s_]")


def parse_date(text: str) -> date:
    text = text.strip()
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"unrecognised date: {text!r}")


def parse_amount(text: str) -> Decimal:
    """'1,234.50' -> Decimal('1234.50'); '(12.00)' -> Decimal('-12.00'). Major units, not minor."""
    text = text.strip()
    negative = text.startswith("(") and text.endswith(")")
    if negative:
        text = text[1:-1]
    text = _AMOUNT_CLEAN.sub("", text)
    try:
        value = Decimal(text)
    except InvalidOperation as exc:
        raise ValueError(f"unrecognised amount: {text!r}") from exc
    return -value if negative else value


def parse_tags(text: str | None) -> list[str]:
    if not text:
        return []
    return sorted({t.strip().lower() for t in re.split(r"[;,|]", text) if t.strip()})
