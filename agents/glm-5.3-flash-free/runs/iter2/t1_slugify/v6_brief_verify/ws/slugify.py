import re
import unicodedata


def slugify(text, max_length=None):
    """Turn a string into a URL slug.

    - Normalizes accented characters to ASCII (é -> e)
    - Lowercases
    - Removes non-alphanumeric characters
    - Collapses consecutive separators into a single hyphen
    - Strips leading/trailing hyphens
    - Optionally truncates to max_length without a trailing hyphen
    """
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    if max_length is not None:
        text = text[:max_length].rstrip("-")
    return text
