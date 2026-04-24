# ultradocs Plugin — Design

- **Date:** 2026-04-25
- **Status:** Draft (pending spec review)
- **Plugin:** `ultradocs` (Claude Code plugin)

## 1. Purpose

A Claude Code plugin that lets Claude build and maintain a **persistent, interlinked markdown wiki** as the user's long-term knowledge store. Dual-use:

- Developer source-code documentation (RFCs, ADRs, component reference, architecture notes).
- Personal second brain (Zettelkasten-style atomic notes, topical maps).

The wiki itself is the retrieval index — no embeddings, no RAG. Claude handles bookkeeping (summarizing, cross-linking, lint), the human curates sources and asks questions. Inspired by Karpathy's persistent-wiki-over-RAG pattern [[ref]] and Zettelkasten atomicity.

## 2. Goals / Non-goals

**Goals**

- Single `ultradocs:init` skill scaffolds a consistent wiki layout at a chosen path.
- Every wiki folder contains `CLAUDE.md` AI instructions so Claude stays consistent across sessions and directories.
- Three operational skills cover Karpathy's loop: ingest, query, lint.
- GitHub-renderable markdown (front-matter tables, relative links, native footnotes).
- Accuracy: every claim in `topics/` or `overviews/` cites a ref.
- Retrievability: stable IDs, consistent front-matter, lint catches drift.

**Non-goals (v0.0.1)**

- No RAG, embeddings, or vector search.
- No non-Claude AI instruction files (AGENTS.md, GEMINI.md) — Claude-only for now; extend later.
- No multi-wiki registry; path is per-invocation.
- No automation hooks; all work is explicit skill invocation.
- No UI beyond Claude Code + GitHub rendering.

## 3. Installation

Local marketplace (already wired):

```
/plugin marketplace add /path/to/ultradocs
/plugin install ultradocs@ultradocs
```

Files already in place:

- `.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json`

## 4. Wiki Layout

`ultradocs:init [path]` scaffolds:

```
<root>/                    # default "docs/", "." for cwd
  CLAUDE.md                # AI: behavior + schema (templates, naming, links, lints)
  README.md                # human + AI: wiki overview, nav, stats
  refs/
    CLAUDE.md              # rules for refs pages
  topics/
    CLAUDE.md              # rules for topic pages
  overviews/
    CLAUDE.md              # rules for overview pages
```

**Conventions**

- `CLAUDE.md` = AI-only instructions (required in every folder).
- `README.md` = human + AI entry point (root only by default; folders optional).
- No separate `schema.md` — schema rules live in root `CLAUDE.md`.

### 4.1 Root `CLAUDE.md` required sections

The `init` skill writes a root `CLAUDE.md` containing these sections verbatim (users may edit after):

1. **Purpose** — what this wiki is for.
2. **Folder roles** — one-line descriptions of `refs/`, `topics/`, `overviews/`.
3. **Front-matter schema** — exact YAML keys, types, required/optional (mirrors §5.1).
4. **Naming** — kebab-case filenames; stable `id`; rename rules (mirrors §5.2).
5. **Link style** — relative markdown only; no wikilinks.
6. **Citation style** — `[^ref-id]` footnotes; pointer rules.
7. **Page templates** — a copy-pasteable skeleton for `ref`, `topic`, `overview`.
8. **Lint rules** — full list from §6.2, in plain language.
9. **Workflow** — when to ingest, when to lint, when to restructure.

### 4.2 Folder `CLAUDE.md` required sections

Each folder's `CLAUDE.md` contains:

1. **Role** — what kind of page goes here (mirrors §5.3 for that folder).
2. **Template** — page template for this type.
3. **Rules** — constraints specific to this folder (immutability for refs, atomicity for topics, citation threshold for overviews).
4. **Anti-patterns** — short list of what not to do.

## 5. Page Model

Three page types, one per folder:

| Folder | Page type | Body | Cites | Updated by |
|---|---|---|---|---|
| `refs/` | External source | Summary of source (paper, URL, doc, code snapshot). Body treated as immutable. | source itself (in front-matter) | `ingest` only |
| `topics/` | Atomic concept | One idea per page, prose + links to related topics. | ≥1 ref | `ingest`, `query` (backfill), curator edits |
| `overviews/` | Aggregation | Narrative tying several topics together. | ≥1 topic + refs | curator edits, `query` backfill |

