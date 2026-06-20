# codex-workflow

Portable hooks and skills for the AI Codex workflow: a project layout pairing a codebase with an Obsidian vault that serves as the canonical agent knowledge base.

## What's in v0.10.0

Three hooks, three init skills, three mining skills, one live query skill, one Canvas generator, one research-ingest skill, one vault-lint skill, and **four research-backed vault archetypes** — all configurable per project with sensible zero-config defaults.

### Init skills

- `/codex-workflow:codex-init-workspace` — scaffold the CLAUDE.md tree (root + per-project) by inspecting `package.json` / `pubspec.yaml`.
- `/codex-workflow:codex-init-vault [--type <archetype>]` — scaffold an Obsidian vault from a research-backed **archetype**: `software-project` (default), `research` (Zettelkasten+PARA), `personal-pkm` (PARA), or `technical-docs` (Diataxis). Reads the archetype spec for folder structure + naming + frontmatter, scaffolds the skeleton, and writes a `.codex-vault.json` marker. See [`archetypes/README.md`](./archetypes/README.md).
- `/codex-workflow:codex-init-rules` — drop a starter set of `.agent/rules/*.md` template files (`strict-implementation-lock`, `rules-architect-protocol`, `rules-git-workflow`, `rules-date-time-handling`).

### Mining skills

- `/codex-workflow:codex-mine-style` — interactive walkthrough that mines an author's commits (`git log --author=...`) to draft a canonical-style-examples Knowledge note with file/line anchors and an Agent Rules block.
- `/codex-workflow:codex-add-refactor-entry <commit-hash>` — inspect a refactor commit and append a before/after entry to the Style Refactor Catalog with the principle applied.
- `/codex-workflow:codex-mine-bases` — backfill the frontmatter convention across an existing vault and scaffold Obsidian Bases (`.base`) over `Tickets/`, `Features/`, `Agent_Sessions/`. Turns flat folders into live, queryable dashboards. Status is derived from the folder, never duplicated. See [`references/frontmatter-convention.md`](./references/frontmatter-convention.md) for the schema.

### Query skills

- `/codex-workflow:codex-query-vault` — **read-only** live query of the vault via the Obsidian CLI: list/query Bases (open tickets, features by area, recent sessions), full-text `search`, and `backlinks` — instead of raw file reads. The sanctioned read channel that complements the markdown allowlist. Requires Obsidian running with the vault open; degrades gracefully when it isn't. Unlike the side-effecting `codex-*` skills, this one **allows model invocation** (it's read-only), so agents can reach for it whenever they need vault state.

### Canvas skills

- `/codex-workflow:codex-canvas-map <hub-note>` — generate an Obsidian Canvas (`.canvas`) relationship map for a hub note: the note centered, its outgoing `links` on one side and its `backlinks` on the other, wired with arrows, saved to `Architecture/`. Reads the link graph via the Obsidian CLI (composes the v0.5.0 query channel with the JSON Canvas format). Requires Obsidian running; validates node/edge integrity before writing.

### Research skills

