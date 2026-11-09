"""Small helpers shared across modules."""
import hashlib
from datetime import date
from itertools import islice
from typing import Iterable, Iterator, TypeVar

T = TypeVar("T")


def month_key(d: date) -> str:
    return f"{d.year:04d}-{d.month:02d}"


def chunked(items: Iterable[T], size: int) -> Iterator[list[T]]:
    it = iter(items)
    while chunk := list(islice(it, size)):
        yield chunk


def stable_id(*parts: object) -> str:
    """Deterministic id from the row's content so re-imports do not duplicate."""
    h = hashlib.sha1("|".join(str(p) for p in parts).encode("utf-8")).hexdigest()
    return h[:12]


def percent(part: int, whole: int) -> float:
    """Share of `part` in `whole`, in percent (0-100). Used by budgets and reports."""
    return 0.0 if whole == 0 else round(part * 100 / whole, 1)
