---
id: script-policy
title: Skill Script Policy
type: topic
created: 2026-04-25
updated: 2026-04-25
tags: [scripts, python, stdlib]
status: stable
---

# Skill Script Policy

Scripts that back ultradocs skills follow strict rules. Language is Python 3, standard library only — no `pip install`, no external dependencies — so users install nothing to use the plugin[^ultradocs-plugin-design]. Scripts live inside the owning skill's directory at `skills/<name>/scripts/`, never in a shared scripts directory; duplication across skills is acceptable and preferred over hidden coupling[^ultradocs-plugin-design].

Skills invoke scripts with `python3 <plugin>/skills/<name>/scripts/<script>.py <args>` and parse JSON from stdout. Exit codes are contractual: 0 means clean, 1 means defects found, and 2 means a usage or I/O error. Front-matter problems are not exit-2 — they surface as `frontmatter-violation` defects with exit 1[^ultradocs-plugin-design].

The lint script is the only script in v0; if `init`, `ingest`, or `query` add scripts later, they live under their own skill directories under the same rules[^ultradocs-plugin-design]. The lint skill itself parses the JSON and never tries to read free text from stdout[^skill-lint].

[^ultradocs-plugin-design]: See [refs/ultradocs-plugin-design.md](../refs/ultradocs-plugin-design.md).
[^skill-lint]: See [refs/skill-lint.md](../refs/skill-lint.md).
