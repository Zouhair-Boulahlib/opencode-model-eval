import re
import unicodedata


def slugify(text, max_length=None):
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_text.lower()).strip("-")

    if max_length is not None:
        if max_length < 0:
            raise ValueError("max_length must be non-negative")
        slug = slug[:max_length].rstrip("-")

    return slug
