import re
import unicodedata


def slugify(text: str, max_length: int | None = None) -> str:
    norm = unicodedata.normalize("NFKD", text)
    norm = "".join(ch for ch in norm if not unicodedata.combining(ch))
    norm = norm.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", norm).strip("-")
    if max_length is not None:
        slug = slug[:max_length].rstrip("-")
    return slug
