import pytest

from slugify import slugify


def test_accents_stripped():
    assert slugify("Crème Brûlée") == "creme-brulee"


def test_combining_marks():
    assert slugify("e\u0301") == "e"


def test_non_ascii_letters_are_separators():
    assert slugify("ß") == ""
    assert slugify("日本語") == ""
    assert slugify("aßb") == "a-b"
    assert slugify("a日本b") == "a-b"


def test_lowercasing():
    assert slugify("Hello World") == "hello-world"
    assert slugify("ABC def GHI") == "abc-def-ghi"


def test_runs_of_separators_collapse():
    assert slugify("a  b") == "a-b"
    assert slugify("a--b") == "a-b"
    assert slugify("a,;:!?b") == "a-b"
    assert slugify("a\tb\nc  d") == "a-b-c-d"


def test_underscores_are_separators():
    assert slugify("foo_bar_baz") == "foo-bar-baz"


def test_strip_leading_trailing_hyphens():
    assert slugify("  --Hello--  ") == "hello"
    assert slugify("...test...") == "test"


def test_max_length_truncates():
    assert slugify("Hello World", 5) == "hello"
    assert slugify("Hello World", 11) == "hello-world"
    assert slugify("Hello World", 100) == "hello-world"


def test_max_length_strips_trailing_hyphen():
    assert slugify("Ab Cd", 3) == "ab"
    assert slugify("Hello  World", 6) == "hello"


def test_max_length_zero():
    assert slugify("Hello", 0) == ""


def test_max_length_none_keeps_full():
    assert slugify("Hello World") == "hello-world"


def test_empty_input():
    assert slugify("") == ""
    assert slugify("", 5) == ""


def test_separators_only():
    assert slugify("   ") == ""
    assert slugify("---") == ""
    assert slugify("!!! @@@ ###") == ""
    assert slugify("日本", 10) == ""


def test_digits_preserved():
    assert slugify("Version 2 of 10") == "version-2-of-10"
    assert slugify("abc123") == "abc123"


def test_mixed():
    assert slugify("Crème & Brûlée — 2024!", 20) == "creme-brulee-2024"


@pytest.mark.parametrize(
    "text,max_length,expected",
    [
        ("Crème Brûlée", None, "creme-brulee"),
        ("Crème Brûlée", 5, "creme"),
        ("  Hi  ", 3, "hi"),
        ("", 7, ""),
    ],
)
def test_parametrized(text, max_length, expected):
    assert slugify(text, max_length) == expected
