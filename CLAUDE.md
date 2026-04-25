# Developing ultradocs

> Instructions for Claude (and humans) working **on** the plugin itself, not on a wiki it manages.

If you're a user or AI agent operating a wiki, follow the `CLAUDE.md` inside that wiki, not this one.

---

## What this repo is

A Claude Code plugin. Not a library. Not a CLI tool (the lint script is the only Python in the repo, and it's invoked through a skill). The deliverables are markdown files that Claude Code loads.

```
.claude-plugin/        plugin manifest + local marketplace
skills/<name>/         each skill is a directory with SKILL.md + optional scripts/templates
agents/                two markdown files: curator (write) and researcher (read)
docs/superpowers/      specs and plans (source of truth for every change)
```

The spec lives at `docs/superpowers/specs/2026-04-25-ultradocs-plugin-design.md`. Read it before changing anything structural.

---

## Local development loop

Test changes against a live Claude Code session:

```bash
# fresh dev session that picks up edits without reinstall
claude --plugin-dir /Users/dknathalage/repos/ultradocs
```

After edits to `SKILL.md` or `agents/*.md`, reload inside Claude Code:

```
/reload-plugins
```

For installed-mode testing:

```
/plugin uninstall ultradocs
/plugin marketplace add /Users/dknathalage/repos/ultradocs
/plugin install ultradocs@ultradocs
# restart the session
```

---

## Lint script

`skills/lint/scripts/lint.py` is the only executable code in the repo. It is the deterministic half of `ultradocs:lint`; the LLM half lives in the skill procedure.

**Run the test suite:**

```bash
cd skills/lint/scripts
python3 -m unittest test_lint.py -v
```

**Run the script against a real wiki:**

```bash
python3 skills/lint/scripts/lint.py /path/to/wiki
```

**Stdlib-only rule.** No `pip install`. Allowed imports: `argparse`, `json`, `sys`, `pathlib`, `re`, `collections`, `datetime`, `os`, `time`, `tempfile`, `subprocess`, `unittest`. If you reach for anything else, write the workaround instead.

Test fixtures:

- `skills/lint/scripts/fixtures/clean/` — must always lint clean.
- `skills/lint/scripts/fixtures/seeded/` — has exactly the defects asserted by `test_seeded_fixture_detects_defects`. If you change a check, check whether the seeded counts still hold.

---

## Adding a new lint check

TDD, no exceptions. Pattern:

1. Add a check id (kebab-case) to `report["summary"]` initialization in `main()`.
2. Write a failing test in `test_lint.py` that creates a tiny temp wiki, asserts the new check fires.
3. Run `python3 -m unittest test_lint.py -v` — confirm it fails.
4. Add a `check_<thing>(pages, ...)` function returning a list of defect dicts (`check`, `severity`, `page`, `message`, `data`).
5. Wire it into `main()`: `if enabled("<id>"): all_defects.extend(check_thing(...))`.
6. Re-run tests, confirm pass.
7. Update `skills/lint/SKILL.md` rules list and the spec/plan if needed.
8. Commit with `feat(lint): <id> check`.

---

## Adding a new skill

1. Create `skills/<name>/SKILL.md` with YAML front-matter:
   ```yaml
   ---
   name: <name>
   description: <natural-language trigger phrases — no slash-command syntax>
   ---
   ```
2. Body sections: **When to use**, **Inputs**, **Procedure**, **Outputs**, **Do not**.
3. If the skill needs scripts, put them under `skills/<name>/scripts/` — **skill-local, not shared**. Duplication is fine.
4. If it needs templates, put them under `skills/<name>/templates/`.
5. Update `agents/*.md` to reference the new skill if appropriate.
6. Update spec §6 and plan if scope changes.

---

## Conventions

- **No slash-command-style trigger phrases.** Trigger phrases in `description` fields must be natural language ("initialize a wiki", "lint the docs"), not "/ultradocs init".
- **Markdown over HTML.** Templates and SKILL.md content must render cleanly on GitHub.
- **Plan before code.** Non-trivial changes need a plan in `docs/superpowers/plans/`. Use the `superpowers:writing-plans` skill.
- **Spec is authoritative.** If code disagrees with spec, update one or the other intentionally. Don't drift.
- **Lean agents.** Curator writes, researcher reads. No third agent without a written justification in the spec.
- **YAGNI.** v0 ships a thin slice of ingest + query + lint. Don't add features without a spec update.

---

## Commit style

Conventional commits, scoped by area:

- `feat(init): ...`, `feat(lint): ...`, `feat(ingest): ...`, `feat(query): ...`, `feat(agents): ...`
- `fix(lint): ...`
- `docs(spec): ...`, `docs(plan): ...`
- `test(lint): ...`
- `chore: ...`

One logical change per commit. Tests in the same commit as the code they test (TDD: failing test → impl → green test all land together when committed at the end of the cycle).

---

## Current architecture decisions

(Recap from the spec — do not change these without amending the spec.)

- **Skills-only interface.** No slash commands, no hooks. v0.
- **Wiki layout** is `refs/` + `topics/` + `overviews/` plus root `CLAUDE.md` and `README.md`. No `schema.md` — schema lives in root `CLAUDE.md`.
- **Filename = link target.** `id` in front-matter is for citation keys and provenance, not for resolving links.
- **Refs are immutable.** Topics/overviews evolve.
- **Lint is JSON-out.** The skill parses; the script never speaks free text.

---

## Releasing

Fully automated via `release-please` and the `dknathalage-release-bot` GitHub App. Do not bump `version`, write `CHANGELOG.md`, or create tags by hand.

1. Land conventional-commit PRs on `main`. `feat:` → minor bump, `fix:` → patch bump, `feat!:` / `BREAKING CHANGE:` → major (capped to minor while pre-1.0).
2. The push to `main` triggers `.github/workflows/release-please.yml`. The workflow mints a short-lived App token, opens (or updates) a release PR that bumps `version` in `.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json`, updates `CHANGELOG.md`, and updates `.release-please-manifest.json`.
3. The same workflow enables auto-merge on the release PR. Required status checks run (the App identity triggers them, unlike GITHUB_TOKEN); when they pass, GitHub squash-merges the PR. The App bypasses the code-owner review requirement; it does **not** bypass status checks.
4. The merge is itself a push to `main`, so the workflow runs again — release-please detects the merged release commit and creates the tag (`vX.Y.Z`) plus a GitHub Release.

Net: zero manual steps after a `feat:` / `fix:` lands on `main`. The changelog is whatever the conventional-commit history produces — curate by writing better commit messages.

---

## When stuck

- Re-read the spec. Most "should I do X" questions are already answered there.
- The plan (`docs/superpowers/plans/`) is your task list. If your work doesn't map to a planned task, write a new plan first.
- Use `superpowers:brainstorming` for design questions before touching code.
