from glossary.models import Source, Term
from glossary.render import render_site

TERMS = [
    Term("refactoring", "Refactoring", "Behaviour-preserving change.\n\nSecond paragraph."),
    Term("api", "API", "A contract.", (Source("RFC", "https://example.com/rfc"),)),
    Term("12-factor-app", "12-Factor App", "Twelve guidelines."),
]


def pages():
    return render_site(TERMS)


def test_page_set_covers_index_present_letters_and_every_term():
    assert set(pages()) == {
        "index.html",
        "a/index.html",
        "r/index.html",
        "other/index.html",
        "term/refactoring/index.html",
        "term/api/index.html",
        "term/12-factor-app/index.html",
    }


def test_alphabet_links_only_letters_that_have_terms():
    index = pages()["index.html"]

    assert '<a href="a/">A</a>' in index
    assert '<span class="disabled" aria-disabled="true">B</span>' in index


def test_links_are_relative_so_the_site_works_under_any_base_path():
    term_page = pages()["term/api/index.html"]

    assert 'href="../../a/"' in term_page
    assert 'href="../../style.css"' in term_page
    assert 'href="../../"' in term_page
    assert 'href="/' not in term_page


def test_term_page_renders_name_description_and_sources():
    page = pages()["term/api/index.html"]

    assert "<h1>API</h1>" in page
    assert "<p>A contract.</p>" in page
    assert '<a href="https://example.com/rfc" rel="noopener noreferrer">RFC</a>' in page


def test_term_page_without_sources_omits_the_section():
    assert "Sources" not in pages()["term/refactoring/index.html"]


def test_letter_page_lists_its_terms_with_an_excerpt_of_the_first_paragraph():
    page = pages()["r/index.html"]

    assert '<a href="../term/refactoring/">Refactoring</a>' in page
    assert "<p>Behaviour-preserving change.</p>" in page
    assert "Second paragraph" not in page


def test_current_letter_is_marked_on_its_own_page():
    assert 'href="./" aria-current="page">R</a>' in pages()["r/index.html"]


def test_markup_in_a_term_name_is_escaped():
    page = render_site([Term("xss", "<script>", "Body.")])["term/xss/index.html"]

    assert "<h1>&lt;script&gt;</h1>" in page
