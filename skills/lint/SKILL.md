---
name: lint
description: Run deterministic and LLM-judged lint checks on an ultradocs wiki. Triggers on "lint the wiki", "check wiki health", "find orphan pages", "ultradocs lint".
---

# ultradocs:lint

Scan a wiki for structural defects and report findings.

## When to use

- "check wiki health"
- "lint the wiki"
- "find orphans"
- "ultradocs lint"

## Inputs

- `path` (optional): wiki root. Default `docs/`.

## Procedure

1. Resolve wiki path.
2. Invoke: `python3 $CLAUDE_PLUGIN_ROOT/skills/lint/scripts/lint.py <path>`.
3. Parse JSON from stdout. Treat exit 2 as a hard failure.
4. Perform LLM soft checks on pages flagged by the script and on a sample of unflagged pages:
   - Contradictions across pages.
   - Atomicity violation in topics (>400 words, H3+, multi-concept).
   - Overview paragraphs missing citations to linked topics/refs.
5. Emit a consolidated report: machine defects grouped by check, soft findings as a separate section.
6. Offer deterministic fixes where safe: broken-link auto-repair if exactly one same-named file exists elsewhere in the wiki; otherwise leave for the user.

## Outputs

Structured report: summary counts, per-defect details, suggested fixes.

## Do not

- Write fixes automatically beyond the safe set; ask before editing pages.
- Parse the script's stdout as free text — always parse JSON.
