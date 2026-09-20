"""Filesystem boundary: read term files, write the rendered site."""

from __future__ import annotations

import shutil
from pathlib import Path

from .models import Term
from .parser import TermError, parse_term
from .render import render_site

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


def load_terms(source_dir: Path) -> list[Term]:
    """Parse every `*.md` file in `source_dir`. Raises on the first malformed file."""
    files = sorted(source_dir.glob("*.md"))
    if not files:
        raise FileNotFoundError(f"no term files found in {source_dir}")

    terms = [parse_term(path.stem, path.read_text(encoding="utf-8")) for path in files]
    _reject_duplicate_names(terms)
    return terms


def build(source_dir: Path, output_dir: Path) -> list[Path]:
    """Render the site from `source_dir` into a freshly created `output_dir`."""
    terms = load_terms(source_dir)
    pages = render_site(terms)

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    written = []
    for path, content in pages.items():
        target = output_dir / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        written.append(target)

    written.extend(_copy_assets(output_dir))

    # Tells GitHub Pages to serve the files as-is instead of running Jekyll.
    nojekyll = output_dir / ".nojekyll"
    nojekyll.touch()
    written.append(nojekyll)
    return written


def _copy_assets(output_dir: Path) -> list[Path]:
    """Copy `assets/` verbatim into the output root: stylesheets and font files."""
    shutil.copytree(ASSETS_DIR, output_dir, dirs_exist_ok=True)
    return sorted(
        output_dir / path.relative_to(ASSETS_DIR)
        for path in ASSETS_DIR.rglob("*")
        if path.is_file()
    )


def _reject_duplicate_names(terms: list[Term]) -> None:
    seen: dict[str, str] = {}
    for term in terms:
        key = term.name.casefold()
        if key in seen:
            raise TermError(term.slug, f"duplicate term name, already defined in {seen[key]}.md")
        seen[key] = term.slug
