---
id: agent-curator
title: ultradocs-curator Agent
type: ref
created: 2026-04-25
updated: 2026-04-25
sources: [agents/ultradocs-curator.md]
tags: [agent, curator, write-side]
status: stable
---

# ultradocs-curator Agent

Write-side caretaker of an ultradocs wiki. Owns all wiki writes: ingesting sources, running lint and applying fixes, restructuring (merging duplicate topics, splitting oversized ones, promoting topics to overviews), and authoring new pages when gaps are identified. Tools: Read, Write, Edit, Glob, Grep, Bash (for git).

Operating rules: always read the target wiki's root `CLAUDE.md` and the relevant folder's `CLAUDE.md` before writing; treat refs as immutable except when the source itself changes; never use `sources:` front-matter on topics or overviews; keep topics atomic (single noun-phrase title, ≤400 words, no H3+ headings); on rename, rewrite all inbound links in the same commit.

Triggered by phrases like "ingest this paper", "lint docs and fix the broken links", "merge these duplicate topics", "add a topic page for X".

## Key points

- Sole holder of Write/Edit tools.
- Owns `ultradocs:ingest` and `ultradocs:lint` skills.
- Reads CLAUDE.md before any write.
- Performs link rewrites atomically with renames.
