---
id: ultradocs-plugin-design
title: ultradocs Plugin — Design Spec
type: ref
created: 2026-04-25
updated: 2026-04-25
sources: [docs/superpowers/specs/2026-04-25-ultradocs-plugin-design.md]
tags: [spec, design, architecture]
status: stable
---

# ultradocs Plugin — Design Spec

Authoritative design document for the ultradocs Claude Code plugin (v0.0.1). Defines a plugin that lets Claude build and maintain a persistent, interlinked markdown wiki as a long-term knowledge store. Dual-use: developer source-code documentation and personal second brain. The wiki itself is the retrieval index — no embeddings, no RAG. Inspired by Karpathy's persistent-wiki-over-RAG pattern and Zettelkasten atomicity.

Specifies wiki layout (`refs/`, `topics/`, `overviews/` plus root `CLAUDE.md`/`README.md`), page model (three types with YAML front-matter), four skills (`init`, `ingest`, `query`, `lint`) as the only interface, two agents (`ultradocs-curator` write-side, `ultradocs-researcher` read-side), citation style (`[^ref-id]` footnotes), link style (relative markdown only), and lint rules split into machine-checkable (deterministic Python script) and soft (LLM-judged).

Non-goals for v0.0.1: no RAG/embeddings, no AGENTS.md/GEMINI.md, no multi-wiki registry, no automation hooks, no UI beyond Claude Code + GitHub rendering.

## Key points

- Wiki is the index; no vector search.
- Skills-only interface; no slash commands, no hooks in v0.
- Filename = link target; `id` = stable cross-reference for citations.
- Refs are immutable once written; topics/overviews evolve.
- Topic atomicity: single noun-phrase title, ≤400 words, no H3+ headings.
- Overviews must link ≥3 distinct topic/ref pages.
- Lint script: Python stdlib only, JSON-out, exit codes 0/1/2.
- Agents non-overlapping: curator owns writes, researcher is read-only.
