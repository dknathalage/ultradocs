#!/usr/bin/env python3
"""ultradocs lint — machine-checkable wiki defects.

Python stdlib only. Invoked by the `ultradocs:lint` skill.
"""
import argparse
import json
import re
import sys
from pathlib import Path

_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.DOTALL)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse YAML front-matter (schema subset).

    Supports: scalars (unquoted, double-quoted), flow-style lists ([a, b, c]),
    dates in ISO form (kept as string). Not a full YAML parser.
    """
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    block, body = m.group(1), m.group(2)
    result: dict = {}
    for line in block.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, raw = line.partition(":")
        key = key.strip()
        raw = raw.strip()
        result[key] = _parse_value(raw)
    return result, body


def _parse_value(raw: str):
    if not raw:
        return ""
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        return [_unquote(x.strip()) for x in inner.split(",")]
    return _unquote(raw)


def _unquote(s: str) -> str:
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ('"', "'"):
        return s[1:-1]
    return s


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
