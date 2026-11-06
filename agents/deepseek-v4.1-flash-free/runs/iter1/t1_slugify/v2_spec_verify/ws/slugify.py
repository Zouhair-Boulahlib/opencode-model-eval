import unicodedata


def slugify(text: str, max_length: int | None = None) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    stripped = "".join(
        ch for ch in normalized if not unicodedata.combining(ch)
    )
    lowered = stripped.lower()
    result = []
    prev_sep = False
    for ch in lowered:
        if ch.isascii() and ch.isalnum():
            result.append(ch)
            prev_sep = False
        else:
            if not prev_sep:
                result.append("-")
                prev_sep = True
    slug = "".join(result).strip("-")
    if max_length is not None:
        slug = slug[:max_length].rstrip("-")
    return slug
