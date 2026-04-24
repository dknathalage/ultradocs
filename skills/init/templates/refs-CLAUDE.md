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

1–3 paragraph summary. Capture the key claims, methods, and conclusions.

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
