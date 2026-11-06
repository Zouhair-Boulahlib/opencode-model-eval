import re
import unicodedata


def slugify(text, max_length=None):
    """Convert a string into a URL slug.

    Normalizes unicode, strips diacritics, removes non-alphanumeric
    characters, and joins words with hyphens.

    Args:
        text: The input string to slugify.
        max_length: If given, truncate the slug to at most this many
            characters without leaving a trailing hyphen.

    Returns:
        The slugified string.
    """
    if not isinstance(text, str):
        text = str(text)

    # Decompose unicode and drop combining marks (diacritics).
    value = unicodedata.normalize("NFKD", text)
    value = "".join(c for c in value if not unicodedata.combining(c))

    value = value.lower().strip()
    value = re.sub(r"[_\s]+", "-", value)
    value = re.sub(r"[^a-z0-9-]", "", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")

    if max_length is not None:
        if max_length < 1:
            return ""
        value = value[:max_length]
        # Avoid a dangling hyphen from truncation.
        value = value.rstrip("-")

    return value
