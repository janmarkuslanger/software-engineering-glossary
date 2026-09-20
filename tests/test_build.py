import pytest

from glossary.build import build, load_terms
from glossary.parser import TermError

TERM = "---\nname: {name}\n---\n\nDescription of {name}.\n"


def write(directory, slug, name):
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"{slug}.md").write_text(TERM.format(name=name), encoding="utf-8")


def test_build_writes_pages_stylesheet_and_nojekyll(tmp_path):
    terms, out = tmp_path / "terms", tmp_path / "_site"
    write(terms, "api", "API")

    build(terms, out)

    assert (out / "index.html").exists()
    assert (out / "a/index.html").exists()
    assert (out / "term/api/index.html").exists()
    assert (out / "style.css").read_text(encoding="utf-8").startswith(":root")
    assert (out / ".nojekyll").exists()


def test_build_copies_the_self_hosted_fonts(tmp_path):
    terms, out = tmp_path / "terms", tmp_path / "_site"
    write(terms, "api", "API")

    build(terms, out)

    assert "@font-face" in (out / "fonts.css").read_text(encoding="utf-8")
    assert sorted(p.name for p in (out / "fonts").glob("*.woff2"))
    # fonts.css sits next to fonts/, so its relative url() resolves from any page.
    assert "url(fonts/" in (out / "fonts.css").read_text(encoding="utf-8")


def test_build_removes_stale_output(tmp_path):
    terms, out = tmp_path / "terms", tmp_path / "_site"
    write(terms, "api", "API")
    out.mkdir()
    (out / "term").mkdir()
    (out / "term" / "deleted.html").write_text("old", encoding="utf-8")

    build(terms, out)

    assert not (out / "term" / "deleted.html").exists()


def test_empty_terms_directory_is_an_error(tmp_path):
    (tmp_path / "terms").mkdir()

    with pytest.raises(FileNotFoundError):
        load_terms(tmp_path / "terms")


def test_duplicate_names_are_rejected(tmp_path):
    terms = tmp_path / "terms"
    write(terms, "api", "API")
    write(terms, "application-programming-interface", "api")

    with pytest.raises(TermError, match="duplicate term name, already defined in api.md"):
        load_terms(terms)


def test_repository_terms_build(tmp_path):
    from glossary.__main__ import ROOT

    written = build(ROOT / "terms", tmp_path / "_site")

    assert len(written) > 10
