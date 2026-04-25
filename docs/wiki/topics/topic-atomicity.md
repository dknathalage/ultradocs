---
id: topic-atomicity
title: Topic Atomicity
type: topic
created: 2026-04-25
updated: 2026-04-25
tags: [topics, zettelkasten, atomicity]
status: stable
---

# Topic Atomicity

Pages in `topics/` are atomic concept notes — one idea per page. The operational definition is concrete: a single noun-phrase subject in `title`, body length ≤400 words, no headings deeper than H2, and a title that expresses one idea. If a writer feels the urge to write "X and Y" in a topic title, the page must be split[^ultradocs-plugin-design].

Atomicity is enforced via two paths. The `ultradocs-curator` agent must keep topics atomic on every write[^agent-curator], and the `lint` skill performs LLM-judged soft checks for atomicity violations — multiple concepts, >400 words, or H3+ headings — on flagged or sampled topic pages[^skill-lint].

Atomicity is the design lever that makes the wiki itself usable as a retrieval index: small focused pages compose cleanly into overviews and resolve cleanly under grep, removing the need for embeddings or RAG[^ultradocs-plugin-design].

[^ultradocs-plugin-design]: See [refs/ultradocs-plugin-design.md](../refs/ultradocs-plugin-design.md).
[^agent-curator]: See [refs/agent-curator.md](../refs/agent-curator.md).
[^skill-lint]: See [refs/skill-lint.md](../refs/skill-lint.md).
