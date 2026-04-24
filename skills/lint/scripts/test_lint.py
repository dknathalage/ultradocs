import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

SCRIPT = Path(__file__).parent / "lint.py"


def run(args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True,
    )


def test_usage_error_on_missing_wiki_root():
    result = run(["/nonexistent/path"])
    assert result.returncode == 2


def test_clean_empty_wiki_exits_zero():
    with tempfile.TemporaryDirectory() as d:
        wiki = Path(d)
        (wiki / "refs").mkdir()
        (wiki / "topics").mkdir()
        (wiki / "overviews").mkdir()
        result = run([str(wiki)])
        assert result.returncode == 0, result.stderr
        out = json.loads(result.stdout)
        assert out["pages_scanned"] == 0
        assert out["defects"] == []


from lint import parse_frontmatter, walk_wiki, extract_links, extract_footnotes


def test_parse_frontmatter_minimal():
    md = """---
id: foo
title: Foo
type: topic
created: 2026-04-25
updated: 2026-04-25
tags: [a, b]
status: draft
---

body"""
    fm, body = parse_frontmatter(md)
    assert fm["id"] == "foo"
    assert fm["type"] == "topic"
    assert fm["tags"] == ["a", "b"]
    assert body.strip() == "body"


def test_parse_frontmatter_missing_returns_empty():
    fm, body = parse_frontmatter("no front-matter here")
    assert fm == {}
    assert body == "no front-matter here"


def test_parse_frontmatter_quoted_string():
    md = """---
id: foo
title: "Foo: the musical"
type: ref
---
body"""
    fm, _ = parse_frontmatter(md)
    assert fm["title"] == "Foo: the musical"


def test_parse_frontmatter_sources_list():
    md = """---
id: foo
type: ref
sources: [https://example.com/a, ./local.pdf]
---
body"""
    fm, _ = parse_frontmatter(md)
    assert fm["sources"] == ["https://example.com/a", "./local.pdf"]


def test_extract_links_relative_only():
    body = """
    See [foo](../topics/foo.md) and [bar](./bar.md).
    But not [external](https://example.com).
    Nor [anchor](#heading).
    """
    links = extract_links(body)
    assert "../topics/foo.md" in links
    assert "./bar.md" in links
    assert "https://example.com" not in links
    assert "#heading" not in links


def test_extract_footnotes():
    body = "See [^foo] and [^bar-baz]."
    assert extract_footnotes(body) == ["foo", "bar-baz"]


def test_walk_wiki_skips_claude_md_and_readme():
    with tempfile.TemporaryDirectory() as d:
        wiki = Path(d)
        (wiki / "refs").mkdir()
        (wiki / "topics").mkdir()
        (wiki / "overviews").mkdir()
        (wiki / "CLAUDE.md").write_text("# instr")
        (wiki / "README.md").write_text("# readme")
        (wiki / "refs" / "CLAUDE.md").write_text("# instr")
        (wiki / "refs" / "a.md").write_text("---\nid: a\ntype: ref\n---\nbody")
        (wiki / "topics" / "b.md").write_text("---\nid: b\ntype: topic\n---\nbody")
        pages = walk_wiki(wiki)
        ids = sorted(p["id"] for p in pages)
        assert ids == ["a", "b"]


# ---------------------------------------------------------------------------
# unittest discovery shim — wraps all module-level test_* functions
# ---------------------------------------------------------------------------
def load_tests(loader, tests, pattern):
    import types
    module = sys.modules[__name__]
    for name in sorted(vars(module)):
        if name.startswith("test_") and callable(getattr(module, name)):
            fn = getattr(module, name)
            if not isinstance(fn, type):
                tests.addTest(unittest.FunctionTestCase(fn))
    return tests


if __name__ == "__main__":
    unittest.main()
