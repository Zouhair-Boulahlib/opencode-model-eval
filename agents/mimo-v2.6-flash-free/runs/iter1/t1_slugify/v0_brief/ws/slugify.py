import re
import unicodedata


def slugify(text, max_length=None):
    if text is None:
        return ""
    text = unicodedata.normalize("NFKD", str(text))
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")

    if max_length is not None:
        max_length = int(max_length)
        if max_length <= 0:
            return ""
        if len(text) > max_length:
            text = text[:max_length].rstrip("-")
    return text
