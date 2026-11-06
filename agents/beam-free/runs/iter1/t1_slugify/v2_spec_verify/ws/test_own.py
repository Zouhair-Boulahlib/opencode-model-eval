from slugify import slugify


def test_creme():
    assert slugify("Crème Brûlée") == "creme-brulee"


def test_separator_chars():
    assert slugify("aßb") == "a-b"
    assert slugify("日本") == ""


def test_lowercase():
    assert slugify("Hello World") == "hello-world"


def test_runs():
    assert slugify("a   b!!!c") == "a-b-c"
    assert slugify("a_b_c") == "a-b-c"


def test_strip():
    assert slugify("---a---") == "a"
    assert slugify("  hello  ") == "hello"


def test_max_length():
    assert slugify("hello-world", 5) == "hello"
    assert slugify("hello-world", 6) == "hello"  # trailing hyphen stripped
    assert slugify("hello-world", 0) == ""


def test_empty():
    assert slugify("") == ""
    assert slugify("   ") == ""
    assert slugify("___") == ""