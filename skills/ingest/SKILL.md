---
name: ingest
description: Add a new source to the ultradocs wiki. Triggers on "add this to the wiki", "ingest this", "save this source", "ultradocs ingest <url/path>". Creates a refs page, updates affected topics, touches overviews.
---

# ultradocs:ingest

Ingest a source into the wiki: create a ref, update or create topics, touch overviews.

## When to use

- "add X to the wiki"
- "save this paper/url/doc"
- "ingest this"
- User pastes a URL or file path in a wiki context

## Inputs

- `source`: URL, file path, or pasted text.
- `path` (optional): wiki root. Default `docs/`.

## Procedure

1. Resolve wiki path. If not an ultradocs wiki (no root `CLAUDE.md` + expected folders), stop.
2. Read the source:
   - File: read directly.
   - URL: WebFetch.
   - Pasted text: use as-is.
3. Generate a stable `id` (kebab-case slug of the source title).
4. If `refs/<id>.md` already exists, stop and report "source already ingested".
5. Write `refs/<id>.md` using the ref template (see root CLAUDE.md §7). Body is a 1–3 paragraph summary + key-points list.
6. **Identify affected topics** (heuristic from spec §9.2):
   - Extract 3–8 key terms: title words, tags, prominent noun phrases.
   - Grep each term against `topics/` titles, filenames, tags.
   - ≥2 term hits → update that topic: append a new paragraph citing the new ref; bump `updated`.
   - 0 hits but coherent new concept → create a new topic page citing this ref.
   - Exactly 1 weak hit → emit a note for the curator; do not auto-create.
7. Touch overviews that link to any updated topic: bump `updated`.
8. Append an entry to the root README's "Recent changes" section: `- <YYYY-MM-DD> ingested [<title>](refs/<id>.md)`.
9. Report: what was created, what was updated, any notes for manual review.

## Outputs

Change summary: created/updated files, notes.

## Do not

- Modify existing ref bodies (refs are immutable).
- Use `sources:` front-matter on topic/overview pages.
- Create topics speculatively on weak matches — emit a note instead.
