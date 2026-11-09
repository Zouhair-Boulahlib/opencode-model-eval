import re
import unicodedata


def slugify(text, max_length=None):
    """Convert *text* into a URL-friendly slug.

    The slug is lowercase, ASCII, and uses single hyphens between words.
    Leading/trailing hyphens are removed, and the result is optionally
    truncated to at most *max_length* characters.
    """
    if text is None:
        return ""

    text = str(text)

    # Decompose accented characters and drop the combining marks.
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")

    text = text.lower()

    # Anything that is not a letter or digit becomes a hyphen.
    text = re.sub(r"[^a-z0-9]+", "-", text)

    # Collapse repeated hyphens and trim from both ends.
    text = re.sub(r"-{2,}", "-", text).strip("-")

    if max_length is not None and max_length >= 0:
        text = text[:max_length].rstrip("-")

    return text