### 5.1 Front-matter (YAML, every page)

```yaml
---
id: <stable-id>               # slug or ULID; never reused
title: <human title>
type: ref | topic | overview
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [<url-or-path>, ...] # required on refs; forbidden on topics/overviews
tags: [tag1, tag2]
status: draft | stable | stale
---
```

`sources` is a provenance field exclusive to `refs/`. Topics and overviews cite sources via footnote links to `refs/` pages, not via this field.

### 5.2 Links & citations

- **Links:** relative markdown only — `[foo](../topics/foo.md)`. No wikilinks.
- **Citations:** footnote style `[^ref-id]` pointing at a `refs/` page. Every non-trivial claim in `topics/` / `overviews/` must cite ≥1 ref.
- **Filenames:** kebab-case. Filename is the link target (relative markdown links resolve by path, not id). `id` exists for stable cross-references in front-matter (e.g., `sources:` provenance) and citation keys. Renames are allowed but require rewriting all inbound links in the same commit — the curator performs the rewrite; lint flags any missed links as broken.

### 5.3 Folder rules (enforced by folder `CLAUDE.md`)

- `refs/`: body is immutable once written; only update if source itself changes. Must set `sources:` in front-matter.
- `topics/`: atomic — one concept per page. Must cite ≥1 ref. Link related topics.
  - **Atomicity operational definition:** single noun-phrase subject in `title`; ≤400 words body; no sub-headings deeper than H2; title expresses one idea (if you feel the urge to write "X and Y", split it).
- `overviews/`: aggregate — must link ≥3 distinct topic or ref pages. No original claims (every paragraph of substantive content cites a topic or ref).

## 6. Skills

Plugin exposes four skills (invoked as `ultradocs:<name>`). Skills are the **only** interface; no slash commands, no hooks.

| Skill | Directory | Auto-trigger phrases | Owner | Action |
|---|---|---|---|---|
| init | `skills/init/` | "initialize wiki", "set up ultradocs" | invoked directly by user (no agent owner — runs in main session) | Scaffold layout at path (default `docs/`). Writes root `CLAUDE.md`, `README.md`, folder `CLAUDE.md`s. |
| ingest | `skills/ingest/` | "add to wiki", "save this source", "ingest this" | `ultradocs-curator` | Read source → write `refs/<id>.md` → update/create affected topics → touch overviews → log in README index. |
| query | `skills/query/` | "what does wiki say about X", "search the wiki for Y" | `ultradocs-researcher` | Search wiki (Glob/Grep) → synthesize with footnote citations → optionally emit gap note (does not write). |
| lint | `skills/lint/` | "check wiki health", "find orphan pages", "lint the wiki" | `ultradocs-curator` | Scan front-matter + links → report orphans, missing citations, broken links, duplicate ids, stale-stable pages, LLM-flagged contradictions. |

### 6.1 Skill structure

Each skill is a self-contained directory with its own `SKILL.md` and any scripts it owns. Scripts are **skill-local**; duplication across skills is acceptable and preferred over a shared `scripts/` directory. Rationale: skills stay portable, independently extractable, and self-documenting — cost of duplication is small compared to cost of hidden coupling.

```
skills/
  init/
    SKILL.md
  ingest/
    SKILL.md
  query/
    SKILL.md
  lint/
    SKILL.md
    scripts/
      lint.py          # Python stdlib only
```

Skills read the target wiki's root `CLAUDE.md` before writing, so schema changes propagate without skill edits.

### 6.1.1 Script policy

- **Language:** Python 3, **standard library only**. No `pip install`, no external deps. Users must not install anything to use the plugin.
- **Location:** inside the owning skill's directory (`skills/<name>/scripts/`). Duplication across skills is acceptable.
- **Invocation:** skills call scripts via `python3 <plugin>/skills/<name>/scripts/<script>.py <args>`.
- **Contract:** scripts emit structured output (JSON on stdout) and use exit codes (0 = clean, 1 = defects found, 2 = usage error). Skills parse output; no LLM parsing of free-form text where JSON will do.

### 6.2 Lint rules (machine-checkable + soft)

