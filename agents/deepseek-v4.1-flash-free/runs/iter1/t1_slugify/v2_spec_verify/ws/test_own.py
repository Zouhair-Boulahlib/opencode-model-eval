from slugify import slugify


def test_basic():
    assert slugify("Hello World") == "hello-world"


def test_accents():
    assert slugify("Crème Brûlée") == "creme-brulee"


def test_separators():
    assert slugify("  Hello___World!!  ") == "hello-world"


def test_tabs_newlines():
    assert slugify("a\tb\nc") == "a-b-c"


def test_non_ascii_separator():
    assert slugify("aßb") == "a-b"
    assert slugify("a日本b") == "a-b"


def test_strip_hyphens():
    assert slugify("---Hello---") == "hello"


def test_max_length():
    assert slugify("hello world", max_length=8) == "hello-wo"
    assert slugify("hello world", max_length=6) == "hello"
    assert slugify("hello world", max_length=7) == "hello-w"
    assert slugify("hello world", max_length=0) == ""
    assert slugify("hello world", max_length=5) == "hello"


def test_empty():
    assert slugify("") == ""
    assert slugify("   ") == ""
    assert slugify("!!!") == ""


def test_only_separators_after_nfkd():
    assert slugify("日本") == ""
