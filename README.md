# codex-workflow-marketplace

A single-plugin Claude Code marketplace shipping [`codex-workflow`](./codex-workflow) — portable hooks (and, soon, skills + templates) for the AI Codex workflow that pairs a code monorepo with an Obsidian vault as the agent's canonical knowledge base.

## For users

Add this marketplace and install the plugin in any project:

```
/plugin marketplace add <github-owner>/codex-workflow-marketplace
/plugin install codex-workflow@codex-workflow-marketplace
```

See [`codex-workflow/README.md`](./codex-workflow/README.md) for what the plugin does and how to configure it.

## For maintainers

Layout:

```
codex-workflow-marketplace/
├── .claude-plugin/
│   └── marketplace.json      ← marketplace manifest
├── codex-workflow/           ← the plugin itself
│   └── ...                   ← see plugin README
└── README.md                 ← this file
```

The marketplace manifest declares exactly one plugin (`codex-workflow`) sourced from the sibling directory.

## Versioning

Plugin version is declared in `codex-workflow/.claude-plugin/plugin.json` and mirrored in the marketplace manifest's `plugins[].version`. Bump both when releasing.