Machine-checkable rules are implemented deterministically by `skills/lint/scripts/lint.py`. The lint skill orchestrates: run script → parse JSON → report / fix. Soft rules are LLM-judged by the skill itself after the script pass.

**Machine-checkable** (implemented by `lint.py`)

- Orphan: page with no inbound markdown links (excluding README).
- Missing citation: `topic`/`overview` body has a paragraph with no `[^ref]` footnote.
- Overview under-linked: `overview` page linking fewer than 3 distinct topic/ref pages (per §5.3).
- Broken link: relative link resolves to no file.
- Duplicate `id` across pages.
- Stale: a `ref` page with `status: stable`, `updated` older than **90 days**, and a `sources:` entry pointing at a local file whose mtime is newer than `updated` (URL-based sources skipped in v0). Only the ref itself is flagged — topics/overviews citing a stale ref are not auto-flagged in v0.
- Front-matter violations: missing required keys; `sources:` present on topic/overview; `type` not matching folder.

**Soft (LLM-judged)**

- Contradictory claims across pages.
- Topic page violating atomicity per §5.3 definition (multiple concepts, >400 words, H3+ headings).
- Overview with substantive paragraphs lacking citation to a linked topic/ref.

## 7. Agents

Two agents, non-overlapping. Lean by design.

| Agent | Side | Owns | Skills | Tools |
|---|---|---|---|---|
| `ultradocs-curator` | Write | ingest, lint, fix, restructure, authoring all pages | `ultradocs:ingest`, `ultradocs:lint` | Read, Write, Edit, Glob, Grep, Bash(git) |
| `ultradocs-researcher` | Read | answer questions, synthesize with citations, identify gaps (delegates writes to curator) | `ultradocs:query` | Read, Glob, Grep, WebFetch, WebSearch |

Both agents live in `agents/` at plugin root:

```
agents/
  ultradocs-curator.md
  ultradocs-researcher.md
```

Each agent is a markdown file with front-matter (`name`, `description`, `tools`) and a body describing its role, constraints, and how it uses skills.

## 8. Plugin Repository Layout

```
ultradocs/
  .claude-plugin/
    plugin.json
    marketplace.json
  skills/
    init/
      SKILL.md
    ingest/
      SKILL.md
    query/
      SKILL.md
    lint/
      SKILL.md
      scripts/
        lint.py
  agents/
    ultradocs-curator.md
    ultradocs-researcher.md
  docs/                       # plugin's own docs (specs, etc.)
    superpowers/specs/
```

Not shown: `hooks/` stays empty in v0.0.1 (reserved for future automation). Other skills (`init`, `ingest`, `query`) ship no scripts in v0; if scripts are added later they live under `skills/<name>/scripts/` even if logic duplicates `lint/scripts/`.

## 9. Flows

### 9.1 New wiki

1. User: "set up ultradocs in ./docs".
2. Claude invokes `ultradocs:init` with path `./docs`.
3. Skill writes root `CLAUDE.md` (schema), `README.md` (empty overview), three folders each with `CLAUDE.md`.
4. User commits.

### 9.2 Ingest a source

1. User pastes URL or drops file, says "add to wiki".
2. Curator invokes `ultradocs:ingest`:
   - Read source.
   - Write `refs/<id>.md` with summary + front-matter.
   - **Identify affected topics** — extract 3–8 key terms from the ref (title words, tags, prominent noun phrases). Grep each against `topics/` titles, filenames, and tags. Matching heuristic:
     - ≥2 term hits in a topic page → update that topic (append citation, refine prose).
     - 0 hits but ref covers a coherent new concept → create a new topic page citing this ref.
     - Ambiguous (1 hit, weak match) → emit a note for curator review, do not auto-create.
   - Touch overviews that reference changed topics (bump `updated`).
   - Append entry to README's recent-changes list.

### 9.3 Query

1. User asks a question.
2. Researcher invokes `ultradocs:query`:
   - Glob/Grep wiki for relevant pages.
   - Synthesize answer citing `[^ref-id]`.
   - If gap detected, emit gap note: "topic X undocumented; suggest ingesting source Y". Does not write.

### 9.4 Lint

