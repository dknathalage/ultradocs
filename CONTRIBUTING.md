# Contributing to ultradocs

Thanks for your interest. This document explains how to propose changes safely. If you're operating a wiki built with this plugin, you don't need this file — see the `CLAUDE.md` inside your wiki instead.

---

## Ground rules

1. **Read the spec first.** `docs/superpowers/specs/2026-04-25-ultradocs-plugin-design.md` is authoritative. Code that contradicts the spec is a bug in one of the two — don't drift silently.
2. **Plan non-trivial changes.** New skills, new lint checks, structural changes: write a plan in `docs/superpowers/plans/` before opening a PR. Use the `superpowers:writing-plans` skill or follow the existing plans as templates.
3. **Stdlib-only Python.** `skills/lint/scripts/lint.py` and its tests must use only the Python standard library. No `pip install`, no `requirements.txt`. The allowed import list is in `CLAUDE.md`.
4. **Natural-language trigger phrases.** Skill `description:` fields must read like instructions to a human ("initialize a wiki", "lint the docs"), not slash-command syntax. Slash commands are not part of v0.
5. **Markdown over HTML.** Templates and skills must render cleanly on GitHub.

## Workflow

```bash
# 1. fork on GitHub, then:
git clone git@github.com:<your-fork>/ultradocs.git
cd ultradocs

# 2. branch
git checkout -b feat/<short-name>

# 3. make changes; if you touched the lint script, run tests:
cd skills/lint/scripts
python3 -m unittest test_lint.py -v

# 4. smoke-test plugin behaviour in a Claude Code session:
claude --plugin-dir "$PWD"
# inside Claude Code: /reload-plugins after edits

# 5. commit using conventional commits, scoped by area:
#    feat(lint): ...   feat(ingest): ...   fix(query): ...
#    docs(spec): ...   test(lint): ...     chore: ...

# 6. push and open a PR against main
```

## What CI runs on your PR

Two workflows, both triggered by `pull_request` (so fork PRs run with read-only `GITHUB_TOKEN` and no access to repository secrets):

| Workflow | What it checks |
|----------|---------------|
| `test.yml` | `unittest` suite for `lint.py`; `lint.py` against the clean fixture |
| `validate.yml` | `plugin.json` / `marketplace.json` parse as JSON; every `SKILL.md` has `name` + `description` front-matter; `description` doesn't use slash-command syntax; no large unexpected binaries |
| `commitlint.yml` | PR **title** is a valid Conventional Commit (used as the squash-merge subject); every commit in the PR is a valid Conventional Commit |

All must pass before review. They don't run privileged code from forks — actions are pinned by commit SHA, secrets are not exposed, and we use `pull_request` (not `pull_request_target`).

### Conventional commit format

```
<type>(<optional scope>): <subject>

[optional body]

[optional footer(s)]
```

Allowed types: `feat`, `fix`, `docs`, `test`, `chore`, `refactor`, `perf`, `build`, `ci`, `style`, `revert`. Suggested scopes: `init`, `ingest`, `query`, `lint`, `agents`, `spec`, `plan`, `ci`. Header ≤ 100 chars.

A commit drives the version bump:

| Commit | Bump (pre-1.0) | Bump (post-1.0) |
|--------|---------------|-----------------|
| `feat: ...` or `feat!: ...` (breaking) | minor | major |
| `feat: ...` (non-breaking) | minor | minor |
| `fix: ...` | (no bump) | patch |
| anything else | (no bump) | (no bump) |

Pre-1.0 we cap major bumps to minor (see `bump-minor-pre-major` in `release-please-config.json`).

## Releases

Releases are fully automated via [`release-please`](https://github.com/googleapis/release-please) and the `dknathalage-release-bot` GitHub App. There are **no manual steps** for the maintainer once a `feat:` / `fix:` lands on `main`.

1. Conventional commits land on `main` (via reviewed PR — that part is still gated).
2. The push to `main` triggers `.github/workflows/release-please.yml`. The workflow:
   - mints a short-lived (~1h) installation token from the App,
   - asks `release-please` to open / update a release PR that bumps `version` in `.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json`, writes/updates `CHANGELOG.md`, and bumps `.release-please-manifest.json`,
   - enables auto-merge (squash) on the release PR.
3. Required status checks run on the release PR (the App identity triggers them, unlike `GITHUB_TOKEN`). When they pass, GitHub auto-merges.
4. The merge to `main` re-runs the workflow, which detects the release commit and creates the Git tag (`vX.Y.Z`) plus a GitHub Release.

The App is a **bypass actor for code-owner review**. It does **not** bypass required status checks — those still gate every release.

You should never bump versions, tag, or write the changelog by hand. The changelog is whatever the conventional commits produce — curate by writing better commit messages.

## Review

- All PRs need at least one approving review from a code owner (see `.github/CODEOWNERS`).
- Stale reviews are dismissed automatically when you push new commits — re-request review after addressing feedback.
- The maintainer squash-merges; don't worry about cleaning history.

## Adding a new skill

See `CLAUDE.md` → "Adding a new skill". TL;DR: `skills/<name>/SKILL.md` with `name` + `description` front-matter, body sections (When to use / Inputs / Procedure / Outputs / Do not), skill-local scripts under `skills/<name>/scripts/`. Update `agents/*.md` if the new skill should be discoverable by curator or researcher.

## Adding a lint check

See `CLAUDE.md` → "Adding a new lint check". TDD only:

1. Failing test in `test_lint.py`.
2. New `check_<thing>` function in `lint.py`.
3. Wire it into `main()` behind `enabled("<id>")`.
4. Re-run tests until green.
5. Update `skills/lint/SKILL.md` rules list.

## Reporting security issues

Don't open a public issue for security reports. Email the maintainer (see commit history for the address). Include steps to reproduce and the affected version.

## Branch protection (for maintainers)

`main` is protected:

- 1 approving review required, dismiss stale reviews on push, require code-owner review, require last-push approval.
- Force pushes blocked, deletions blocked.
- Required status checks (already configured via `gh api`):
  - `lint script unittest`
  - `plugin manifests`
  - `skill front-matter`
  - `no unexpected binaries`
  - `pr title is conventional`
  - `commits are conventional`
- Actions setting: "Allow GitHub Actions to create and approve pull requests" is enabled (required for `release-please` to open release PRs).

Suggested follow-ups (not yet enabled):

- Enable **Require conversation resolution before merging**.
- Enable **Include administrators** so admins are also gated by checks/reviews.
- Enable **Require signed commits** if maintainers can comply.
