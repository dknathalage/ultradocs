---
id: skill-lint
title: ultradocs:lint Skill
type: ref
created: 2026-04-25
updated: 2026-04-25
sources: [skills/lint/SKILL.md, skills/lint/scripts/lint.py]
tags: [skill, lint, defects, script]
status: stable
---

# ultradocs:lint Skill

Scans a wiki for structural defects and reports findings. Two-stage: a deterministic Python script (`skills/lint/scripts/lint.py`, stdlib-only) emits JSON; the skill parses, then performs LLM soft checks on flagged and sampled pages. Owned by `ultradocs-curator`.

Procedure: invoke `python3 $CLAUDE_PLUGIN_ROOT/skills/lint/scripts/lint.py <path>`; parse JSON from stdout; treat exit 2 as hard failure. Run soft checks for cross-page contradictions, topic atomicity violations, and overview paragraphs missing citations. Emit a consolidated report grouping machine defects by check, with soft findings as a separate section. Offer deterministic fixes only when safe (e.g., broken-link auto-repair if exactly one same-named file exists elsewhere); otherwise defer to user.

Constraints: skill must parse JSON, never free text; no automatic writes beyond the safe fix set.

## Key points

- Machine checks: orphan, broken-link, duplicate-id, missing-citation, overview-underlinked, stale, frontmatter-violation.
- Soft checks: contradictions, atomicity, overview citation quality.
- Exit codes: 0 clean, 1 defects, 2 usage error.
- Auto-fix limited to safe broken-link repair.
- Script: Python stdlib only; no `pip install`.