1. User: "check wiki".
2. Curator invokes `ultradocs:lint`:
   - Run `python3 skills/lint/scripts/lint.py <wiki-root>`; parse JSON.
   - Perform LLM soft checks (contradictions, atomicity, narrative citation quality) on pages flagged or sampled.
   - Emit consolidated report combining script defects + soft findings.
   - Apply fixes deterministically where safe (broken-link auto-repair if target is obvious; otherwise defer to user).

## 10. Open Questions / Deferred

- Multi-AI instruction files (AGENTS.md, GEMINI.md) — add once Claude-only flow is stable.
- Automation hooks (auto-lint on file change) — deferred; explicit invocation only in v0.0.1.
- Multi-wiki registry / workspace switching — deferred.
- Page promotion workflow (topic → overview) details — curator decides manually for now; formalize if patterns emerge.
- ID scheme (slug vs ULID) — start with slug; switch to ULID if collisions become common.

## 11. Success Criteria

- `ultradocs:init .` produces a wiki skeleton (root + 3 folders, all `CLAUDE.md`s, root `README.md`) that renders cleanly on GitHub (front-matter as table, footnotes as endnotes, relative links clickable).
- After ingesting 10 sources, `ultradocs:query` answers 5 test questions with every non-trivial claim backed by a `[^ref]` footnote resolving to a ref page.
- On a test fixture containing **3 orphans, 2 broken links, 2 missing-citation paragraphs, 1 duplicate id, 1 undercited overview (linking <3 topics/refs)**, `ultradocs:lint` detects ≥90% of seeded defects with zero false positives on a known-clean control fixture.
- `ultradocs-researcher` never writes to the wiki (verified by read-only tool set); `ultradocs-curator` is the only agent with Write/Edit tools.
- `skills/lint/scripts/lint.py` runs on a 100-page fixture in under 1 second on a modern laptop, using only Python stdlib (verified by `python3 -c 'import <module>'` for each import the script uses — all resolve against stdlib).

## 12. Scripts

### 12.1 `skills/lint/scripts/lint.py`

**Purpose:** deterministic implementation of all machine-checkable lint rules from §6.2.

**Invocation:**
```
python3 skills/lint/scripts/lint.py <wiki-root> [--only <check>,<check>,...]
```

- `<wiki-root>`: path to wiki (e.g. `./docs`).
- `--only`: comma-separated checks to run (e.g. `orphan,broken-link`). Default: all.
- Output is always JSON on stdout. v0 ships no human-readable mode (skills format output for users).

**Exit codes:**
- `0`: no defects.
- `1`: defects found.
- `2`: I/O or argument failure (missing wiki root, bad CLI args, script-level exception). Front-matter problems are not exit-2 — they surface as `frontmatter-violation` defects with exit 1.

**JSON output shape:**
```json
{
  "wiki_root": "./docs",
  "pages_scanned": 42,
  "defects": [
    {
      "check": "orphan",
      "severity": "warn",
      "page": "topics/foo.md",
      "message": "no inbound links",
      "data": {}
    },
    {
      "check": "broken-link",
      "severity": "error",
      "page": "overviews/bar.md",
      "message": "link target not found: ../topics/missing.md",
      "data": {"target": "topics/missing.md", "line": 17}
    }
  ],
  "summary": {
    "orphan": 3,
    "broken-link": 2,
    "missing-citation": 0,
    "overview-underlinked": 1,
    "duplicate-id": 0,
    "stale": 0,
    "frontmatter-violation": 1
  }
}
```

**Check identifiers** (stable, used in `--only` and JSON):
- `orphan`
- `broken-link`
- `duplicate-id`
- `missing-citation`
- `overview-underlinked`
- `stale`
- `frontmatter-violation`

**Implementation notes:**
- YAML front-matter parsed with a minimal stdlib-only parser (limited to the subset the schema uses: scalars, flow-style lists, dates). No `PyYAML` dependency.
- Markdown link extraction via regex (`\[([^\]]+)\]\(([^)]+)\)`), restricted to relative paths (no `http://`, no `#` anchors alone).
- Footnote detection via regex (`\[\^[\w-]+\]`).
- Walks `<wiki-root>` with `pathlib.Path.rglob("*.md")`; respects folder roles by path prefix.

**Testing:** ship a fixtures dir under `skills/lint/scripts/fixtures/` with a seeded-defect wiki and a clean control. Not part of the plugin install — used only in plugin development.
