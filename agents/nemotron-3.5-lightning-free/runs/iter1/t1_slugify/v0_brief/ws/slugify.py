import re


def slugify(text, max_length=None):
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text.strip())
    text = re.sub(r"[-\s]+", "-", text)
    if max_length is not None:
        text = text[:max_length]
    return text