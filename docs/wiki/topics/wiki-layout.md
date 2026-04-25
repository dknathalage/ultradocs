---
id: wiki-layout
title: Wiki Layout
type: topic
created: 2026-04-25
updated: 2026-04-25
tags: [structure, layout, scaffolding]
status: stable
---

# Wiki Layout

An ultradocs wiki is a directory containing a root `CLAUDE.md` (AI instructions and schema), a root `README.md` (human + AI entry point with stats and recent-changes log), and three subfolders for the three page types: `refs/`, `topics/`, and `overviews/`. Each subfolder also carries its own `CLAUDE.md` describing role, template, rules, and anti-patterns for that page type[^ultradocs-plugin-design].

The layout is created by the `ultradocs:init` skill, which copies five templates into place and refuses to overwrite any existing wiki file[^skill-init]. The default install path is `docs/`; passing `.` resolves to the current working directory[^skill-init].

`CLAUDE.md` files are AI-only — Claude reads them before writing — while `README.md` is the human-facing entry point with navigation and stats[^ultradocs-plugin-design]. Schema rules live in the root `CLAUDE.md`; there is no separate `schema.md` file[^ultradocs-plugin-design].

[^ultradocs-plugin-design]: See [refs/ultradocs-plugin-design.md](../refs/ultradocs-plugin-design.md).
[^skill-init]: See [refs/skill-init.md](../refs/skill-init.md).
