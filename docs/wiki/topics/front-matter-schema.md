---
id: front-matter-schema
title: Front-Matter Schema
type: topic
created: 2026-04-25
updated: 2026-04-25
tags: [schema, frontmatter, yaml]
status: stable
---

# Front-Matter Schema

Every page in an ultradocs wiki carries YAML front-matter with a fixed set of keys: `id` (stable slug or ULID, never reused), `title` (human-readable), `type` (`ref`, `topic`, or `overview`), `created` and `updated` dates in `YYYY-MM-DD` form, optional `tags` list, and `status` (`draft`, `stable`, or `stale`)[^ultradocs-plugin-design].

The `sources` key is provenance-only and exclusive to `refs/` pages — it lists the URL or file path of the external source. Topics and overviews must not carry `sources`; they cite refs via footnote links instead[^ultradocs-plugin-design]. Lint flags any topic or overview that includes a `sources` key as a `frontmatter-violation`[^skill-lint].

The `id` is the stable cross-reference key used in citations and provenance fields. The filename is a separate concern — it is the link target that relative markdown resolves against. Renames are permitted but require rewriting all inbound links in the same commit[^ultradocs-plugin-design].

[^ultradocs-plugin-design]: See [refs/ultradocs-plugin-design.md](../refs/ultradocs-plugin-design.md).
[^skill-lint]: See [refs/skill-lint.md](../refs/skill-lint.md).
