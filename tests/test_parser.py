import pytest

from glossary.models import Source
from glossary.parser import TermError, parse_term

FULL = """---
name: Idempotence
sources:
  - title: RFC 9110
    url: https://www.rfc-editor.org/rfc/rfc9110.html
  - https://example.com/retries
---

An operation that can be applied repeatedly.
"""


def test_parses_name_sources_and_description():
    term = parse_term("idempotence", FULL)

    assert term.slug == "idempotence"
    assert term.name == "Idempotence"
    assert term.description == "An operation that can be applied repeatedly."
    assert term.sources == (
        Source("RFC 9110", "https://www.rfc-editor.org/rfc/rfc9110.html"),
        Source("https://example.com/retries", "https://example.com/retries"),
    )


def test_name_defaults_to_slug_and_frontmatter_is_optional():
    term = parse_term("race-condition", "Timing-dependent behaviour.")

    assert term.name == "Race Condition"
    assert term.sources == ()
    assert term.letter == "R"


def test_source_without_url_keeps_its_title():
    term = parse_term("api", "---\nsources:\n  - title: A printed book\n---\nContract.")

    assert term.sources == (Source("A printed book", None),)


def test_terms_starting_with_a_digit_land_in_the_other_bucket():
    assert parse_term("12-factor-app", "Twelve guidelines.").letter == "#"


@pytest.mark.parametrize(
    ("slug", "text", "message"),
    [
        ("Bad Slug", "Body.", "kebab-case"),
        ("empty", "---\nname: X\n---\n\n   \n", "description is empty"),
        ("broken", "---\nname: [unclosed\n---\nBody.", "invalid YAML"),
        ("scalar", "---\njust a string\n---\nBody.", "must be a mapping"),
        ("typo", "---\nsorces: []\n---\nBody.", "unknown frontmatter keys: sorces"),
        ("blank-name", "---\nname: '  '\n---\nBody.", "non-empty string"),
        ("bad-sources", "---\nsources: nope\n---\nBody.", "'sources' must be a list"),
        ("bad-entry", "---\nsources:\n  - 42\n---\nBody.", "URL string or a mapping"),
        ("bad-key", "---\nsources:\n  - link: x\n---\nBody.", "unknown source keys: link"),
        ("js-url", "---\nsources:\n  - javascript:alert(1)\n---\nBody.", "must be http"),
    ],
)
def test_rejects_malformed_files(slug, text, message):
    with pytest.raises(TermError, match=message):
        parse_term(slug, text)


def test_error_names_the_file():
    with pytest.raises(TermError, match=r"^broken\.md: "):
        parse_term("broken", "---\nname: [\n---\nBody.")
