import re
import unicodedata


def slugify(text, max_length=None):
    if text is None:
        text = ""
    text = str(text)
    # Normalize unicode characters to ASCII
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    # Lowercase
    text = text.lower()
    # Replace non-alphanumeric with hyphens
    text = re.sub(r"[^a-z0-9]+", "-", text)
    # Collapse multiple hyphens
    text = re.sub(r"-+", "-", text)
    # Strip leading/trailing hyphens
    text = text.strip("-")
    if max_length is not None:
        if max_length < 0:
            max_length = 0
        text = text[:max_length]
        text = text.rstrip("-")
    return text
