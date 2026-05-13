# codex-workflow

Portable hooks and skills for the AI Codex workflow: a project layout pairing a codebase with an Obsidian vault that serves as the canonical agent knowledge base.

## What's in v0.2.0

Two hooks plus three init skills, all configurable per project with sensible zero-config defaults.

### Init skills

- `/codex-workflow:codex-init-workspace` — scaffold the CLAUDE.md tree (root + per-project) by inspecting `package.json` / `pubspec.yaml`.
- `/codex-workflow:codex-init-vault` — scaffold the Obsidian vault skeleton (README, Knowledge/, Agent_Sessions/, Tickets/, Architecture/, Features/, Agent_Reports/, assets/).
- `/codex-workflow:codex-init-rules` — drop a starter set of `.agent/rules/*.md` template files (`strict-implementation-lock`, `rules-architect-protocol`, `rules-git-workflow`, `rules-date-time-handling`).

Each init skill is an interactive walkthrough: it inspects current project state, proposes a plan, asks the user to confirm, then writes. Existing files are never overwritten without explicit per-file approval.

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
| 0.2.0 (this) | Init skills: `codex-init-workspace`, `codex-init-vault`, `codex-init-rules`. |
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
├── skills/
│   ├── codex-init-workspace/SKILL.md
│   ├── codex-init-vault/SKILL.md
│   └── codex-init-rules/SKILL.md
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
