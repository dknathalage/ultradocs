# ultradocs Plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build v0.0.1 of the `ultradocs` Claude Code plugin: a markdown-wiki system with 4 skills (init, ingest, query, lint), 2 agents (curator, researcher), and a Python-stdlib lint script. Spec: `docs/superpowers/specs/2026-04-25-ultradocs-plugin-design.md`.

**Architecture:** Skills-only interface. Each skill is a directory `skills/<name>/` containing `SKILL.md` with YAML front-matter + procedure. The `init` skill copies template files from `skills/init/templates/` into a target wiki path. The `lint` skill calls a Python stdlib script at `skills/lint/scripts/lint.py` that emits JSON defects. Agents (`agents/<name>.md`) define write vs read personas invoking these skills. Wiki folders: `refs/`, `topics/`, `overviews/`.

**Tech Stack:** Claude Code plugin (markdown + YAML). Python 3.11+ stdlib only for lint.py. `unittest` for lint tests. Git.

---

## File Structure

### Plugin files (created)

```
ultradocs/
  .claude-plugin/
    plugin.json                     # already exists
    marketplace.json                # already exists
  skills/
    init/
      SKILL.md
      templates/
        root-CLAUDE.md
        root-README.md
        refs-CLAUDE.md
        topics-CLAUDE.md
        overviews-CLAUDE.md
    ingest/
      SKILL.md
    query/
      SKILL.md
    lint/
      SKILL.md
      scripts/
        lint.py
        test_lint.py
        fixtures/
          clean/                    # control wiki, no defects
            <clean wiki tree>
          seeded/                   # seeded-defect wiki
            <defect wiki tree>
  agents/
    ultradocs-curator.md
    ultradocs-researcher.md
  docs/
    superpowers/
      specs/2026-04-25-ultradocs-plugin-design.md     # exists
      plans/2026-04-25-ultradocs-plugin.md            # this file
```

### Responsibility of each file

- `skills/init/SKILL.md` — triggers on "initialize wiki" / "set up ultradocs"; accepts optional `path` argument (default `docs/`, `.` = cwd); copies templates from `templates/` into target path, filling placeholders (`{{wiki_name}}`, `{{date}}`).
- `skills/init/templates/*.md` — static content per §4.1 and §4.2 of spec.
- `skills/ingest/SKILL.md` — triggers on "add to wiki" / "ingest"; reads a source, writes `refs/<id>.md`, updates topics per §9.2 heuristic, touches overviews, appends README recent-changes.
- `skills/query/SKILL.md` — triggers on "what does wiki say about X"; Glob/Grep wiki, synthesize with `[^ref]` footnotes, emit gap note if found. No writes.
- `skills/lint/SKILL.md` — triggers on "lint wiki" / "check wiki"; runs `scripts/lint.py`, parses JSON, performs LLM soft checks, reports + applies safe fixes.
- `skills/lint/scripts/lint.py` — deterministic machine checks per §6.2; JSON output per §12.
- `skills/lint/scripts/test_lint.py` — unittest suite against `fixtures/`.
- `skills/lint/scripts/fixtures/` — `clean/` control wiki, `seeded/` defect wiki matching §11 success criteria counts.
- `agents/ultradocs-curator.md` — write-side agent; tools Read/Write/Edit/Glob/Grep/Bash; invokes `ultradocs:ingest` and `ultradocs:lint`.
- `agents/ultradocs-researcher.md` — read-side agent; tools Read/Glob/Grep/WebFetch/WebSearch (no Write/Edit); invokes `ultradocs:query` only.

---

## Task 0: Initialize repository

**Files:**
- Modify: `/Users/dknathalage/repos/ultradocs/` (git init)

- [ ] **Step 1: Init git**

```bash
cd /Users/dknathalage/repos/ultradocs
git init
```

Expected: `Initialized empty Git repository in /Users/dknathalage/repos/ultradocs/.git/`

- [ ] **Step 2: Add .gitignore**

Create `.gitignore`:
```
.DS_Store
__pycache__/
*.pyc
.pytest_cache/
```

- [ ] **Step 3: First commit**

```bash
git add .gitignore .claude-plugin/ docs/
git commit -m "chore: initial plugin scaffolding with spec and plan"
```

Expected: commit created.

---

## Task 1: Init skill — templates

**Files:**
- Create: `skills/init/templates/root-CLAUDE.md`
- Create: `skills/init/templates/root-README.md`
- Create: `skills/init/templates/refs-CLAUDE.md`
- Create: `skills/init/templates/topics-CLAUDE.md`
- Create: `skills/init/templates/overviews-CLAUDE.md`

- [ ] **Step 1: Write root-CLAUDE.md template**

Must contain all 9 sections per spec §4.1: Purpose, Folder roles, Front-matter schema, Naming, Link style, Citation style, Page templates (ref/topic/overview skeletons), Lint rules, Workflow.

Content:

````markdown
# Wiki AI Instructions

> For AI agents (Claude). Human docs live in `README.md`.

## 1. Purpose

This wiki is a persistent, interlinked markdown knowledge store. LLMs maintain it; humans curate sources and ask questions. Wiki IS the index — no RAG, no embeddings.

## 2. Folder roles

- `refs/` — one page per external source (paper, URL, doc, code snapshot). Body is a summary. Body is immutable once written.
- `topics/` — atomic concept pages. One idea per page.
- `overviews/` — aggregated narratives linking multiple topics/refs.

## 3. Front-matter schema (YAML, required on every page)

```yaml
---
id: <stable-id>               # slug or ULID; never reused
title: <human title>
type: ref | topic | overview
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [<url-or-path>, ...] # required on refs; forbidden on topics/overviews
tags: [tag1, tag2]
status: draft | stable | stale
---
```

## 4. Naming

- Filenames: kebab-case.
- `id` in front-matter is the stable identifier for cross-reference (citation keys, `sources:`).
- Filename is the link target — relative markdown links resolve by path.
- Renames allowed but you must rewrite all inbound links in the same commit.