- `/codex-workflow:codex-research-ingest <url>` — fetch an external web page as clean markdown with the [Defuddle](https://github.com/kepano/defuddle) CLI and file it into `Knowledge/` as a source-stamped `type: reference` note (with `source`/`domain`/`retrieved` frontmatter and a provenance callout). More than a fetch: it follows the frontmatter convention and slots into the Knowledge index. Requires `defuddle` (`npm install -g defuddle`).

### Maintenance skills

- `/codex-workflow:codex-vault-lint [vault] [--type <archetype>]` — audit an existing vault against its archetype spec and fix the drift: filename violations, frontmatter issues, stray files, and (semantic layer) mixed-language / near-duplicate / mangled notes. Proposes renames + frontmatter fixes, applies them with `git mv` and **wikilink repair** on confirmation, then re-scans. The retrofit path for vaults that predate archetypes. Backed by the deterministic scanner `scripts/vault-lint.py`.

Every skill is an interactive walkthrough: it inspects current state, proposes a plan, asks the user to confirm, then writes. Existing files are never overwritten without explicit per-file approval.

### Hooks

### `SessionStart` — Codex orientation injection

Reads the project's Codex `README.md` and `Knowledge/Agent_Orientation.md` and injects them as `additionalContext` so every new session boots with the workspace map already loaded.

- **Codex folder name** comes from `.claude/codex-workflow.config.json` (`codex.folder`) or falls back to autodetect via glob `AI_Codex_*/`.
- **Files to inject** come from `codex.bootstrap[]` or default to `["README.md", "Knowledge/Agent_Orientation.md"]`.
- If no codex folder is found, the hook is a silent no-op.

### `PreToolUse` (matcher `Read|Grep`) — markdown allowlist

Denies Read/Grep on markdown files inside the project tree that aren't on a small allowlist. Reads outside the project, and reads of non-`.md` files, pass through.

- **Allowlist patterns** come from `markdownAllowlist.patterns[]` or default to:
  - `CLAUDE.md`, `GEMINI.md` at any level
  - any `*.md` under `.agent/` (recursive)
  - `projects/*/CLAUDE.md`, `projects/*/GEMINI.md`, `projects/*/.agent/*`
- **Codex folder is always fully allowed** (matched by name from config or autodetect).
- Custom patterns use bash `case` glob syntax (`*` matches any characters including `/`).

### `PreToolUse` (matcher `Write`) — archetype naming enforcement

Structurally gates new `.md` writes inside a vault that declares its archetype (a
`.codex-vault.json` marker written by `codex-init-vault`). Reads the marker → the archetype
spec, and **denies** a write whose filename shape is wrong or whose frontmatter is missing a
required key / contains a forbidden one (e.g. `status` in a ticket). It is **fail-open**: a no-op
outside a marked vault, for unknown archetypes, or for exempt files (`README.md`,
`Agent_Orientation.md`, `Home.md`, `index.md`, and `assets/` / `Meta/` folders).

- Enforces only what regex/sets can decide (filename **shape**, required/forbidden frontmatter
  **keys**) — semantic issues (language, near-duplicates) are `codex-vault-lint`'s job.
- Disable per project via `.claude/codex-workflow.config.json` → `{"namingEnforcement":{"enabled":false}}`.
- Implemented in `hooks/scripts/naming-enforcement.py` (Python 3, stdlib only).

## Installation

Add the marketplace once per machine, then install the plugin:

```text
/plugin marketplace add <your-github-owner>/codex-workflow-marketplace
/plugin install codex-workflow@codex-workflow-marketplace
```

After installation, open `/hooks` (or restart Claude Code) to ensure the watcher picks up the new hooks for the current session. New sessions get them automatically.

## Configuration

Most projects need zero configuration — the defaults match the convention this plugin assumes.

If you want to customize, drop a file at `.claude/codex-workflow.config.json` in your project. See `examples/codex-workflow.config.example.json` for the schema. Every key is optional; omitted keys fall back to the defaults above.

## Roadmap

| Version         | Adds                                                                                                                                                                                    |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0.1.0           | Hooks: SessionStart bootstrap + PreToolUse markdown allowlist. Config-driven, with autodetect fallback.                                                                                 |
| 0.1.1           | Hooks: broaden `AI_Codex*/` autodetect glob; silently skip missing bootstrap files.                                                                                                     |
| 0.2.0           | Init skills: `codex-init-workspace`, `codex-init-vault`, `codex-init-rules`.                                                                                                            |
| 0.3.0           | Mining skills: `codex-mine-style`, `codex-add-refactor-entry`.                                                                                                                          |
| 0.4.0           | Bases tranche: `codex-mine-bases` skill + frontmatter convention; `codex-init-vault` now emits `.base` dashboards (Tickets/Features/Agent_Sessions).                                    |
| 0.5.0           | obsidian-cli tranche: `codex-query-vault` — read-only live `base:query`/`search`/`backlinks` vault access.                                                                              |
| 0.6.0           | json-canvas tranche: `codex-canvas-map` — Canvas relationship map for a hub note (links + backlinks) into `Architecture/`.                                                              |
| 0.7.0           | defuddle tranche: `codex-research-ingest` — fetch a URL via Defuddle into a source-stamped `Knowledge/` reference note.                                                                 |
| 0.8.0           | Vault archetypes: 4 research-backed specs (software-project/research/personal-pkm/technical-docs); `codex-init-vault --type` scaffolds from spec + writes a `.codex-vault.json` marker. |
| 0.9.0           | `PreToolUse(Write)` archetype naming-enforcement hook — structural filename + frontmatter gating, marker-gated and fail-open.                                                           |
| 0.10.0 (this)   | `codex-vault-lint` — audit a vault against its archetype spec (structural scanner + semantic layer) and apply renames/frontmatter fixes with backlink repair.                           |
| 0.6.0 (planned) | json-canvas tranche: Architecture canvases.                                                                                                                                             |
| 0.7.0 (planned) | defuddle tranche: clean research ingestion into `Knowledge/`.                                                                                                                           |

See [`docs/obsidian-leverage.md`](./docs/obsidian-leverage.md) for how each tranche maps to the `obsidian-skills` plugin, and the open-runway status.

## Layout

```
codex-workflow/
├── .claude-plugin/
│   └── plugin.json
├── hooks/
│   ├── hooks.json
│   └── scripts/
│       ├── codex-bootstrap.sh
│       ├── markdown-allowlist.sh
│       └── naming-enforcement.py
├── skills/
│   ├── codex-init-workspace/SKILL.md
│   ├── codex-init-vault/SKILL.md
│   ├── codex-init-rules/SKILL.md
│   ├── codex-mine-style/SKILL.md
│   ├── codex-add-refactor-entry/SKILL.md
│   ├── codex-mine-bases/SKILL.md
│   ├── codex-query-vault/SKILL.md
│   ├── codex-canvas-map/SKILL.md
│   ├── codex-research-ingest/SKILL.md
│   └── codex-vault-lint/SKILL.md
├── archetypes/
│   ├── README.md            ← archetype spec format + marker
│   ├── software-project.json
│   ├── research.json
│   ├── personal-pkm.json
│   └── technical-docs.json
├── references/
│   └── frontmatter-convention.md
├── docs/
│   └── obsidian-leverage.md
├── scripts/
│   └── vault-lint.py        ← deterministic vault scanner
├── examples/
│   └── codex-workflow.config.example.json
└── README.md
```

## Dependencies

Hook scripts require:

- `bash`
- `jq`
- `realpath` (part of GNU coreutils)
- `python3` (stdlib only — for the naming-enforcement hook)

All three are standard on Linux and recent macOS. Windows users running under WSL or Git Bash should also be fine.

Some skills have optional runtime dependencies (the skill degrades or instructs install when absent):

- `codex-query-vault`, `codex-canvas-map` — the [`obsidian` CLI](https://github.com/Yakitrak/obsidian-cli) and Obsidian running with the vault open.
- `codex-research-ingest` — the [`defuddle`](https://github.com/kepano/defuddle) CLI (`npm install -g defuddle`).
