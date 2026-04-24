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
