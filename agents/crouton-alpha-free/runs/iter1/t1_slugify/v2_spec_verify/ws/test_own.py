from slugify import slugify


def test_creme_brulee():
    assert slugify("Crème Brûlée") == "creme-brulee"


def test_sharp_s_and_japanese_separators():
    assert slugify("ß") == ""
    assert slugify("日本") == ""
    assert slugify("aßb") == "a-b"
    assert slugify("a日本b") == "a-b"
    assert slugify("hello 日本 world") == "hello-world"


def test_lowercase_and_separators():
    assert slugify("Hello   World") == "hello-world"
    assert slugify("Hello_World") == "hello-world"
    assert slugify("Hello\tWorld\nAgain") == "hello-world-again"
    assert slugify("Hello, World!") == "hello-world"
    assert slugify("  --Hello__World--  ") == "hello-world"
    assert slugify("ABC 123") == "abc-123"


def test_empty_and_only_separators():
    assert slugify("") == ""
    assert slugify("   ") == ""
    assert slugify("---___   ") == ""
    assert slugify("!@#$%") == ""


def test_max_length():
    assert slugify("hello world", max_length=5) == "hello"
    assert slugify("hello world", max_length=6) == "hello"
    assert slugify("hello world", max_length=8) == "hello-wo"
    assert slugify("hello world", max_length=0) == ""
    assert slugify("hello world", max_length=100) == "hello-world"
    assert slugify("hello world", max_length=None) == "hello-world"


def test_max_length_strips_trailing_hyphen():
    assert slugify("hello-world-again", max_length=6) == "hello"
