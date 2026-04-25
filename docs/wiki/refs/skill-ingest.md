---
id: skill-ingest
title: ultradocs:ingest Skill
type: ref
created: 2026-04-25
updated: 2026-04-25
sources: [skills/ingest/SKILL.md]
tags: [skill, ingest, refs, topics]
status: stable
---

# ultradocs:ingest Skill

Adds a source (URL, file path, or pasted text) to a wiki: writes a `refs/<id>.md`, updates or creates affected topic pages, touches overviews, and logs the change to README. Owned by the `ultradocs-curator` agent.

Procedure: validate wiki path, read source (file/WebFetch/inline), generate kebab-case `id` slug, refuse if ref already exists, write summary to `refs/<id>.md`. Then identify affected topics via key-term grep heuristic — extract 3–8 terms, search `topics/` titles/filenames/tags. ≥2 hits → update topic with new citation; 0 hits but coherent new concept → create new topic; exactly 1 weak hit → emit curator note instead of auto-creating. Bump `updated` on overviews linking changed topics. Append a dated entry to README's "Recent changes" section.

Constraints: ref bodies are immutable on subsequent ingests; never use `sources:` front-matter on topics/overviews; do not create topics speculatively on weak matches.

## Key points

- Three input modes: URL, file path, pasted text.
- Stable id = kebab-case slug of source title.
- Topic-update heuristic: 0 / 1 weak / ≥2 hits drives create / note / update.
- README "Recent changes" gets one line per ingest.
- Refs are write-once; re-ingest is refused.
