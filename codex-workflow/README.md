# codex-workflow

Portable hooks and skills for the AI Codex workflow: a project layout pairing a codebase with an Obsidian vault that serves as the canonical agent knowledge base.

## What's in v0.7.0

Two hooks, three init skills, three mining skills, one live query skill, one Canvas generator, and one research-ingest skill — all configurable per project with sensible zero-config defaults.

### Init skills

- `/codex-workflow:codex-init-workspace` — scaffold the CLAUDE.md tree (root + per-project) by inspecting `package.json` / `pubspec.yaml`.
- `/codex-workflow:codex-init-vault` — scaffold the Obsidian vault skeleton (README, Knowledge/, Agent_Sessions/, Tickets/, Architecture/, Features/, Agent_Reports/, assets/).
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

## Installation

Add the marketplace once per machine, then install the plugin:

```
/plugin marketplace add <your-github-owner>/codex-workflow-marketplace
/plugin install codex-workflow@codex-workflow-marketplace
```

After installation, open `/hooks` (or restart Claude Code) to ensure the watcher picks up the new hooks for the current session. New sessions get them automatically.

## Configuration

Most projects need zero configuration — the defaults match the convention this plugin assumes.

If you want to customize, drop a file at `.claude/codex-workflow.config.json` in your project. See `examples/codex-workflow.config.example.json` for the schema. Every key is optional; omitted keys fall back to the defaults above.

## Roadmap

| Version | Adds |
|---|---|
| 0.1.0 | Hooks: SessionStart bootstrap + PreToolUse markdown allowlist. Config-driven, with autodetect fallback. |
| 0.1.1 | Hooks: broaden `AI_Codex*/` autodetect glob; silently skip missing bootstrap files. |
| 0.2.0 | Init skills: `codex-init-workspace`, `codex-init-vault`, `codex-init-rules`. |
| 0.3.0 | Mining skills: `codex-mine-style`, `codex-add-refactor-entry`. |
| 0.4.0 | Bases tranche: `codex-mine-bases` skill + frontmatter convention; `codex-init-vault` now emits `.base` dashboards (Tickets/Features/Agent_Sessions). |
| 0.5.0 | obsidian-cli tranche: `codex-query-vault` — read-only live `base:query`/`search`/`backlinks` vault access. |
| 0.6.0 | json-canvas tranche: `codex-canvas-map` — Canvas relationship map for a hub note (links + backlinks) into `Architecture/`. |
| 0.7.0 (this) | defuddle tranche: `codex-research-ingest` — fetch a URL via Defuddle into a source-stamped `Knowledge/` reference note. |
| 0.6.0 (planned) | json-canvas tranche: Architecture canvases. |
| 0.7.0 (planned) | defuddle tranche: clean research ingestion into `Knowledge/`. |

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
│       └── markdown-allowlist.sh
├── skills/
│   ├── codex-init-workspace/SKILL.md
│   ├── codex-init-vault/SKILL.md
│   ├── codex-init-rules/SKILL.md
│   ├── codex-mine-style/SKILL.md
│   ├── codex-add-refactor-entry/SKILL.md
│   ├── codex-mine-bases/SKILL.md
│   ├── codex-query-vault/SKILL.md
│   ├── codex-canvas-map/SKILL.md
│   └── codex-research-ingest/SKILL.md
├── references/
│   └── frontmatter-convention.md
├── docs/
│   └── obsidian-leverage.md
├── examples/
│   └── codex-workflow.config.example.json
└── README.md
```

## Dependencies

Hook scripts require:

- `bash`
- `jq`
- `realpath` (part of GNU coreutils)

All three are standard on Linux and recent macOS. Windows users running under WSL or Git Bash should also be fine.

Some skills have optional runtime dependencies (the skill degrades or instructs install when absent):

- `codex-query-vault`, `codex-canvas-map` — the [`obsidian` CLI](https://github.com/Yakitrak/obsidian-cli) and Obsidian running with the vault open.
- `codex-research-ingest` — the [`defuddle`](https://github.com/kepano/defuddle) CLI (`npm install -g defuddle`).
