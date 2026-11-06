import unicodedata
import re


def slugify(text: str, max_length: int | None = None) -> str:
    if not text or text.strip() == "":
        return ""

    # Step 1: Normalize with NFKD and drop combining marks
    normalized = unicodedata.normalize("NFKD", text)
    ascii_only = "".join(c for c in normalized if not unicodedata.combining(c))

    # Step 2: Lowercase
    lowered = ascii_only.lower()

    # Step 3: Replace every run of one or more non-ASCII letters/digits with a single hyphen
    replaced = re.sub(r"[^a-z0-9]+", "-", lowered)

    # Step 4: Strip leading and trailing hyphens
    stripped = replaced.strip("-")

    # Step 5: If max_length is not None, cut to at most max_length chars, then strip trailing hyphens again
    if max_length is not None:
        if max_length == 0:
            return ""
        slug = stripped[:max_length].rstrip("-")
    else:
        slug = stripped

    # Step 6: Empty input or input containing only separators returns ""
    if not slug:
        return ""

    return slug