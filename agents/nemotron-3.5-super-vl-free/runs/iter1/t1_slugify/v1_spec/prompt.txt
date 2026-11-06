Create a file `slugify.py` in the current directory containing exactly this function:

    def slugify(text: str, max_length: int | None = None) -> str

Apply these rules in order:
1. Normalize the text with Unicode NFKD and drop combining marks (so "Crème Brûlée" becomes "Creme Brulee"). Any character that is still not an ASCII letter or digit after this step (for example "ß" or "日本") is treated as a separator.
2. Lowercase the result.
3. Replace every run of one or more characters that are not ASCII letters or digits (spaces, punctuation, underscores, tabs, newlines, non-ASCII) with a single hyphen "-".
4. Strip leading and trailing hyphens.
5. If `max_length` is not None, cut the slug to at most `max_length` characters, then strip trailing hyphens again. `max_length=0` returns "".
6. Empty input or input containing only separators returns "".

Use only the Python standard library. Put everything in `slugify.py`; do not create other source files.
