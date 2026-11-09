from slugify import slugify


def test_basic():
    assert slugify("Hello World") == "hello-world"


def test_lowercase():
    assert slugify("HELLO") == "hello"


def test_punctuation_and_spaces_collapse():
    assert slugify("  Hello,   World!  ") == "hello-world"


def test_underscores_and_symbols():
    assert slugify("foo_bar+baz/qux") == "foo-bar-baz-qux"


def test_accents_are_transliterated():
    assert slugify("Café au lait") == "cafe-au-lait"


def test_leading_trailing_separators_removed():
    assert slugify("---hello---") == "hello"


def test_empty_and_none():
    assert slugify("") == ""
    assert slugify(None) == ""


def test_max_length_truncates():
    assert slugify("Hello World", max_length=5) == "hello"


def test_max_length_strips_trailing_hyphen():
    assert slugify("Hello World", max_length=6) == "hello"


def test_max_length_larger_than_slug():
    assert slugify("Hi There", max_length=100) == "hi-there"


def test_max_length_zero_or_negative():
    assert slugify("Hello", max_length=0) == ""
    assert slugify("Hello", max_length=-3) == ""
