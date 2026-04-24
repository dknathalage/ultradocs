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
