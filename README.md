# Software Engineering Glossary

A static glossary of software engineering terms. One term is one markdown file in
[`terms/`](terms); a Python build script turns that folder into a site with A–Z
navigation and a detail page per term, deployed to GitHub Pages.

## Adding a term

Create `terms/<slug>.md`. The file name is the URL slug and must be lowercase
kebab-case:

```markdown
---
name: Idempotence
sources:
  - title: RFC 9110 — HTTP Semantics, Section 9.2.2
    url: https://www.rfc-editor.org/rfc/rfc9110.html#name-idempotent-methods
  - https://example.com/a-bare-url-works-too
---

An operation is **idempotent** when applying it more than once has the same effect as
applying it once.

## Achieving it

Markdown is fully supported: headings, lists, tables, code blocks, links.
```

- `name` — optional, defaults to the slug in title case. Decides the A–Z bucket;
  terms not starting with a latin letter land under `#`.
- `sources` — optional list of `{title, url}` mappings or bare `http(s)` URLs.
- Everything below the frontmatter is the description.

The build fails on unknown frontmatter keys, non-`http(s)` source URLs, empty
descriptions and duplicate term names, so a typo never silently ships.

## Building locally

Dependencies are managed with [uv](https://docs.astral.sh/uv/); `uv run` creates the
environment from `uv.lock` on first use.

```bash
uv run pytest -q                        # tests
uv run python -m glossary               # renders ./terms into ./_site
uv run python -m http.server -d _site 8000
```

`uv run python -m glossary --terms DIR --out DIR` overrides the defaults. The output
directory is deleted and recreated on every build. Dependency changes go into
`pyproject.toml`, followed by `uv lock`.

## Deployment

`.github/workflows/pages.yml` runs the tests and the build on every push to `main`
and publishes `_site` to GitHub Pages. Enable it once under
**Settings → Pages → Build and deployment → Source: GitHub Actions**. Pull requests
run tests and build without deploying.

All links in the generated site are relative, so it works both at a user page root
and under a project path such as `/software-engineering-glossary/`.

## Layout

| Path | Purpose |
| --- | --- |
| `terms/*.md` | content, one file per term |
| `glossary/models.py` | `Term` / `Source` and the A–Z bucketing rule |
| `glossary/parser.py` | markdown file → `Term`, with validation |
| `glossary/render.py` | terms → `{page path: HTML}` |
| `glossary/build.py` | the only filesystem layer: read, render, write |
| `assets/style.css` | stylesheet, copied into the output as-is |
| `tests/` | pytest suite |
| `pyproject.toml`, `uv.lock` | dependencies, pinned by uv |
