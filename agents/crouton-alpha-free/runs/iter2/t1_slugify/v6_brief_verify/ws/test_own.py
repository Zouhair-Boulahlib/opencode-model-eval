from slugify import slugify


def test_basic_lowercase_and_space():
    assert slugify("Hello World") == "hello-world"


def test_punctuation_removed():
    assert slugify("Hello, World!") == "hello-world"


def test_multiple_spaces_and_underscores_collapsed():
    assert slugify("Hello   World__Foo") == "hello-world-foo"


def test_leading_trailing_trimmed():
    assert slugify("  Hello World  ") == "hello-world"
    assert slugify("---Hello---") == "hello"


def test_unicode_transliteration():
    assert slugify("Héllo Wörld") == "hello-world"
    assert slugify("naïve café") == "naive-cafe"


def test_empty_and_symbol_only():
    assert slugify("") == ""
    assert slugify("!!!") == ""
    assert slugify("   ") == ""


def test_numbers_preserved():
    assert slugify("Top 10 Tips") == "top-10-tips"


def test_apostrophe():
    assert slugify("Don't") == "dont"


def test_max_length_basic():
    result = slugify("Hello World Foo", max_length=5)
    assert result == "hello"
    assert len(result) <= 5


def test_max_length_no_trailing_hyphen():
    result = slugify("hello world", max_length=6)
    assert not result.endswith("-")
    assert len(result) <= 6


def test_max_length_word_boundary():
    assert slugify("Hello World Foo", max_length=11) == "hello-world"


def test_max_length_none():
    assert slugify("Hello World", max_length=None) == "hello-world"
    assert slugify("Hello World") == "hello-world"


def test_max_length_single_long_word():
    assert slugify("supercalifragilistic", max_length=5) == "super"
