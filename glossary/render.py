"""Rendering of the static site. Pure: terms in, {output path: HTML} out."""

from __future__ import annotations

import html
import posixpath
import re
import string
from collections.abc import Iterable

import markdown

from .models import OTHER_LETTER, Term

SITE_TITLE = "Software Engineering Glossary"
SITE_TAGLINE = "A plain-language reference of software engineering terms."
LETTERS = tuple(string.ascii_uppercase) + (OTHER_LETTER,)

INDEX_PAGE = "index.html"
STYLESHEET = "style.css"

_MARKDOWN = markdown.Markdown(extensions=["extra", "sane_lists", "smarty"])
_TAGS = re.compile(r"<[^>]+>")


def render_site(terms: Iterable[Term]) -> dict[str, str]:
    """Render every page of the site, keyed by its path below the output root."""
    ordered = sorted(terms, key=lambda term: term.sort_key)
    by_letter: dict[str, list[Term]] = {}
    for term in ordered:
        by_letter.setdefault(term.letter, []).append(term)

    pages = {INDEX_PAGE: _index_page(ordered, by_letter)}
    for letter, group in by_letter.items():
        pages[letter_page(letter)] = _letter_page(letter, group, by_letter)
    for term in ordered:
        pages[term_page(term.slug)] = _term_page(term, by_letter)
    return pages


def letter_page(letter: str) -> str:
    slug = "other" if letter == OTHER_LETTER else letter.lower()
    return f"{slug}/{INDEX_PAGE}"


def term_page(slug: str) -> str:
    return f"term/{slug}/{INDEX_PAGE}"


def _index_page(terms: list[Term], by_letter: dict[str, list[Term]]) -> str:
    count = len(terms)
    entries = "\n".join(
        f'<li><a href="{_link(INDEX_PAGE, term_page(term.slug))}">{html.escape(term.name)}</a></li>'
        for term in terms
    )
    body = f"""
      <p class="lede">{html.escape(SITE_TAGLINE)}</p>
      {_nav(INDEX_PAGE, by_letter, current=None)}
      <h2>All {count} term{"" if count == 1 else "s"}</h2>
      <ul class="term-index">{entries}</ul>
    """
    return _layout(INDEX_PAGE, title=None, heading=SITE_TITLE, body=body)


def _letter_page(letter: str, terms: list[Term], by_letter: dict[str, list[Term]]) -> str:
    path = letter_page(letter)
    heading = "Other" if letter == OTHER_LETTER else letter
    cards = "\n".join(
        f"""<li class="card">
          <h3><a href="{_link(path, term_page(term.slug))}">{html.escape(term.name)}</a></h3>
          <p>{html.escape(_excerpt(term.description))}</p>
        </li>"""
        for term in terms
    )
    body = f"""
      {_nav(path, by_letter, current=letter)}
      <ul class="cards">{cards}</ul>
    """
    return _layout(path, title=f"{heading} — {SITE_TITLE}", heading=heading, body=body)


def _term_page(term: Term, by_letter: dict[str, list[Term]]) -> str:
    path = term_page(term.slug)
    body = f"""
      {_nav(path, by_letter, current=term.letter)}
      <article class="term">
        {_MARKDOWN.reset().convert(term.description)}
      </article>
      {_sources(path, term)}
    """
    return _layout(path, title=f"{term.name} — {SITE_TITLE}", heading=term.name, body=body)


def _sources(path: str, term: Term) -> str:
    if not term.sources:
        return ""
    items = "\n".join(
        "<li>"
        + (
            f'<a href="{html.escape(source.url, quote=True)}" rel="noopener noreferrer">'
            f"{html.escape(source.title)}</a>"
            if source.url
            else html.escape(source.title)
        )
        + "</li>"
        for source in term.sources
    )
    return f'<section class="sources"><h2>Sources</h2><ol>{items}</ol></section>'


def _nav(path: str, by_letter: dict[str, list[Term]], current: str | None) -> str:
    items = []
    for letter in LETTERS:
        group = by_letter.get(letter)
        label = html.escape(letter)
        if not group:
            items.append(f'<li><span class="disabled" aria-disabled="true">{label}</span></li>')
        elif letter == current:
            items.append(
                f'<li><a href="{_link(path, letter_page(letter))}" aria-current="page">{label}</a></li>'
            )
        else:
            items.append(f'<li><a href="{_link(path, letter_page(letter))}">{label}</a></li>')
    return f'<nav class="alphabet" aria-label="Browse by letter"><ul>{"".join(items)}</ul></nav>'


def _layout(path: str, title: str | None, heading: str, body: str) -> str:
    home = _link(path, INDEX_PAGE)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title or SITE_TITLE)}</title>
<meta name="description" content="{html.escape(SITE_TAGLINE, quote=True)}">
<link rel="stylesheet" href="{_link(path, STYLESHEET)}">
</head>
<body>
<header class="masthead">
  <a class="brand" href="{home}">{html.escape(SITE_TITLE)}</a>
</header>
<main>
  <h1>{html.escape(heading)}</h1>
  {body}
</main>
<footer>
  <p>Built from markdown files in <code>terms/</code>.</p>
</footer>
</body>
</html>
"""


def _link(from_page: str, to_page: str) -> str:
    """Relative URL between two pages, so the site works under any base path."""
    target = posixpath.relpath(to_page, posixpath.dirname(from_page))
    directory = posixpath.dirname(target)
    if posixpath.basename(target) == INDEX_PAGE:
        target = f"{directory}/" if directory else "./"
    return html.escape(target, quote=True)


def _excerpt(description: str, limit: int = 180) -> str:
    """First paragraph of the description as plain text, for listings."""
    paragraph = description.strip().split("\n\n", 1)[0]
    text = " ".join(_TAGS.sub("", _MARKDOWN.reset().convert(paragraph)).split())
    text = html.unescape(text)
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0].rstrip(",;:.") + "…"
