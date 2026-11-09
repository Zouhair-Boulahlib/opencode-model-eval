import re
import unicodedata


def slugify(text, max_length=None):
    if text is None:
        return ""

    normalized = unicodedata.normalize("NFKD", str(text))
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_text).strip("-").lower()

    if max_length is not None:
        if max_length <= 0:
            return ""
        slug = slug[:max_length].rstrip("-")

    return slug
