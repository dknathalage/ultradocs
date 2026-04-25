---
id: ultradocs-plugin
title: ultradocs Plugin Overview
type: overview
created: 2026-04-25
updated: 2026-04-25
tags: [overview, plugin, architecture]
status: stable
---

# ultradocs Plugin Overview

ultradocs is a Claude Code plugin that turns a markdown directory into a persistent, interlinked knowledge wiki maintained by Claude. The wiki itself is the retrieval index — no embeddings, no RAG. Inspired by Karpathy's persistent-wiki-over-RAG pattern and Zettelkasten atomicity[^ultradocs-plugin-design].

The structural foundation is the [wiki-layout](../topics/wiki-layout.md): a root `CLAUDE.md` carrying schema and AI instructions, a `README.md` for humans, and three subfolders — `refs/` for external sources, `topics/` for atomic concepts, `overviews/` for narrative aggregations — each with its own folder-level `CLAUDE.md`. Pages share a uniform [front-matter-schema](../topics/front-matter-schema.md) (id, title, type, dates, tags, status) where `sources` is exclusive to refs[^ultradocs-plugin-design].

Interlinking is enforced by [citation-style](../topics/citation-style.md): relative markdown links between pages and `[^ref-id]` footnote citations from topics and overviews back to refs. Topic-level discipline is enforced by [topic-atomicity](../topics/topic-atomicity.md) — single noun-phrase titles, ≤400 words, no H3+ headings — which keeps the wiki grep-friendly without vector search[^ultradocs-plugin-design].

Four skills cover the operational loop: `ultradocs:init` scaffolds the layout[^skill-init], `ultradocs:ingest` adds sources and updates affected topics[^skill-ingest], `ultradocs:query` answers questions read-only with citations[^skill-query], and `ultradocs:lint` enforces wiki health via [lint-rules](../topics/lint-rules.md) backed by a stdlib Python script following the [script-policy](../topics/script-policy.md)[^skill-lint].

Two agents own these skills under the [agent-split](../topics/agent-split.md): `ultradocs-curator` holds all write tools and runs ingest/lint/restructure[^agent-curator], while `ultradocs-researcher` is read-only and runs query, handing off any write request to the curator[^agent-researcher].

[^ultradocs-plugin-design]: See [refs/ultradocs-plugin-design.md](../refs/ultradocs-plugin-design.md).
[^skill-init]: See [refs/skill-init.md](../refs/skill-init.md).
[^skill-ingest]: See [refs/skill-ingest.md](../refs/skill-ingest.md).
[^skill-query]: See [refs/skill-query.md](../refs/skill-query.md).
[^skill-lint]: See [refs/skill-lint.md](../refs/skill-lint.md).
[^agent-curator]: See [refs/agent-curator.md](../refs/agent-curator.md).
[^agent-researcher]: See [refs/agent-researcher.md](../refs/agent-researcher.md).