## 5. Link style

Relative markdown only: `[foo](../topics/foo.md)`. No wikilinks. No bare http links as cross-references.

## 6. Citation style

Footnote syntax: `[^ref-id]` where `ref-id` matches the `id` of a page in `refs/`. Every non-trivial claim in `topics/` or `overviews/` must cite ≥1 ref.

## 7. Page templates

### ref

```markdown
---
id: <slug>
title: <source title>
type: ref
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [<url-or-path>]
tags: []
status: stable
---

# <title>

Summary of the source in 1–3 paragraphs. Capture the key claims, methods, and conclusions.

## Key points

- ...
```

### topic

```markdown
---
id: <slug>
title: <concept>
type: topic
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: []
status: draft
---

# <title>

Prose explaining the single concept, citing refs[^ref-id].

## Related

- [related-topic](./related-topic.md)

[^ref-id]: See `refs/<ref-id>.md`.
```

### overview

```markdown
---
id: <slug>
title: <area>
type: overview
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: []
status: draft
---

# <title>

Narrative tying together [topic-a](../topics/topic-a.md), [topic-b](../topics/topic-b.md), and [topic-c](../topics/topic-c.md).

Each substantive paragraph cites a topic or ref[^ref-id].

[^ref-id]: See `refs/<ref-id>.md`.
```

## 8. Lint rules

Machine-checked by `ultradocs:lint`:

- Orphan: page with no inbound markdown links (excluding README).
- Broken link: relative link target not found.
- Duplicate `id`.
- Missing citation: paragraph in topic/overview without `[^ref]`.
- Overview under-linked: fewer than 3 distinct topic/ref links.
- Stale: `ref` with `status: stable`, `updated` >90 days old, local source mtime newer than `updated`.
- Front-matter violation: missing required keys; `sources` on topic/overview; `type` not matching folder.

LLM-checked:

- Contradictions across pages.
- Topic atomicity violation (>400 words, H3+ headings, multiple concepts).
- Overview paragraphs without topic/ref citations.

## 9. Workflow

- **Ingest** new sources with `ultradocs:ingest` — writes a ref, updates affected topics, touches overviews.
- **Query** with `ultradocs:query` — never writes; emits gap notes if content missing.
- **Lint** with `ultradocs:lint` regularly — fix defects before they compound.
- **Restructure** (merge/split/promote) is manual, performed by `ultradocs-curator`.
````

- [ ] **Step 2: Write root-README.md template**

Content:

````markdown
# {{wiki_name}}

