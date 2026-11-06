import re
import unicodedata


def slugify(text: str, max_length: int | None = None) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    without_marks = "".join(
        char for char in normalized if not unicodedata.combining(char)
    )
    ascii_only = "".join(
        char if ord(char) < 128 and char.isalnum() else " "
        for char in without_marks
    )
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_only.lower()).strip("-")

    if max_length is not None:
        if max_length <= 0:
            return ""
        slug = slug[:max_length].rstrip("-")

    return slug
