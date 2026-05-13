# codex-workflow

Portable hooks (and, in upcoming versions, skills + templates) for the AI Codex workflow: a project layout pairing a code monorepo with an Obsidian vault that serves as the canonical agent knowledge base.

## What's in v0.1.0

Two hooks, configurable per project, with sensible zero-config defaults.

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
| 0.1.0 (this) | Hooks: SessionStart bootstrap + PreToolUse markdown allowlist. Config-driven, with autodetect fallback. |
| 0.2.0 (planned) | Skill `codex-init-workspace`: scaffolds the CLAUDE.md tree (root + per-project) from a project's `package.json` / `pubspec.yaml`. |
| 0.2.0 (planned) | Skill `codex-init-vault`: scaffolds the Obsidian vault skeleton (README + Knowledge/Agent_Orientation). |
| 0.2.0 (planned) | Skill `codex-init-rules`: drops cross-cutting `.agent/rules/*.md` files. |
| 0.3.0 (planned) | Skill `codex-mine-style`: interactive walkthrough that mines authored commits to draft canonical-style-examples notes. |
| 0.3.0 (planned) | Skill `codex-add-refactor-entry`: takes a commit hash and proposes an entry for the Style Refactor Catalog. |

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
