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
