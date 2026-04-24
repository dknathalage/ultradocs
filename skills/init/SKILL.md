---
name: init
description: Initialize a new ultradocs wiki at a given path. Triggers on "initialize wiki", "set up ultradocs", "create a wiki at X", "ultradocs init". Accepts an optional path argument (default `docs/`, use `.` for cwd).
---

# ultradocs:init

Scaffold a new wiki at the target path with the canonical layout and CLAUDE.md/README.md instruction files.

## When to use

User says any of:
- "initialize a wiki"
- "set up ultradocs here"
- "create a wiki at ./somepath"
- "ultradocs init [path]"

## Inputs

- `path` (optional): target directory. Default `docs/`. Use `.` for current working directory.

## Procedure

1. Resolve target path. If relative, resolve against cwd. If `.`, use cwd.
2. If the target already contains any of `CLAUDE.md`, `refs/`, `topics/`, `overviews/`, stop and report: "wiki already exists at <path>; refusing to overwrite".
3. Create directories:
   - `<path>/refs/`
   - `<path>/topics/`
   - `<path>/overviews/`
4. Copy templates from `$CLAUDE_PLUGIN_ROOT/skills/init/templates/` into target:
   - `root-CLAUDE.md` → `<path>/CLAUDE.md`
   - `root-README.md` → `<path>/README.md`, substituting `{{wiki_name}}` with the basename of `<path>` (or the repo name if `<path>` is `.`).
   - `refs-CLAUDE.md` → `<path>/refs/CLAUDE.md`
   - `topics-CLAUDE.md` → `<path>/topics/CLAUDE.md`
   - `overviews-CLAUDE.md` → `<path>/overviews/CLAUDE.md`
5. Report success with a tree of what was created.

## Outputs

Confirmation message plus the created file list.

## Do not

- Write any pages into `refs/`, `topics/`, `overviews/` — scaffolding only.
- Overwrite existing files.
