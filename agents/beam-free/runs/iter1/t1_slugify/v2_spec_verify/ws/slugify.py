import re
import unicodedata


def slugify(text: str, max_length: int | None = None) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    chars = [c for c in normalized if not unicodedata.combining(c)]
    s = "".join(chars).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    if max_length is not None:
        if max_length <= 0:
            return ""
        s = s[:max_length].rstrip("-")
    return s