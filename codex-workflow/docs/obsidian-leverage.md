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

Net: of the five obsidian-skills, **`obsidian-bases`** and **`obsidian-markdown`** are fully
exploited and shipped as v0.4.0.

## Open runway

| Item | obsidian-skill | Value | Status | Next step |
|---|---|---|---|---|
| **A. Live vault queries** — wire SessionStart / mining skills to `obsidian base:query` + `search` instead of `cat`/raw reads | **`obsidian-cli`** | High — makes the vault a live, queryable knowledge source; complements the markdown allowlist | **Validated, unblocked.** CLI talks to the running app; `base:query path="Tickets.base" view="Board" format=md` returns normalized rows | Build the cli tranche (in progress) |
| **B. Architecture canvases** — visual maps in `Architecture/` (dependency graphs, the Code↔Vault bifurcation diagram) | **`json-canvas`** | Medium | Buildable (pure JSON file generation, no external dep) | Add a `codex-*` canvas skill; not started |
| **C. Research ingestion** — route external-doc research into `Knowledge/` as clean, source-stamped notes instead of WebFetch dumps | **`defuddle`** | Medium | **Blocked** — Defuddle CLI not installed (`npx` not cached) | Install Defuddle CLI first, then add an ingest skill |

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
