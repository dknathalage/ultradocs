# ultradocs

> A Claude Code plugin that turns markdown into a living, self-maintaining wiki.

`ultradocs` lets Claude build and curate a persistent, interlinked markdown knowledge base — your source-code documentation, research notebook, or personal second brain. The wiki **is** the index: no embeddings, no RAG, no opaque vector store. Just markdown files Claude can read, write, and link with discipline.

Inspired by [Karpathy's persistent-wiki-over-RAG pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) and the Zettelkasten method.

---

## Why

LLMs are great at maintaining knowledge but humans are bad at the bookkeeping that keeps a wiki alive. `ultradocs` flips the labour: **you curate sources and ask questions, Claude writes, links, and lints**.

- **Markdown-native.** Renders perfectly on GitHub. Diffable. Greppable. Yours.
- **Schema-enforced.** Every page has typed front-matter, every claim cites a source.
- **No black-box retrieval.** When Claude answers, every footnote points at a real file you can open.
- **Dual-purpose.** Same primitives work for dev docs, research, or a personal second brain — only the folder names change in your head.

---

## How it works

Three folders, three roles:

| Folder | Holds | Updated by |
|---|---|---|
| `refs/` | One page per external source — papers, URLs, docs, code snapshots. Body is a summary, immutable. | `ultradocs:ingest` only |
| `topics/` | Atomic concept pages. One idea per page, ≤400 words, must cite a ref. | `ultradocs:ingest`, curator edits |
| `overviews/` | Narrative aggregations linking ≥3 topics or refs. No original claims. | curator edits |

Every folder has a `CLAUDE.md` so AI agents stay consistent across sessions. The root `README.md` is the human + AI entry point.

---

## Skills

`ultradocs` ships four skills, invoked by name:

- **`ultradocs:init`** — scaffold a new wiki at any path.
  > "set up an ultradocs wiki in `./docs`"

- **`ultradocs:ingest`** — read a source, write a `refs/` page, update or create the affected topics, touch overviews, log the change.
  > "ingest this paper into the wiki"

- **`ultradocs:query`** — search, synthesize an answer with footnote citations, flag gaps. Read-only.
  > "what does the wiki say about prompt caching?"

- **`ultradocs:lint`** — find orphans, broken links, missing citations, stale pages, contradictions, atomicity violations.
  > "lint the wiki and fix what you safely can"

Plus two agents:

- **`ultradocs-curator`** — write side. Owns ingest, lint, fixes, and restructures.
- **`ultradocs-researcher`** — read side. Synthesizes answers, never writes.

---

## Install

```bash
# in Claude Code
/plugin marketplace add /path/to/ultradocs
/plugin install ultradocs@ultradocs
```

Or for live development:

```bash
claude --plugin-dir /path/to/ultradocs
```

---

## Quick start

```text
You: set up an ultradocs wiki in ./docs
Claude: [scaffolds CLAUDE.md, README.md, refs/, topics/, overviews/]

You: ingest https://arxiv.org/abs/2305.20081 into the wiki
Claude: [writes refs/tree-of-thoughts.md, creates topics/tree-search-prompting.md,
         updates overviews/llm-reasoning.md, appends a change log entry]

You: what does the wiki say about tree search prompting?
Claude: [returns cited prose with [^tree-of-thoughts] footnotes]

You: lint the wiki
Claude: [runs lint.py, reports orphans and broken links, offers safe auto-fixes]
```

---

## Design principles

1. **The wiki is the index.** No embeddings, no vectors. If you can `grep` it, Claude can find it.
2. **Schema before scale.** Front-matter is mandatory. IDs are stable. Renames rewrite inbound links.
3. **AI instructions live next to the data.** Every folder's `CLAUDE.md` defines its rules; behavior follows the wiki, not the model.
4. **Determinism where possible.** Lint runs as a Python stdlib script — no LLM tokens spent on grunt work.
5. **Lean agents.** One agent writes, one agent reads. No overlap.

---

## Status

`v0.0.1` — initial release. Claude-only AI instructions; broader agent support (AGENTS.md, GEMINI.md) planned.

## License

MIT.
