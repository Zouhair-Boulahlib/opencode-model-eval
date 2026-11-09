import pytest

from slugify import slugify


def test_basic_two_words():
    assert slugify("Hello World") == "hello-world"


def test_lowercases():
    assert slugify("CAPS LOCK") == "caps-lock"


def test_punctuation_becomes_separator():
    assert slugify("Hello, World!") == "hello-world"


def test_underscores_become_separator():
    assert slugify("foo_bar baz") == "foo-bar-baz"


def test_collapses_repeated_separators():
    assert slugify("a --- b   c") == "a-b-c"


def test_strips_leading_and_trailing_separators():
    assert slugify("  --hello--  ") == "hello"


def test_already_a_slug_is_unchanged():
    assert slugify("already-a-slug") == "already-a-slug"


def test_digits_kept():
    assert slugify("Top 10 Things") == "top-10-things"


def test_accents_fold_to_ascii():
    assert slugify("Café Déjà Vu") == "cafe-deja-vu"
    assert slugify("Ünïcödé") == "unicode"


def test_symbols_only_returns_empty():
    assert slugify("!!!") == ""
    assert slugify("   ") == ""
    assert slugify("") == ""


def test_non_ascii_letters_without_ascii_base_removed():
    assert slugify("日本語") == ""


def test_max_length_truncates():
    assert slugify("hello world", max_length=5) == "hello"


def test_max_length_does_not_end_with_hyphen():
    assert slugify("hello world", max_length=6) == "hello"
    assert slugify("hello world", max_length=8) == "hello-wo"


def test_max_length_larger_than_slug_is_ignored():
    assert slugify("short", max_length=100) == "short"


def test_max_length_zero_returns_empty():
    assert slugify("hello world", max_length=0) == ""


def test_max_length_negative_returns_empty():
    assert slugify("hello world", max_length=-3) == ""


def test_max_length_one():
    assert slugify("abc def", max_length=1) == "a"


def test_none_text_raises_type_error():
    with pytest.raises(TypeError):
        slugify(None)


def test_non_string_text_raises_type_error():
    with pytest.raises(TypeError):
        slugify(42)


def test_bad_max_length_raises_type_error():
    with pytest.raises(TypeError):
        slugify("hi", max_length="10")
    with pytest.raises(TypeError):
        slugify("hi", max_length=3.5)
    with pytest.raises(TypeError):
        slugify("hi", max_length=True)
