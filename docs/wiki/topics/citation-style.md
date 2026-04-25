---
id: citation-style
title: Citation Style
type: topic
created: 2026-04-25
updated: 2026-04-25
tags: [citations, footnotes, links]
status: stable
---

# Citation Style

Citations in an ultradocs wiki use markdown footnote syntax `[^ref-id]`, where `ref-id` matches the `id` front-matter field of a page in `refs/`. Every non-trivial claim in `topics/` and `overviews/` must cite at least one ref via this footnote form[^ultradocs-plugin-design].

Cross-page links use relative markdown only, with paths like `../topics/<slug>.md`. Wikilinks and bare HTTP URLs as cross-references are not used; HTTP URLs belong only inside `sources:` of a ref page[^ultradocs-plugin-design].

The `query` skill ranks results overviews-first, then topics, then refs, and synthesizes answers with the same `[^ref-id]` footnotes pointing back to refs pages, plus a "Sources" list at the end of each answer[^skill-query]. Lint flags topic or overview paragraphs that lack a footnote citation as `missing-citation` defects[^skill-lint].

[^ultradocs-plugin-design]: See [refs/ultradocs-plugin-design.md](../refs/ultradocs-plugin-design.md).
[^skill-query]: See [refs/skill-query.md](../refs/skill-query.md).
[^skill-lint]: See [refs/skill-lint.md](../refs/skill-lint.md).
