#!/usr/bin/env python3
"""ultradocs lint — machine-checkable wiki defects.

Python stdlib only. Invoked by the `ultradocs:lint` skill.
"""
import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

_FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)$", re.DOTALL)


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


_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
_FOOTNOTE_REF_RE = re.compile(r"\[\^([\w-]+)\](?!:)")


def extract_links(body: str) -> list[str]:
    out = []
    for target in _LINK_RE.findall(body):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        if target.startswith("#"):
            continue
        out.append(target)
    return out


def extract_footnotes(body: str) -> list[str]:
    return _FOOTNOTE_REF_RE.findall(body)


_WIKI_FOLDERS = ("refs", "topics", "overviews")


def walk_wiki(root: Path) -> list[dict]:
    pages = []
    for folder in _WIKI_FOLDERS:
        fdir = root / folder
        if not fdir.is_dir():
            continue
        for md in fdir.rglob("*.md"):
            if md.name in ("CLAUDE.md", "README.md"):
                continue
            text = md.read_text(encoding="utf-8")
            fm, body = parse_frontmatter(text)
            pages.append({
                "path": md,
                "rel": str(md.relative_to(root)),
                "folder": folder,
                "id": fm.get("id", ""),
                "frontmatter": fm,
                "body": body,
                "links": extract_links(body),
                "footnotes": extract_footnotes(body),
            })
    return pages


def check_orphans(pages, wiki_root):
    inbound = defaultdict(int)
    for p in pages:
        for target in p["links"]:
            target_clean = target.split("#", 1)[0]
            if not target_clean:
                continue
            resolved = (p["path"].parent / target_clean).resolve()
            inbound[resolved] += 1
    defects = []
    for p in pages:
        if inbound[p["path"].resolve()] == 0:
            defects.append({
                "check": "orphan",
                "severity": "warn",
                "page": p["rel"],
                "message": "no inbound markdown links",
                "data": {},
            })
    return defects


REQUIRED_KEYS = ("id", "title", "type", "created", "updated", "status")
TYPE_PER_FOLDER = {"refs": "ref", "topics": "topic", "overviews": "overview"}


def check_frontmatter(pages):
    defects = []
    for p in pages:
        fm = p["frontmatter"]
        for key in REQUIRED_KEYS:
            if key not in fm or fm[key] == "":
                defects.append({
                    "check": "frontmatter-violation",
                    "severity": "error",
                    "page": p["rel"],
                    "message": f"missing required key: {key}",
                    "data": {"key": key},
                })
        expected_type = TYPE_PER_FOLDER[p["folder"]]
        if fm.get("type") and fm["type"] != expected_type:
            defects.append({
                "check": "frontmatter-violation",
                "severity": "error",
                "page": p["rel"],
                "message": f"type '{fm['type']}' does not match folder '{p['folder']}' (expected '{expected_type}')",
                "data": {"type": fm.get("type"), "expected": expected_type},
            })
        if p["folder"] in ("topics", "overviews") and fm.get("sources"):
            defects.append({
                "check": "frontmatter-violation",
                "severity": "error",
                "page": p["rel"],
                "message": "sources field is forbidden on topic/overview pages",
                "data": {},
            })
        if p["folder"] == "refs" and not fm.get("sources"):
            defects.append({
                "check": "frontmatter-violation",
                "severity": "error",
                "page": p["rel"],
                "message": "sources field is required on ref pages",
                "data": {},
            })
    return defects


def check_duplicate_ids(pages):
    by_id = defaultdict(list)
    for p in pages:
        if p["id"]:
            by_id[p["id"]].append(p)
    defects = []
    for pid, group in by_id.items():
        if len(group) > 1:
            for p in group:
                defects.append({
                    "check": "duplicate-id",
                    "severity": "error",
                    "page": p["rel"],
                    "message": f"duplicate id '{pid}' shared with {[g['rel'] for g in group if g is not p]}",
                    "data": {"id": pid},
                })
    return defects


def check_broken_links(pages, wiki_root):
    defects = []
    for p in pages:
        for target in p["links"]:
            target_clean = target.split("#", 1)[0]
            if not target_clean:
                continue
            resolved = (p["path"].parent / target_clean).resolve()
            try:
                resolved.relative_to(wiki_root.resolve())
            except ValueError:
                pass
            if not resolved.exists():
                defects.append({
                    "check": "broken-link",
                    "severity": "error",
                    "page": p["rel"],
                    "message": f"link target not found: {target}",
                    "data": {"target": target},
                })
    return defects


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
    pages = walk_wiki(args.wiki_root)
    report["pages_scanned"] = len(pages)

    only = set(filter(None, args.only.split(",")))
    def enabled(name): return not only or name in only

    all_defects = []
    if enabled("broken-link"):
        all_defects.extend(check_broken_links(pages, args.wiki_root))
    if enabled("duplicate-id"):
        all_defects.extend(check_duplicate_ids(pages))
    if enabled("frontmatter-violation"):
        all_defects.extend(check_frontmatter(pages))
    if enabled("orphan"):
        all_defects.extend(check_orphans(pages, args.wiki_root))

    for d in all_defects:
        report["summary"][d["check"]] += 1
    report["defects"] = all_defects

    print(json.dumps(report, indent=2))
    return 0 if not all_defects else 1


if __name__ == "__main__":
    sys.exit(main())
