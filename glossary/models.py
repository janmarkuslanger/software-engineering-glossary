"""Domain model of the glossary. Pure data, no I/O."""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field

OTHER_LETTER = "#"
"""Bucket for terms that do not start with a latin letter (".NET", "12-Factor App")."""


@dataclass(frozen=True)
class Source:
    """A reference backing a term."""

    title: str
    url: str | None = None


@dataclass(frozen=True)
class Term:
    """A single glossary entry, as parsed from one markdown file."""

    slug: str
    name: str
    description: str
    sources: tuple[Source, ...] = field(default_factory=tuple)

    @property
    def letter(self) -> str:
        """Bucket of the A-Z navigation this term belongs to."""
        return initial(self.name)

    @property
    def sort_key(self) -> tuple[str, str]:
        return (fold(self.name), self.slug)


def fold(text: str) -> str:
    """Normalise for comparison: accent-insensitive, case-insensitive."""
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(c for c in decomposed if not unicodedata.combining(c)).casefold()


def initial(name: str) -> str:
    """First character of `name` mapped onto an A-Z bucket, or `#`."""
    first = fold(name)[:1].upper()
    return first if "A" <= first <= "Z" else OTHER_LETTER
