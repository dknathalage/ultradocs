---
id: skill-init
title: ultradocs:init Skill
type: ref
created: 2026-04-25
updated: 2026-04-25
sources: [skills/init/SKILL.md]
tags: [skill, init, scaffolding]
status: stable
---

# ultradocs:init Skill

Scaffolds a new wiki at a target path with the canonical layout. Triggers on phrases like "initialize a wiki", "set up ultradocs here", "create a wiki at <path>". Optional `path` input defaults to `docs/`; `.` resolves to cwd.

Procedure: resolve target path; refuse if `CLAUDE.md`, `refs/`, `topics/`, or `overviews/` already exist; create the three subfolders; copy five templates from `$CLAUDE_PLUGIN_ROOT/skills/init/templates/` (root CLAUDE.md, README.md with `{{wiki_name}}` substitution, and one CLAUDE.md per folder).

The skill writes scaffolding only — never authors pages into `refs/`, `topics/`, or `overviews/`, and never overwrites existing files.

## Key points

- Default path: `docs/`. Use `.` for cwd.
- Refuses to overwrite existing wiki layout.
- Substitutes `{{wiki_name}}` in README with basename of path (or repo name).
- Five templates copied; nothing else written.
