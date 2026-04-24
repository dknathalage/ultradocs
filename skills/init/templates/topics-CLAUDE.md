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
