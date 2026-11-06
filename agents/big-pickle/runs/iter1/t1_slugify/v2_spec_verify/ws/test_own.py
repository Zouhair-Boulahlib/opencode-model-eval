from slugify import slugify


def test_basic():
    assert slugify("Hello, World!") == "hello-world"


def test_unicode_accents():
    assert slugify("Crème Brûlée") == "creme-brulee"


def test_non_ascii_separators():
    assert slugify("Straße") == "stra-e"
    assert slugify("日本語") == ""


def test_punctuation_and_whitespace_runs():
    assert slugify("  foo___bar\t\nbaz  ") == "foo-bar-baz"


def test_strip_hyphens():
    assert slugify("---hello---") == "hello"


def test_max_length():
    assert slugify("hello world", max_length=6) == "hello"
    assert slugify("hello world", max_length=7) == "hello-w"
    assert slugify("hello world", max_length=8) == "hello-wo"
    assert slugify("hello world", max_length=100) == "hello-world"
    assert slugify("hello world", max_length=0) == ""


def test_empty_and_separators_only():
    assert slugify("") == ""
    assert slugify("   ---!!!") == ""
