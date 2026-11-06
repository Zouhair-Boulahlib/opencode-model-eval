import re
import unicodedata


def slugify(text: str, max_length: int | None = None) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    stripped = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    lowered = stripped.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", lowered)
    slug = slug.strip("-")
    if max_length is not None:
        slug = slug[:max_length].rstrip("-")
    return slug
