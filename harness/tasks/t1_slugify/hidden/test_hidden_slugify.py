import pytest
from slugify import slugify


@pytest.mark.parametrize("text,expected", [
    ("Hello World", "hello-world"),
    ("  Hello,   World!  ", "hello-world"),
    ("Crème Brûlée", "creme-brulee"),
    ("already-slugged", "already-slugged"),
    ("C++ & C# rock", "c-c-rock"),
    ("a_b_c", "a-b-c"),
    ("123 Main St.", "123-main-st"),
    ("tab\tand\nnewline", "tab-and-newline"),
    ("ÀÉÎÕÜ", "aeiou"),
    ("Straße 日本", "stra-e"),
    ("MiXeD CaSe", "mixed-case"),
])
def test_basic(text, expected):
    assert slugify(text) == expected


@pytest.mark.parametrize("text", ["", "---", "!!!", "   ", "日本語"])
def test_empty_results(text):
    assert slugify(text) == ""


def test_max_length_cut():
    assert slugify("Hello World", max_length=5) == "hello"


def test_max_length_strips_trailing_hyphen():
    assert slugify("Hello World", max_length=6) == "hello"


def test_max_length_longer_than_slug():
    assert slugify("Hi there", max_length=100) == "hi-there"


def test_max_length_zero():
    assert slugify("Hello", max_length=0) == ""


def test_max_length_exact():
    assert slugify("Hello World", max_length=11) == "hello-world"


def test_returns_str_type():
    out = slugify("x")
    assert isinstance(out, str) and out == "x"
