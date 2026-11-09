from slugify import slugify


def test_basic():
    assert slugify("Hello World") == "hello-world"


def test_punctuation_and_spaces():
    assert slugify("  Hello,   World!  ") == "hello-world"


def test_multiple_separators_collapse():
    assert slugify("foo---bar___baz") == "foo-bar-baz"


def test_leading_trailing_separators_removed():
    assert slugify("--Hello World--") == "hello-world"


def test_unicode_accents_removed():
    assert slugify("Café déjà vu") == "cafe-deja-vu"


def test_empty_and_none():
    assert slugify("") == ""
    assert slugify(None) == ""


def test_only_punctuation():
    assert slugify("!!!") == ""


def test_numbers_preserved():
    assert slugify("Python 3.13") == "python-3-13"


def test_max_length():
    assert slugify("The quick brown fox", max_length=9) == "the-quick"
    assert len(slugify("The quick brown fox", max_length=9)) <= 9


def test_max_length_no_trailing_hyphen():
    assert slugify("Hello World", max_length=6) == "hello"


def test_max_length_larger_than_slug():
    assert slugify("Hi there", max_length=100) == "hi-there"


def test_max_length_zero():
    assert slugify("Hello", max_length=0) == ""