Markdown wiki maintained with the [ultradocs](https://github.com/dknathalage/ultradocs) Claude Code plugin.

## Structure

- [`refs/`](./refs/) — external sources, summarized.
- [`topics/`](./topics/) — atomic concept pages.
- [`overviews/`](./overviews/) — narrative aggregations.

## Recent changes

_Appended by `ultradocs:ingest`._

## Stats

- Pages: 0
- Refs: 0
- Topics: 0
- Overviews: 0

_Run `ultradocs:lint` to refresh._
````

- [ ] **Step 3: Write refs-CLAUDE.md template**

````markdown
# refs/ AI Instructions

## Role

One page per external source. Each page summarizes a paper, URL, document, or code snapshot. Body is immutable — only update if the source itself changes.

## Template

```markdown
---
id: <slug>
title: <source title>
type: ref
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [<url-or-path>]
tags: []
status: stable
---

# <title>

1–3 paragraph summary.

## Key points

- ...
```

## Rules

- `type: ref` required.
- `sources:` must list at least one URL or path.
- Body is immutable once `status: stable`.
- Kebab-case filename, matching `id` where practical.

## Anti-patterns

- Editorializing — stick to summarizing the source.
- Citing other refs inside a ref — refs are terminal.
- Multiple sources per ref page — one source, one page.
````

- [ ] **Step 4: Write topics-CLAUDE.md template**

````markdown
# topics/ AI Instructions

## Role

Atomic concept pages. One idea per page.

## Template

```markdown
---
id: <slug>
title: <concept>
type: topic
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: []
status: draft
---

# <title>

Prose explaining the single concept, citing refs[^ref-id].

## Related

- [related-topic](./related-topic.md)

[^ref-id]: See `refs/<ref-id>.md`.
```

## Rules

- `type: topic` required.
- `sources:` forbidden (use footnote citations instead).
- **Atomicity**: single noun-phrase title; body ≤400 words; no H3+ headings; if you feel the urge to write "X and Y", split.
- Every substantive paragraph cites ≥1 ref via `[^ref-id]`.
- Link related topics with relative markdown links.

## Anti-patterns

- Multi-concept pages ("X and Y").
- Uncited assertions.
- Using `sources:` front-matter field (that's refs-only).
````

- [ ] **Step 5: Write overviews-CLAUDE.md template**

````markdown
# overviews/ AI Instructions

## Role

Narrative aggregations linking topics and refs into a readable overview of an area.

## Template

```markdown
---
id: <slug>
title: <area>
type: overview
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: []
status: draft
---

# <title>

Narrative tying together [topic-a](../topics/topic-a.md), [topic-b](../topics/topic-b.md), and [topic-c](../topics/topic-c.md).

Each substantive paragraph cites a topic or ref[^ref-id].

[^ref-id]: See `refs/<ref-id>.md`.
```

## Rules

- `type: overview` required.
- `sources:` forbidden.
- Must link ≥3 distinct topic or ref pages.
- No original claims — every substantive paragraph cites a linked topic or ref.

## Anti-patterns

- Overviews with fewer than 3 links (promote to a topic instead).
- Original analysis not supported by a cited topic/ref.
- Duplicating topic content instead of linking to it.
````

- [ ] **Step 6: Commit**

```bash
git add skills/init/templates/
git commit -m "feat(init): add wiki scaffolding templates"
```

---

## Task 2: Init skill — SKILL.md

**Files:**
- Create: `skills/init/SKILL.md`

- [ ] **Step 1: Write SKILL.md**

Content:

````markdown
---
name: init
description: Initialize a new ultradocs wiki at a given path. Triggers on "initialize wiki", "set up ultradocs", "create a wiki at X", "ultradocs init". Accepts an optional path argument (default `docs/`, use `.` for cwd).
---

# ultradocs:init

Scaffold a new wiki at the target path with the canonical layout and CLAUDE.md/README.md instruction files.

## When to use

User says any of:
- "initialize a wiki"
- "set up ultradocs here"
- "create a wiki at ./somepath"
- "ultradocs init [path]"

## Inputs

- `path` (optional): target directory. Default `docs/`. Use `.` for current working directory.

## Procedure

1. Resolve target path. If relative, resolve against cwd. If `.`, use cwd.
2. If the target already contains any of `CLAUDE.md`, `refs/`, `topics/`, `overviews/`, stop and report: "wiki already exists at <path>; refusing to overwrite".
3. Create directories:
   - `<path>/refs/`
   - `<path>/topics/`
   - `<path>/overviews/`
4. Copy templates from `$CLAUDE_PLUGIN_ROOT/skills/init/templates/` into target:
   - `root-CLAUDE.md` → `<path>/CLAUDE.md`
   - `root-README.md` → `<path>/README.md`, substituting `{{wiki_name}}` with the basename of `<path>` (or the repo name if `<path>` is `.`).
   - `refs-CLAUDE.md` → `<path>/refs/CLAUDE.md`
   - `topics-CLAUDE.md` → `<path>/topics/CLAUDE.md`
   - `overviews-CLAUDE.md` → `<path>/overviews/CLAUDE.md`
5. Report success with a tree of what was created.

## Outputs

Confirmation message plus the created file list.

## Do not

- Write any pages into `refs/`, `topics/`, `overviews/` — scaffolding only.
- Overwrite existing files.
````

- [ ] **Step 2: Commit**

```bash
git add skills/init/SKILL.md
git commit -m "feat(init): add init skill"
```

---

## Task 3: Lint script — scaffold and argparse

**Files:**
- Create: `skills/lint/scripts/lint.py`
- Create: `skills/lint/scripts/test_lint.py`

- [ ] **Step 1: Write failing test for CLI**

`test_lint.py`:

```python
import json
import subprocess
import sys
import tempfile
from pathlib import Path

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
```

- [ ] **Step 2: Run tests — verify fail**

```bash
cd /Users/dknathalage/repos/ultradocs/skills/lint/scripts
python3 -m unittest test_lint.py -v
```

Expected: FAIL (file `lint.py` doesn't exist).

- [ ] **Step 3: Write minimal lint.py**

```python
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
```

- [ ] **Step 4: Run tests — verify pass**

```bash
python3 -m unittest test_lint.py -v
```

Expected: 2 tests pass.

- [ ] **Step 5: Commit**

```bash
git add skills/lint/scripts/lint.py skills/lint/scripts/test_lint.py
git commit -m "feat(lint): scaffold lint.py CLI with empty-wiki happy path"
```

---

## Task 4: Lint — front-matter parser

**Files:**
- Modify: `skills/lint/scripts/lint.py`
- Modify: `skills/lint/scripts/test_lint.py`

A minimal YAML parser for the schema subset: scalars (strings, ints, dates), flow-style lists (`[a, b, c]`), quoted strings. Full YAML NOT required.

- [ ] **Step 1: Write failing tests for parser**

Add to `test_lint.py`:

```python
from lint import parse_frontmatter


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
```

- [ ] **Step 2: Run — verify fail**

```bash
python3 -m unittest test_lint.py -v
```

Expected: 4 new tests fail (ImportError or AttributeError).

- [ ] **Step 3: Implement parse_frontmatter**

Add to `lint.py`:

```python
import re

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
```

- [ ] **Step 4: Run — verify pass**

```bash
python3 -m unittest test_lint.py -v
```

Expected: all 6 tests pass.

- [ ] **Step 5: Commit**

```bash
git add -u
git commit -m "feat(lint): add stdlib-only front-matter parser"
```

---

## Task 5: Lint — wiki walker + link/footnote extractors

**Files:**
- Modify: `skills/lint/scripts/lint.py`
- Modify: `skills/lint/scripts/test_lint.py`

- [ ] **Step 1: Write failing tests**

Add to `test_lint.py`:

```python
from lint import walk_wiki, extract_links, extract_footnotes


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
```

- [ ] **Step 2: Run — verify fail**

```bash
python3 -m unittest test_lint.py -v
```

- [ ] **Step 3: Implement walker + extractors**

Add to `lint.py`:

```python
_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
_FOOTNOTE_REF_RE = re.compile(r"\[\^([\w-]+)\]")


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
```

- [ ] **Step 4: Wire walker into main() page count**

Replace the `pages_scanned: 0` hardcoded value:

```python
pages = walk_wiki(args.wiki_root)
report["pages_scanned"] = len(pages)
```

- [ ] **Step 5: Run — verify pass**

```bash
python3 -m unittest test_lint.py -v
```

- [ ] **Step 6: Commit**

```bash
git add -u
git commit -m "feat(lint): wiki walker, link extractor, footnote extractor"
```

---

## Task 6: Lint — broken-link check

**Files:**
- Modify: `skills/lint/scripts/lint.py`
- Modify: `skills/lint/scripts/test_lint.py`

- [ ] **Step 1: Write failing test**

```python
def test_broken_link_detected():
    with tempfile.TemporaryDirectory() as d:
        wiki = Path(d)
        for f in ("refs", "topics", "overviews"):
            (wiki / f).mkdir()
        (wiki / "topics" / "a.md").write_text(
            "---\nid: a\ntype: topic\n---\n"
            "See [missing](./missing.md)."
        )
        result = run([str(wiki)])
        assert result.returncode == 1
        out = json.loads(result.stdout)
        checks = [d["check"] for d in out["defects"]]
        assert "broken-link" in checks
        assert out["summary"]["broken-link"] == 1
```

- [ ] **Step 2: Run — verify fail**

- [ ] **Step 3: Implement check**

Add to `lint.py`:

```python
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
```

Wire into `main()` — replace the prior `print(...); return 0 if not report["defects"] else 1` block (inside `main()`) with this body. The lines below all live inside the existing `main()` function after the `if not args.wiki_root.is_dir()` guard and `report = {...}` initialization:

```python
    pages = walk_wiki(args.wiki_root)
    report["pages_scanned"] = len(pages)

    only = set(filter(None, args.only.split(",")))
    def enabled(name): return not only or name in only

    all_defects = []
    if enabled("broken-link"):
        all_defects.extend(check_broken_links(pages, args.wiki_root))

    for d in all_defects:
        report["summary"][d["check"]] += 1
    report["defects"] = all_defects

    print(json.dumps(report, indent=2))
    return 0 if not all_defects else 1
```

As each subsequent task adds a check, append another `if enabled("<check-id>"): all_defects.extend(check_<x>(...))` line to the block — do not duplicate the wiring code in later tasks.

- [ ] **Step 4: Run — verify pass**

- [ ] **Step 5: Commit**

```bash
git add -u
git commit -m "feat(lint): broken-link check"
```

---

## Task 7: Lint — duplicate-id check

**Files:**
- Modify: `skills/lint/scripts/lint.py`
- Modify: `skills/lint/scripts/test_lint.py`

- [ ] **Step 1: Write failing test**

```python
def test_duplicate_id_detected():
    with tempfile.TemporaryDirectory() as d:
        wiki = Path(d)
        for f in ("refs", "topics", "overviews"):
            (wiki / f).mkdir()
        (wiki / "topics" / "a.md").write_text("---\nid: dup\ntype: topic\n---\nbody")
        (wiki / "topics" / "b.md").write_text("---\nid: dup\ntype: topic\n---\nbody")
        result = run([str(wiki)])
        out = json.loads(result.stdout)
        assert out["summary"]["duplicate-id"] >= 1
```

- [ ] **Step 2: Run — verify fail**

- [ ] **Step 3: Implement**

```python
from collections import defaultdict


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
```

Wire into main() like Task 6.

- [ ] **Step 4: Run — verify pass**

- [ ] **Step 5: Commit**

```bash
git add -u
git commit -m "feat(lint): duplicate-id check"
```

---

## Task 8: Lint — front-matter violation check

**Files:** same pattern as above.

- [ ] **Step 1: Write failing tests**

```python
def test_frontmatter_missing_required_keys():
    with tempfile.TemporaryDirectory() as d:
        wiki = Path(d)
        for f in ("refs", "topics", "overviews"):
            (wiki / f).mkdir()
        (wiki / "topics" / "a.md").write_text("---\nid: a\n---\nbody")
        result = run([str(wiki)])
        out = json.loads(result.stdout)
        assert out["summary"]["frontmatter-violation"] >= 1


def test_sources_forbidden_on_topic():
    with tempfile.TemporaryDirectory() as d:
        wiki = Path(d)
        for f in ("refs", "topics", "overviews"):
            (wiki / f).mkdir()
        (wiki / "topics" / "a.md").write_text(
            "---\nid: a\ntype: topic\ncreated: 2026-01-01\n"
            "updated: 2026-01-01\nsources: [https://x]\n"
            "status: draft\ntitle: A\n---\nbody"
        )
        result = run([str(wiki)])
        out = json.loads(result.stdout)
        violations = [d for d in out["defects"]
                      if d["check"] == "frontmatter-violation"]
        assert any("sources" in v["message"] for v in violations)


def test_type_must_match_folder():
    with tempfile.TemporaryDirectory() as d:
        wiki = Path(d)
        for f in ("refs", "topics", "overviews"):
            (wiki / f).mkdir()
        (wiki / "topics" / "a.md").write_text(
            "---\nid: a\ntitle: A\ntype: ref\ncreated: 2026-01-01\n"
            "updated: 2026-01-01\nstatus: draft\n---\nbody"
        )
        result = run([str(wiki)])
        out = json.loads(result.stdout)
        violations = [d for d in out["defects"]
                      if d["check"] == "frontmatter-violation"]
        assert any("type" in v["message"] for v in violations)
```

- [ ] **Step 2: Run — verify fail**

- [ ] **Step 3: Implement**

```python
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
```

Wire into main.

- [ ] **Step 4: Run — verify pass**

- [ ] **Step 5: Commit**

```bash
git add -u
git commit -m "feat(lint): front-matter violation checks"
```

---

## Task 9: Lint — orphan check

- [ ] **Step 1: Write failing test**

```python
def test_orphan_detected():
    with tempfile.TemporaryDirectory() as d:
        wiki = Path(d)
        for f in ("refs", "topics", "overviews"):
            (wiki / f).mkdir()
        (wiki / "topics" / "lonely.md").write_text(
            "---\nid: lonely\ntitle: Lonely\ntype: topic\n"
            "created: 2026-01-01\nupdated: 2026-01-01\nstatus: draft\n"
            "---\nsee [^ref1].\n[^ref1]: see refs/ref1.md"
        )
        (wiki / "refs" / "ref1.md").write_text(
            "---\nid: ref1\ntitle: R\ntype: ref\ncreated: 2026-01-01\n"
            "updated: 2026-01-01\nsources: [https://x]\nstatus: stable\n---\nbody"
        )
        result = run([str(wiki)])
        out = json.loads(result.stdout)
        orphans = [d for d in out["defects"] if d["check"] == "orphan"]
        # lonely.md has no inbound links -> orphan
        assert any("lonely" in o["page"] for o in orphans)
```

- [ ] **Step 2: Run — verify fail**

- [ ] **Step 3: Implement**

```python
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
```

Wire into main.

- [ ] **Step 4: Run — verify pass**

- [ ] **Step 5: Commit**

```bash
git add -u
git commit -m "feat(lint): orphan check"
```

---

## Task 10: Lint — missing-citation check

- [ ] **Step 1: Write failing test**

```python
def test_missing_citation_in_topic():
    with tempfile.TemporaryDirectory() as d:
        wiki = Path(d)
        for f in ("refs", "topics", "overviews"):
            (wiki / f).mkdir()
        (wiki / "topics" / "a.md").write_text(
            "---\nid: a\ntitle: A\ntype: topic\ncreated: 2026-01-01\n"
            "updated: 2026-01-01\nstatus: draft\n---\n"
            "This paragraph makes a claim but has no citation.\n\n"
            "Another paragraph still without a citation."
        )
        result = run([str(wiki)])
        out = json.loads(result.stdout)
        assert out["summary"]["missing-citation"] >= 1
```

- [ ] **Step 2: Run — verify fail**

- [ ] **Step 3: Implement**

```python
def check_missing_citations(pages):
    defects = []
    for p in pages:
        if p["folder"] not in ("topics", "overviews"):
            continue
        # Split body on blank lines; skip footnote definitions and headings.
        paragraphs = [
            para for para in re.split(r"\n\s*\n", p["body"])
            if para.strip()
               and not para.lstrip().startswith("#")
               and not re.match(r"^\s*\[\^[\w-]+\]:", para)
        ]
        offenders = [para for para in paragraphs
                     if not _FOOTNOTE_REF_RE.search(para)]
        if offenders:
            defects.append({
                "check": "missing-citation",
                "severity": "warn",
                "page": p["rel"],
                "message": f"{len(offenders)} paragraph(s) without [^ref] citation",
                "data": {"count": len(offenders)},
            })
    return defects
```

- [ ] **Step 4: Run — verify pass**

- [ ] **Step 5: Commit**

```bash
git add -u
git commit -m "feat(lint): missing-citation check"
```

---

## Task 11: Lint — overview-underlinked check

- [ ] **Step 1: Write failing test**

```python
def test_overview_underlinked():
    with tempfile.TemporaryDirectory() as d:
        wiki = Path(d)
        for f in ("refs", "topics", "overviews"):
            (wiki / f).mkdir()
        (wiki / "overviews" / "o.md").write_text(
            "---\nid: o\ntitle: O\ntype: overview\ncreated: 2026-01-01\n"
            "updated: 2026-01-01\nstatus: draft\n---\n"
            "Only two links: [a](../topics/a.md) and [b](../topics/b.md)[^r]."
            "\n[^r]: see refs/r.md"
        )
        (wiki / "topics" / "a.md").write_text(
            "---\nid: a\ntitle: A\ntype: topic\ncreated: 2026-01-01\n"
            "updated: 2026-01-01\nstatus: draft\n---\nbody[^r]\n[^r]: see"
        )
        (wiki / "topics" / "b.md").write_text(
            "---\nid: b\ntitle: B\ntype: topic\ncreated: 2026-01-01\n"
            "updated: 2026-01-01\nstatus: draft\n---\nbody[^r]\n[^r]: see"
        )
        result = run([str(wiki)])
        out = json.loads(result.stdout)
        assert out["summary"]["overview-underlinked"] == 1
```

- [ ] **Step 2: Run — verify fail**

- [ ] **Step 3: Implement**

```python
def check_overview_underlinked(pages):
    defects = []
    for p in pages:
        if p["folder"] != "overviews":
            continue
        distinct = set()
        for target in p["links"]:
            t = target.split("#", 1)[0]
            if t:
                distinct.add(t)
        if len(distinct) < 3:
            defects.append({
                "check": "overview-underlinked",
                "severity": "warn",
                "page": p["rel"],
                "message": f"links {len(distinct)} distinct page(s); overview must link ≥3",
                "data": {"count": len(distinct)},
            })
    return defects
```

- [ ] **Step 4: Run — verify pass**

- [ ] **Step 5: Commit**

```bash
git add -u
git commit -m "feat(lint): overview-underlinked check"
```

---

## Task 12: Lint — stale check

- [ ] **Step 1: Write failing test**

```python
import os
import time


def test_stale_ref_detected():
    with tempfile.TemporaryDirectory() as d:
        wiki = Path(d)
        for f in ("refs", "topics", "overviews"):
            (wiki / f).mkdir()
        source = wiki / "source.pdf"
        source.write_bytes(b"old")
        # Set source mtime newer than updated; updated = 200 days ago
        ref_path = wiki / "refs" / "r.md"
        ref_path.write_text(
            "---\nid: r\ntitle: R\ntype: ref\ncreated: 2024-01-01\n"
            "updated: 2024-01-01\nsources: [./source.pdf]\nstatus: stable\n---\nbody"
        )
        # Ensure source mtime > updated (use current time, which is >> 2024-01-01)
        os.utime(source, (time.time(), time.time()))
        result = run([str(wiki)])
        out = json.loads(result.stdout)
        assert out["summary"]["stale"] >= 1
```

- [ ] **Step 2: Run — verify fail**

- [ ] **Step 3: Implement**

```python
from datetime import date, datetime, timedelta

STALE_DAYS = 90


def check_stale(pages, wiki_root):
    defects = []
    today = date.today()
    for p in pages:
        if p["folder"] != "refs":
            continue
        fm = p["frontmatter"]
        if fm.get("status") != "stable":
            continue
        try:
            updated = datetime.strptime(fm.get("updated", ""), "%Y-%m-%d").date()
        except ValueError:
            continue
        if (today - updated).days < STALE_DAYS:
            continue
        sources = fm.get("sources", [])
        if not isinstance(sources, list):
            continue
        for src in sources:
            if src.startswith(("http://", "https://")):
                continue
            src_path = (p["path"].parent / src).resolve() \
                if not Path(src).is_absolute() else Path(src)
            if not src_path.exists():
                continue
            src_mtime = datetime.fromtimestamp(src_path.stat().st_mtime).date()
            if src_mtime > updated:
                defects.append({
                    "check": "stale",
                    "severity": "warn",
                    "page": p["rel"],
                    "message": f"local source {src} modified after 'updated'",
                    "data": {"source": str(src), "updated": fm["updated"]},
                })
                break
    return defects
```

- [ ] **Step 4: Run — verify pass**

- [ ] **Step 5: Commit**

```bash
git add -u
git commit -m "feat(lint): stale check"
```

---

## Task 13: Lint — fixtures and success-criterion test

**Files:**
- Create: `skills/lint/scripts/fixtures/clean/` (valid tiny wiki)
- Create: `skills/lint/scripts/fixtures/seeded/` (seeded defects matching §11)
- Modify: `skills/lint/scripts/test_lint.py`

- [ ] **Step 1a: Scaffold clean fixture directories**

```bash
mkdir -p /Users/dknathalage/repos/ultradocs/skills/lint/scripts/fixtures/clean/{refs,topics,overviews}
```

- [ ] **Step 1b: Write clean fixture files**

Create these files (all with valid front-matter, no defects):

- `fixtures/clean/refs/ref-a.md` — ref with `sources: [https://example.com/a]`.
- `fixtures/clean/refs/ref-b.md` — ref with `sources: [https://example.com/b]`.
- `fixtures/clean/refs/ref-c.md` — ref with `sources: [https://example.com/c]`.
- `fixtures/clean/topics/topic-a.md` — topic citing `[^ref-a]`, linked from overview.
- `fixtures/clean/topics/topic-b.md` — topic citing `[^ref-b]`, linked from overview.
- `fixtures/clean/topics/topic-c.md` — topic citing `[^ref-c]`, linked from overview.
- `fixtures/clean/overviews/area-one.md` — overview linking to topic-a, topic-b, topic-c (≥3 links).

Each topic must also be the target of an inbound link (overview links all three → no orphans). Each ref must also be the target of at least one inbound link — cite `[^ref-x]` footnotes resolve to `refs/ref-x.md` relative markdown links inside the footnote definition (e.g. `[^ref-a]: See [ref-a](../refs/ref-a.md).`).

- [ ] **Step 2a: Scaffold seeded fixture directories**

```bash
mkdir -p /Users/dknathalage/repos/ultradocs/skills/lint/scripts/fixtures/seeded/{refs,topics,overviews}
```

- [ ] **Step 2b: Write seeded fixture files**

Create exactly these defects (match §11 counts):

- `fixtures/seeded/refs/good-ref.md` — valid ref, linked from overview.
- `fixtures/seeded/topics/orphan-1.md` — valid topic, no inbound links (**orphan 1**).
- `fixtures/seeded/topics/orphan-2.md` — valid topic, no inbound links (**orphan 2**).
- `fixtures/seeded/topics/orphan-3.md` — valid topic, no inbound links (**orphan 3**).
- `fixtures/seeded/topics/broken-links.md` — valid topic, body links to `./no-such-file.md` and `../refs/also-missing.md` (**broken-link × 2**), linked from overview.
- `fixtures/seeded/topics/missing-cites-a.md` — topic with 1 offending paragraph (no `[^ref]`) (**missing-citation 1**). Linked from overview.
- `fixtures/seeded/topics/missing-cites-b.md` — topic with 1 offending paragraph (no `[^ref]`) (**missing-citation 2**). Linked from overview. *(One defect is emitted per offending page, so 2 pages = summary count 2.)*
- `fixtures/seeded/topics/dup-a.md` — `id: dup` (**duplicate-id A**).
- `fixtures/seeded/topics/dup-b.md` — `id: dup` (**duplicate-id B**). Both linked from overview.
- `fixtures/seeded/overviews/short-overview.md` — overview linking only 2 distinct pages (**overview-underlinked 1**).
- `fixtures/seeded/overviews/main.md` — overview linking ≥3 distinct pages, used to give orphans' siblings inbound links.

- [ ] **Step 3: Write success-criterion test**

```python
FIXTURES = Path(__file__).parent / "fixtures"


def test_clean_fixture_has_zero_defects():
    result = run([str(FIXTURES / "clean")])
    out = json.loads(result.stdout)
    assert out["defects"] == [], out["defects"]
    assert result.returncode == 0


def test_seeded_fixture_detects_defects():
    result = run([str(FIXTURES / "seeded")])
    out = json.loads(result.stdout)
    s = out["summary"]
    # 9 total seeded defects: 3 orphan + 2 broken-link + 2 missing-citation
    # + (2 pages from duplicate-id pair) + 1 overview-underlinked
    assert s["orphan"] == 3
    assert s["broken-link"] == 2
    assert s["missing-citation"] == 2
    assert s["duplicate-id"] == 2   # both pages flagged
    assert s["overview-underlinked"] == 1
    assert result.returncode == 1


def test_lint_runs_under_one_second_on_100_pages():
    import time as _t
    with tempfile.TemporaryDirectory() as d:
        wiki = Path(d)
        for f in ("refs", "topics", "overviews"):
            (wiki / f).mkdir()
        for i in range(100):
            (wiki / "topics" / f"t{i}.md").write_text(
                "---\nid: t{i}\ntitle: T\ntype: topic\ncreated: 2026-01-01\n"
                "updated: 2026-01-01\nstatus: draft\n---\nbody[^r]\n[^r]: see"
                .replace("{i}", str(i))
            )
        start = _t.perf_counter()
        run([str(wiki)])
        assert _t.perf_counter() - start < 1.0
```

- [ ] **Step 4: Run — fixtures must make tests pass**

Adjust fixtures until tests pass.

- [ ] **Step 5: Commit**

```bash
git add skills/lint/scripts/fixtures/ skills/lint/scripts/test_lint.py
git commit -m "test(lint): fixtures + success-criterion tests"
```

---

## Task 14: Lint skill — SKILL.md

**Files:**
- Create: `skills/lint/SKILL.md`

- [ ] **Step 1: Write SKILL.md**

````markdown
---
name: lint
description: Run deterministic and LLM-judged lint checks on an ultradocs wiki. Triggers on "lint the wiki", "check wiki health", "find orphan pages", "ultradocs lint".
---

# ultradocs:lint

Scan a wiki for structural defects and report findings.

## When to use

- "check wiki health"
- "lint the wiki"
- "find orphans"
- "ultradocs lint"

## Inputs

- `path` (optional): wiki root. Default `docs/`.

## Procedure

1. Resolve wiki path.
2. Invoke: `python3 $CLAUDE_PLUGIN_ROOT/skills/lint/scripts/lint.py <path>`.
3. Parse JSON from stdout. Treat exit 2 as a hard failure.
4. Perform LLM soft checks on pages flagged by the script and on a sample of unflagged pages:
   - Contradictions across pages.
   - Atomicity violation in topics (>400 words, H3+, multi-concept).
   - Overview paragraphs missing citations to linked topics/refs.
5. Emit a consolidated report: machine defects grouped by check, soft findings as a separate section.
6. Offer deterministic fixes where safe: broken-link auto-repair if exactly one same-named file exists elsewhere in the wiki; otherwise leave for the user.

## Outputs

Structured report: summary counts, per-defect details, suggested fixes.

## Do not

- Write fixes automatically beyond the safe set; ask before editing pages.
- Parse the script's stdout as free text — always parse JSON.
````

- [ ] **Step 2: Commit**

```bash
git add skills/lint/SKILL.md
git commit -m "feat(lint): add lint skill"
```

---

## Task 15: Ingest skill — SKILL.md

**Files:**
- Create: `skills/ingest/SKILL.md`

- [ ] **Step 1: Write SKILL.md**

````markdown
---
name: ingest
description: Add a new source to the ultradocs wiki. Triggers on "add this to the wiki", "ingest this", "save this source", "ultradocs ingest <url/path>". Creates a refs page, updates affected topics, touches overviews.
---

# ultradocs:ingest

Ingest a source into the wiki: create a ref, update or create topics, touch overviews.

## When to use

- "add X to the wiki"
- "save this paper/url/doc"
- "ingest this"
- User pastes a URL or file path in a wiki context

## Inputs

- `source`: URL, file path, or pasted text.
- `path` (optional): wiki root. Default `docs/`.

## Procedure

1. Resolve wiki path. If not an ultradocs wiki (no root `CLAUDE.md` + expected folders), stop.
2. Read the source:
   - File: read directly.
   - URL: WebFetch.
   - Pasted text: use as-is.
3. Generate a stable `id` (kebab-case slug of the source title).
4. If `refs/<id>.md` already exists, stop and report "source already ingested".
5. Write `refs/<id>.md` using the ref template (see root CLAUDE.md §7). Body is a 1–3 paragraph summary + key-points list.
6. **Identify affected topics** (heuristic from spec §9.2):
   - Extract 3–8 key terms: title words, tags, prominent noun phrases.
   - Grep each term against `topics/` titles, filenames, tags.
   - ≥2 term hits → update that topic: append a new paragraph citing the new ref; bump `updated`.
   - 0 hits but coherent new concept → create a new topic page citing this ref.
   - Exactly 1 weak hit → emit a note for the curator; do not auto-create.
7. Touch overviews that link to any updated topic: bump `updated`.
8. Append an entry to the root README's "Recent changes" section: `- <YYYY-MM-DD> ingested [<title>](refs/<id>.md)`.
9. Report: what was created, what was updated, any notes for manual review.

## Outputs

Change summary: created/updated files, notes.

## Do not

- Modify existing ref bodies (refs are immutable).
- Use `sources:` front-matter on topic/overview pages.
- Create topics speculatively on weak matches — emit a note instead.
````

- [ ] **Step 2: Commit**

```bash
git add skills/ingest/SKILL.md
git commit -m "feat(ingest): add ingest skill"
```

---

## Task 16: Query skill — SKILL.md

**Files:**
- Create: `skills/query/SKILL.md`

- [ ] **Step 1: Write SKILL.md**

````markdown
---
name: query
description: Answer a question from the ultradocs wiki with cited synthesis. Triggers on "what does the wiki say about X", "search the wiki for Y", "ultradocs query Z". Read-only — never writes.
---

# ultradocs:query

Answer a question by searching the wiki and synthesizing with footnote citations.

## When to use

- "what does wiki say about X"
- "search the wiki for Y"
- "ultradocs query Z"

## Inputs

- `question`: natural-language question.
- `path` (optional): wiki root. Default `docs/`.

## Procedure

1. Resolve wiki path.
2. Extract query terms from the question.
3. Glob + Grep across `refs/`, `topics/`, `overviews/` for relevant pages (match on front-matter `title`, `tags`, body).
4. Rank results: overviews first (synthesize answer), topics next (concrete claims), refs last (provenance).
5. Compose the answer as markdown:
   - Prose citing pages via `[^ref-id]` footnotes pointing to `refs/` pages.
   - Include a "Sources" list at the end with relative links.
6. If relevant topics are missing or thin, emit a **Gap note**: "Wiki has no (or shallow) coverage of <subtopic>; consider ingesting <source suggestion>."

## Outputs

Markdown answer + optional gap note.

## Do not

- Write, create, or modify any wiki file. Queries are read-only.
- Invent facts not present in the wiki. If the wiki is silent, say so and emit a gap note.
- Synthesize from memory instead of grepping the wiki.
````

- [ ] **Step 2: Commit**

```bash
git add skills/query/SKILL.md
git commit -m "feat(query): add query skill"
```

---

## Task 17: Agents

**Files:**
- Create: `agents/ultradocs-curator.md`
- Create: `agents/ultradocs-researcher.md`

- [ ] **Step 1: Write curator**

````markdown
---
name: ultradocs-curator
description: Write-side ultradocs agent. Owns all wiki writes — ingest, lint + fix, restructure, authoring pages. Use when adding sources, maintaining health, merging duplicates, or editing wiki pages.
tools: Read, Write, Edit, Glob, Grep, Bash
---

# ultradocs-curator

You are the write-side caretaker of an ultradocs wiki.

## Responsibilities

- Ingest new sources via `ultradocs:ingest`.
- Run `ultradocs:lint` periodically; fix defects.
- Restructure: merge duplicate topics, split oversized ones, promote topics to overviews.
- Author new pages when a gap is identified.

## Rules

- Always read the target wiki's root `CLAUDE.md` and the relevant folder's `CLAUDE.md` before writing.
- Refs are immutable — only update when the source itself changes.
- Never use `sources:` front-matter on topic or overview pages.
- Keep topics atomic (single noun-phrase title, ≤400 words, no H3+ headings).
- On rename, rewrite all inbound links in the same commit.

## Typical triggers

- "ingest this paper into the wiki"
- "lint docs/ and fix the broken links"
- "merge these two duplicate topics"
- "add a topic page for X"

## Tools available

Read, Write, Edit, Glob, Grep, Bash (for git operations).
````

- [ ] **Step 2: Write researcher**

````markdown
---
name: ultradocs-researcher
description: Read-side ultradocs agent. Answers questions from the wiki, synthesizes with citations, identifies gaps. Never writes — delegates write operations to ultradocs-curator.
tools: Read, Glob, Grep, WebFetch, WebSearch
---

# ultradocs-researcher

You are the read-side analyst of an ultradocs wiki.

## Responsibilities

- Answer user questions via `ultradocs:query`.
- Synthesize answers with `[^ref-id]` footnote citations.
- Identify gaps where the wiki is silent or shallow.
- Suggest external sources worth ingesting, without ingesting them yourself.

## Rules

- **Read-only.** You have no Write or Edit tool. Never attempt to modify wiki files.
- If a user asks you to update or create a page, respond: "I can't write — handing off to ultradocs-curator."
- Never invent facts. If the wiki is silent, say so and emit a gap note.
- Prefer overviews > topics > refs when composing an answer.

## Typical triggers

- "what does the wiki say about X"
- "research Y using ultradocs"
- "find gaps in our coverage of Z"

## Tools available

Read, Glob, Grep, WebFetch, WebSearch. No write tools by design.
````

- [ ] **Step 3: Commit**

```bash
git add agents/
git commit -m "feat(agents): curator and researcher"
```

---

## Task 18: Update plugin.json

**Files:**
- Modify: `.claude-plugin/plugin.json`

- [ ] **Step 1: Verify plugin discovers skills and agents**

Claude Code auto-discovers `skills/` and `agents/` under a plugin root. The existing `plugin.json` has the required `name`, `version`, `description`, `author`. Confirm no changes needed.

```bash
cat .claude-plugin/plugin.json
```

If the Claude Code version running requires explicit declarations, add a `keywords` entry (already done).

- [ ] **Step 2: No commit unless changed**

---

## Task 19: End-to-end smoke test

**Files:** none (manual verification)

- [ ] **Step 1: Reinstall plugin**

```bash
# In Claude Code:
/plugin uninstall ultradocs
/plugin marketplace add /Users/dknathalage/repos/ultradocs
/plugin install ultradocs@ultradocs
# restart Claude Code session
```

- [ ] **Step 2: Run init on a scratch dir**

```bash
mkdir -p /tmp/wiki-smoke
```

In Claude Code: "set up ultradocs at /tmp/wiki-smoke".

Expected: `ultradocs:init` fires, scaffold matches spec §4 layout.

- [ ] **Step 3: Ingest a test source**

Give Claude a small file or URL and say "ingest this into /tmp/wiki-smoke".

Expected: `ultradocs:ingest` fires, writes a `refs/*.md`, possibly creates a topic, appends README recent-changes.

- [ ] **Step 4: Query**

"what does the wiki at /tmp/wiki-smoke say about <topic from source>?"

Expected: `ultradocs:query` returns cited markdown answer.

- [ ] **Step 5: Lint**

"lint /tmp/wiki-smoke"

Expected: `ultradocs:lint` runs `lint.py`, parses JSON, reports clean or defects.

- [ ] **Step 6: Run lint script directly**

```bash
python3 /Users/dknathalage/repos/ultradocs/skills/lint/scripts/lint.py /tmp/wiki-smoke
```

Expected: valid JSON on stdout, exit 0.

- [ ] **Step 7: Run full unittest suite**

```bash
cd /Users/dknathalage/repos/ultradocs/skills/lint/scripts
python3 -m unittest test_lint.py -v
```

Expected: all tests pass.

- [ ] **Step 8: Final commit + tag**

```bash
git tag v0.0.1
git log --oneline
```

---

## Notes for the implementer

- **Test-first.** Every lint check has a failing test written before the implementation.
- **Stdlib only** for `lint.py` and `test_lint.py`. No `pip install` allowed. If you feel you need a library, use regex + `pathlib` + `datetime` + `json` + `argparse` instead.
- **Commit after every step** with the exact message in the plan (or a close variant). Frequent small commits are the contract.
- **Do not add features** beyond what each task specifies. If you think something is missing, flag it and stop — do not invent scope.
- **Plugin invocation.** `$CLAUDE_PLUGIN_ROOT` is set by Claude Code to the plugin install dir at runtime. Use it in SKILL.md procedures when invoking scripts.
- **Trigger phrases** in SKILL.md `description` fields are what Claude Code matches on. Keep them varied and natural-language; no slash-command style.
