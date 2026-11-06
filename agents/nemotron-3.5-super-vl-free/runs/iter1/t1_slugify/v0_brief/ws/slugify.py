import re


def slugify(text, max_length=None):
    if text is None:
        return ""

    text = str(text).strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    slug = re.sub(r"[_\s-]+", "-", text).strip("-")

    if max_length is not None:
        slug = slug[:max_length].rstrip("-")

    return slug
