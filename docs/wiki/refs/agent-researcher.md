---
id: agent-researcher
title: ultradocs-researcher Agent
type: ref
created: 2026-04-25
updated: 2026-04-25
sources: [agents/ultradocs-researcher.md]
tags: [agent, researcher, read-side]
status: stable
---

# ultradocs-researcher Agent

Read-side analyst of an ultradocs wiki. Answers questions, synthesizes responses with `[^ref-id]` footnote citations, identifies gaps in coverage, and suggests external sources worth ingesting — without ingesting them itself. Tools: Read, Glob, Grep, WebFetch, WebSearch. No write tools by design.

Operating rules: read-only — never attempt to modify wiki files; if a user requests a write, respond "I can't write — handing off to ultradocs-curator"; never invent facts (if the wiki is silent, say so and emit a gap note); prefer overviews over topics over refs when composing an answer.

Triggered by phrases like "what does the wiki say about X", "research Y using ultradocs", "find gaps in our coverage of Z".

## Key points

- No Write or Edit tool — enforced by tool list.
- Owns `ultradocs:query` skill.
- Hands off writes to `ultradocs-curator`.
- Composition preference: overviews > topics > refs.
- Emits gap notes for missing coverage.
