# How codex-workflow leverages the obsidian-skills plugin

The codex workflow pairs a codebase with an Obsidian vault as the agent's canonical
knowledge base. The separate [`obsidian-skills`](https://github.com/...) plugin ships five
skills (`obsidian-bases`, `obsidian-markdown`, `obsidian-cli`, `json-canvas`, `defuddle`)
that expose Obsidian's native capabilities. This document maps what this plugin draws from
each — both what's shipped and what's still open runway — so future work has the rationale
in one place.

## What we built (shipped)

| # | Accomplishment | obsidian-skill leveraged | How |
|---|---|---|---|
| 1 | **`Tickets.base` board** — tickets grouped into status lanes, live in Obsidian | **`obsidian-bases`** | Used its `.base` schema (filters/formulas/views): a table with `groupBy`, a `has_meta` formula, and a "Needs metadata" triage view |
| 2 | **The `.last()` fix** (`file.folder.replace(...)`, not `split("/").last()`) | **`obsidian-bases`** (FUNCTIONS_REFERENCE) | Its reference showed lists have no index/`.last()` accessor — so we strip the folder prefix instead. Captured as a documented gotcha |
| 3 | **Frontmatter convention** (`ticket`/`type`/`area`/`stack`/`tags`/`created`; *status encoded by folder*) | **`obsidian-markdown`** | Properties/frontmatter are this skill's domain; this schema is what makes Bases queryable |
| 4 | **`codex-mine-bases` skill** + **`.base` emission in `codex-init-vault`** (v0.4.0) | **`obsidian-bases` + `obsidian-markdown`** | Codified the schema and the three dashboards (Tickets/Features/Agent_Sessions) into portable plugin skills |
| 5 | **Design: agents query a Base instead of raw-reading files**; the markdown allowlist becomes a "use the structured channel" guardrail | **`obsidian-cli`** (`base:query`) | The runtime channel the convention is built for — see runway item A, now validated |
| 6 | **Finding: Obsidian rewrites `.base` files on open** (strips comments, flow→block, adds `columnSize`) | **`obsidian-bases`** (observed) | Folded into [`frontmatter-convention.md`](../references/frontmatter-convention.md) |

Net: **all five** obsidian-skills are now leveraged — `obsidian-bases` + `obsidian-markdown`
(v0.4.0), `obsidian-cli` (v0.5.0 `codex-query-vault`, also powering v0.6.0), `json-canvas`
(v0.6.0 `codex-canvas-map`), and `defuddle` (v0.7.0 `codex-research-ingest`).

## Open runway

| Item | obsidian-skill | Value | Status | Next step |
|---|---|---|---|---|
| **A. Live vault queries** via `obsidian base:query` + `search` instead of `cat`/raw reads | **`obsidian-cli`** | High — makes the vault a live, queryable knowledge source; complements the markdown allowlist | **SHIPPED v0.5.0** as the read-only `codex-query-vault` skill; dogfooded live | Optional: opt-in SessionStart enhancement to inject open-ticket snapshot |
| **B. Architecture canvases** — visual relationship maps in `Architecture/` | **`json-canvas`** | Medium | **SHIPPED v0.6.0** as `codex-canvas-map` (hub note → links/backlinks graph); dogfooded live | Optional: more layouts (domain clusters, full dependency graphs) |
| **C. Research ingestion** — external docs → clean, source-stamped `Knowledge/` notes | **`defuddle`** | Medium | **SHIPPED v0.7.0** as `codex-research-ingest`; Defuddle installed + dogfooded live | Optional: batch/multi-page ingest |

### Validated CLI invocation (item A)

```bash
# List bases / query a view as structured rows (Obsidian must be running, vault active)
obsidian bases
obsidian base:query path="Tickets.base" view="Board" format=md      # or format=json
```

Gotchas found:
- Bases resolve by **`path=` (e.g. `Tickets.base`)**, not `file=` (which is name/wikilink
  resolution and reports "Base file not found" for bases).
- `base:views` appears to ignore `path=` and return the *active* base's views — prefer
  `base:query` with an explicit `view=` you already know.
- The CLI requires the Obsidian app to be running with the target vault open; design any
  hook/skill that uses it to **degrade gracefully** (fall back to file reads or no-op) when
  the CLI is unavailable.
- **`base:query` only returns columns in a view's `order`** — not the `groupBy` property.
  So a "By area" view that groups by `area` but omits it from `order` shows blank `area` over
  the CLI (it still renders correctly *inside* Obsidian). Rule: for any Base you intend to
  query via the CLI, **put the `groupBy` property in `order` too**.
