---
id: lint-rules
title: Lint Rules
type: topic
created: 2026-04-25
updated: 2026-04-25
tags: [lint, defects, quality]
status: stable
---

# Lint Rules

The `ultradocs:lint` skill enforces a fixed set of defects in two tiers: machine-checkable rules implemented by a deterministic Python script, and soft rules judged by Claude on flagged or sampled pages[^skill-lint].

Machine-checkable rules cover orphan pages (no inbound markdown links, README excluded), broken relative links, duplicate `id` front-matter values, missing `[^ref]` citations in topic/overview paragraphs, overviews under-linked (fewer than 3 distinct topic/ref links), stale refs (status `stable`, `updated` >90 days, local source mtime newer), and front-matter violations (missing keys, `sources` on topics/overviews, `type` mismatched with folder)[^ultradocs-plugin-design]. The script returns these as JSON with stable check identifiers and exit codes 0 (clean), 1 (defects), or 2 (usage error)[^skill-lint].

Soft rules are LLM-judged: cross-page contradictions, atomicity violations in topics, and overviews whose substantive paragraphs lack citations to linked topics or refs[^ultradocs-plugin-design]. Auto-fix is restricted to broken-link repair when exactly one same-named file exists elsewhere in the wiki[^skill-lint].

[^ultradocs-plugin-design]: See [refs/ultradocs-plugin-design.md](../refs/ultradocs-plugin-design.md).
[^skill-lint]: See [refs/skill-lint.md](../refs/skill-lint.md).
