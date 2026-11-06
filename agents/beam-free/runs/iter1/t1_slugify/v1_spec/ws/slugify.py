import re
import unicodedata


def slugify(text: str, max_length: int | None = None) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    stripped = "".join(c for c in normalized if not unicodedata.combining(c))
    chars = []
    for c in stripped:
        if c.isascii() and c.isalnum():
            chars.append(c)
        else:
            chars.append("-")
    slug = "".join(chars).lower()
    slug = re.sub(r"-+", "-", slug)
    slug = slug.strip("-")
    if max_length is not None:
        if max_length <= 0:
            return ""
        slug = slug[:max_length].rstrip("-")
    return slug
