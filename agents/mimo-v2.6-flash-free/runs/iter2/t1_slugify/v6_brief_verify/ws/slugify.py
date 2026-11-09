"""Turn a string into a URL slug.

Rules:
    1. Unicode is normalized (NFKD) and combining marks are dropped, so
       accented characters fold to their ASCII base ("Café" -> "cafe").
    2. The text is lowercased.
    3. Every character that is not an ASCII letter or digit becomes a
       separator hyphen (spaces, punctuation, underscores, non-ASCII
       letters such as CJK/Cyrillic, ...).
    4. Runs of hyphens collapse into one, and leading/trailing hyphens
       are stripped.
    5. ``max_length`` truncates the slug to at most that many characters
       and never leaves a trailing hyphen. A non-positive ``max_length``
       yields the empty string.
    6. Empty or symbol-only input yields the empty string.

    ``text`` must be a str and ``max_length`` an int (or None);
    anything else raises TypeError.
"""

from __future__ import annotations

import re
import unicodedata

__all__ = ["slugify"]

_NON_ALNUM = re.compile(r"[^a-z0-9]+")
_SEPARATOR = "-"


def slugify(text: str, max_length: int | None = None) -> str:
    if not isinstance(text, str):
        raise TypeError(f"text must be str, got {type(text).__name__}")
    if max_length is not None and (
        isinstance(max_length, bool) or not isinstance(max_length, int)
    ):
        raise TypeError(
            f"max_length must be int or None, got {type(max_length).__name__}"
        )

    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = "".join(
        ch for ch in normalized if not unicodedata.combining(ch)
    ).lower()

    slug = _NON_ALNUM.sub(_SEPARATOR, ascii_text).strip(_SEPARATOR)

    if max_length is not None:
        if max_length <= 0:
            return ""
        if len(slug) > max_length:
            slug = slug[:max_length].rstrip(_SEPARATOR)

    return slug


if __name__ == "__main__":
    import sys

    print(slugify(*sys.argv[1:]))
