Examples (input -> output):
- slugify("Hello World") -> "hello-world"
- slugify("  Hello,   World!  ") -> "hello-world"
- slugify("Crème Brûlée") -> "creme-brulee"
- slugify("C++ & C# rock") -> "c-c-rock"
- slugify("a_b_c") -> "a-b-c"
- slugify("Hello World", max_length=6) -> "hello"   (cut gives "hello-", trailing hyphen stripped)
- slugify("!!!") -> ""
