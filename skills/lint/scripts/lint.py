#!/usr/bin/env python3
"""ultradocs lint — machine-checkable wiki defects.

Python stdlib only. Invoked by the `ultradocs:lint` skill.
"""
import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(prog="lint.py")
    parser.add_argument("wiki_root", type=Path)
    parser.add_argument("--only", type=str, default="")
    args = parser.parse_args()

    if not args.wiki_root.is_dir():
        print(f"error: {args.wiki_root} is not a directory", file=sys.stderr)
        return 2

    report = {
        "wiki_root": str(args.wiki_root),
        "pages_scanned": 0,
        "defects": [],
        "summary": {
            "orphan": 0,
            "broken-link": 0,
            "duplicate-id": 0,
            "missing-citation": 0,
            "overview-underlinked": 0,
            "stale": 0,
            "frontmatter-violation": 0,
        },
    }
    print(json.dumps(report, indent=2))
    return 0 if not report["defects"] else 1


if __name__ == "__main__":
    sys.exit(main())
