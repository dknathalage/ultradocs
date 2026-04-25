## Summary

<!-- One or two sentences. Why this change? -->

## Type

- [ ] feat (new skill / new capability)
- [ ] fix (bug fix)
- [ ] docs (spec / plan / README / CONTRIBUTING)
- [ ] test (lint script tests)
- [ ] chore (tooling, CI, housekeeping)

## Spec / plan link

<!-- Path to docs/superpowers/specs/... or docs/superpowers/plans/...
     Non-trivial changes need a plan first. See CONTRIBUTING.md. -->

## Checklist

- [ ] `python3 -m unittest test_lint.py -v` passes (if lint script touched)
- [ ] Smoke-tested in a Claude Code session with `claude --plugin-dir .` (if skill or agent touched)
- [ ] No new dependencies (lint script must be stdlib-only)
- [ ] Trigger phrases in `description:` fields are natural language, not `/slash-command` syntax
- [ ] Spec / plan updated if scope changed
