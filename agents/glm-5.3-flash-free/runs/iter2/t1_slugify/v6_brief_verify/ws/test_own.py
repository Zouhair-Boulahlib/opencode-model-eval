from slugify import slugify


def test_basic():
    assert slugify("Hello World") == "hello-world"


def test_lowercase_and_spaces():
    assert slugify("  Hello   World  ") == "hello-world"


def test_accented_characters():
    assert slugify("Héllo Wörld") == "hello-world"


def test_remove_special_characters():
    assert slugify("Hello, World!") == "hello-world"
    assert slugify("foo@bar.com") == "foo-bar-com"


def test_multiple_separators():
    assert slugify("a -- b _ c") == "a-b-c"


def test_leading_trailing_hyphens():
    assert slugify("--hello--world--") == "hello-world"


def test_empty_string():
    assert slugify("") == ""


def test_numbers():
    assert slugify("Release 2.0") == "release-2-0"


def test_max_length():
    assert slugify("Hello World", max_length=5) == "hello"


def test_max_length_no_trailing_hyphen():
    assert slugify("Hello World", max_length=6) == "hello"


def test_max_length_none():
    assert slugify("Hello World", max_length=None) == "hello-world"


def test_cyrillic_removed():
    assert slugify("Привет мир") == ""
