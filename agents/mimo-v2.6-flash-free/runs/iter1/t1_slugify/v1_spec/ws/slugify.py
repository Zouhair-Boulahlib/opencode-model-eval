import unicodedata


def slugify(text: str, max_length: int | None = None) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower()

    parts: list[str] = []
    pending_sep = False
    for c in text:
        if ("a" <= c <= "z") or ("0" <= c <= "9"):
            parts.append(c)
            pending_sep = False
        elif not pending_sep:
            parts.append("-")
            pending_sep = True

    slug = "".join(parts).strip("-")

    if max_length is not None:
        if max_length <= 0:
            return ""
        slug = slug[:max_length].rstrip("-")

    return slug
