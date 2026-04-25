---
id: agent-split
title: Curator vs Researcher Agent Split
type: topic
created: 2026-04-25
updated: 2026-04-25
tags: [agents, separation-of-concerns]
status: stable
---

# Curator vs Researcher Agent Split

ultradocs ships two non-overlapping agents. `ultradocs-curator` is the write-side caretaker — it owns ingest, lint-and-fix, restructure, and authoring, and holds the Write, Edit, Read, Glob, Grep, and Bash tools[^agent-curator]. `ultradocs-researcher` is the read-side analyst — it answers questions with `[^ref-id]` citations, identifies gaps, and suggests external sources to ingest, but holds only Read, Glob, Grep, WebFetch, and WebSearch tools, with no write capability[^agent-researcher].

The split is enforced through tool lists rather than convention. The researcher physically cannot modify wiki files; if a user requests a write, the researcher hands off to the curator[^agent-researcher]. The design keeps the agent surface lean — two agents, no third — and makes the read/write boundary auditable, as summarized in the [ultradocs Plugin Overview](../overviews/ultradocs-plugin.md)[^ultradocs-plugin-design].

[^agent-curator]: See [refs/agent-curator.md](../refs/agent-curator.md).
[^agent-researcher]: See [refs/agent-researcher.md](../refs/agent-researcher.md).
[^ultradocs-plugin-design]: See [refs/ultradocs-plugin-design.md](../refs/ultradocs-plugin-design.md).
