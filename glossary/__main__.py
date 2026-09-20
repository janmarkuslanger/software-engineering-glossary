"""CLI: `python -m glossary [--terms DIR] [--out DIR]`."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .build import build
from .parser import TermError

ROOT = Path(__file__).resolve().parent.parent


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="glossary", description=__doc__)
    parser.add_argument("--terms", type=Path, default=ROOT / "terms", help="directory of term markdown files")
    parser.add_argument("--out", type=Path, default=ROOT / "_site", help="output directory (recreated on every build)")
    args = parser.parse_args(argv)

    try:
        written = build(args.terms, args.out)
    except (TermError, FileNotFoundError) as exc:
        print(f"build failed: {exc}", file=sys.stderr)
        return 1

    print(f"wrote {len(written)} files to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
