import re
import unicodedata


def slugify(text, max_length=None):
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)

    if not text.strip():
        return ""

    text = unicodedata.normalize("NFKD", text)

    replacements = {
        "ß": "ss",
        "ẞ": "ss",
        "æ": "ae",
        "Æ": "ae",
        "œ": "oe",
        "Œ": "oe",
        "ø": "o",
        "Ø": "o",
        "ł": "l",
        "Ł": "l",
        "đ": "d",
        "Đ": "d",
        "ð": "d",
        "Ð": "d",
        "þ": "th",
        "Þ": "th",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)

    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = text.replace("'", "").replace("’", "").replace("`", "")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text)
    text = text.strip("-")

    if max_length is not None:
        try:
            max_length = int(max_length)
        except (TypeError, ValueError):
            max_length = None
        if max_length is not None:
            if max_length <= 0:
                return ""
            if len(text) > max_length:
                text = text[:max_length].strip("-")

    return text
