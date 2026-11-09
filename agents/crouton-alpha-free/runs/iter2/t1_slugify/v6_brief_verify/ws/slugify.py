import re
import unicodedata


def slugify(text, max_length=None):
    if text is None:
        text = ""
    text = str(text)
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = text.replace("'", "")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    if max_length is not None:
        try:
            max_length = int(max_length)
        except (TypeError, ValueError):
            raise TypeError("max_length must be an integer or None")
        if max_length <= 0:
            return ""
        if len(text) > max_length:
            truncated = text[:max_length]
            if truncated.endswith("-"):
                truncated = truncated.rstrip("-")
            elif max_length < len(text) and text[max_length] != "-":
                if "-" in truncated:
                    truncated = truncated[: truncated.rfind("-")].rstrip("-")
                else:
                    truncated = truncated.rstrip("-")
            text = truncated
    return text
