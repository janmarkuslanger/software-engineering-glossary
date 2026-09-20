"""Parsing of term files: markdown with YAML frontmatter. Pure, no I/O."""

from __future__ import annotations

import re
import yaml

from .models import Source, Term

FRONTMATTER = re.compile(r"\A---\r?\n(?P<meta>.*?)\r?\n---[ \t]*\r?\n?(?P<body>.*)\Z", re.S)

SLUG_ALLOWED = re.compile(r"\A[a-z0-9]+(?:-[a-z0-9]+)*\Z")


class TermError(ValueError):
    """A term file is malformed. Carries the offending slug for context."""

    def __init__(self, slug: str, message: str) -> None:
        super().__init__(f"{slug}.md: {message}")
        self.slug = slug


def parse_term(slug: str, text: str) -> Term:
    """Build a `Term` from the raw contents of `<slug>.md`."""
    if not SLUG_ALLOWED.match(slug):
        raise TermError(slug, "file name must be lowercase kebab-case (a-z, 0-9, '-')")

    meta, body = _split(slug, text)
    name = meta.pop("name", None) or slug.replace("-", " ").title()
    if not isinstance(name, str) or not name.strip():
        raise TermError(slug, "'name' must be a non-empty string")

    sources = _parse_sources(slug, meta.pop("sources", None))
    if meta:
        raise TermError(slug, f"unknown frontmatter keys: {', '.join(sorted(meta))}")

    description = body.strip()
    if not description:
        raise TermError(slug, "description is empty")

    return Term(slug=slug, name=name.strip(), description=description, sources=sources)


def _split(slug: str, text: str) -> tuple[dict, str]:
    match = FRONTMATTER.match(text.lstrip("﻿"))
    if not match:
        return {}, text

    try:
        meta = yaml.safe_load(match["meta"])
    except yaml.YAMLError as exc:
        raise TermError(slug, f"invalid YAML frontmatter: {exc}") from exc

    if meta is None:
        meta = {}
    if not isinstance(meta, dict):
        raise TermError(slug, "frontmatter must be a mapping")
    return meta, match["body"]


def _parse_sources(slug: str, raw: object) -> tuple[Source, ...]:
    if raw is None:
        return ()
    if not isinstance(raw, list):
        raise TermError(slug, "'sources' must be a list")

    sources = []
    for entry in raw:
        if isinstance(entry, str):
            sources.append(_source_from_url(slug, entry))
        elif isinstance(entry, dict):
            sources.append(_source_from_mapping(slug, entry))
        else:
            raise TermError(slug, "each source must be a URL string or a mapping")
    return tuple(sources)


def _source_from_url(slug: str, url: str) -> Source:
    url = url.strip()
    if not url:
        raise TermError(slug, "source URL is empty")
    return Source(title=url, url=_checked_url(slug, url))


def _source_from_mapping(slug: str, entry: dict) -> Source:
    unknown = set(entry) - {"title", "url"}
    if unknown:
        raise TermError(slug, f"unknown source keys: {', '.join(sorted(unknown))}")

    url = entry.get("url")
    if url is not None:
        url = _checked_url(slug, str(url).strip())

    title = entry.get("title") or url
    if not isinstance(title, str) or not title.strip():
        raise TermError(slug, "source needs a 'title' or a 'url'")
    return Source(title=title.strip(), url=url)


def _checked_url(slug: str, url: str) -> str:
    """Reject anything but http(s) so a source link can never become script execution."""
    if not url.lower().startswith(("http://", "https://")):
        raise TermError(slug, f"source URL must be http(s): {url!r}")
    return url
