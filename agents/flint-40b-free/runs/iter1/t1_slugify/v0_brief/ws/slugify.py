import re
import unicodedata

def slugify(text, max_length=None):
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    slug = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
    if max_length is not None:
        slug = slug[:max_length].rstrip('-')
    return slug
