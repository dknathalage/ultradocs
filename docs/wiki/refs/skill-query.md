---
id: skill-query
title: ultradocs:query Skill
type: ref
created: 2026-04-25
updated: 2026-04-25
sources: [skills/query/SKILL.md]
tags: [skill, query, read-only]
status: stable
---

# ultradocs:query Skill

Answers a natural-language question by searching the wiki and synthesizing a response with footnote citations. Owned by the `ultradocs-researcher` agent. Read-only — never writes any wiki file.

Procedure: resolve wiki path, extract terms from the question, Glob+Grep across `refs/`, `topics/`, `overviews/` matching front-matter title, tags, and body. Rank: overviews first (synthesis), topics next (concrete claims), refs last (provenance). Compose markdown answer citing pages via `[^ref-id]` footnotes pointing to refs pages, with a "Sources" list at the end. If wiki coverage is missing or thin, emit a "Gap note" suggesting what to ingest.

Constraints: never write, create, or modify wiki files; never invent facts not present in the wiki; never synthesize from memory instead of grepping.

## Key points

- Read-only: no Write/Edit tools used.
- Ranking: overviews > topics > refs.
- Citations via `[^ref-id]` footnotes.
- Gap notes flag missing coverage without writing.
- Handoff to `ultradocs-curator` if user requests a write.
