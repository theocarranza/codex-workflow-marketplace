# codex-workflow — Build Status

Snapshot of the in-flight plugin build, captured for cross-session resumption. Update when state changes meaningfully.

## Where we are (2026-05-13)

**v0.1.0 — Layer 1 (hooks tranche) is built and locally tested. Not yet installed/tested via `/plugin install`.**

### Done

- Marketplace + plugin scaffolding (`.claude-plugin/marketplace.json`, `codex-workflow/.claude-plugin/plugin.json`).
- Two portable hook scripts:
  - `hooks/scripts/codex-bootstrap.sh` — SessionStart, reads `.claude/codex-workflow.config.json` for `codex.folder` + `codex.bootstrap[]`, autodetects `AI_Codex_*/` glob when no config, silent no-op when no codex folder exists.
  - `hooks/scripts/markdown-allowlist.sh` — PreToolUse on `Read|Grep`, reads config for `markdownAllowlist.patterns[]`, always allows the codex folder in full, defaults to `CLAUDE.md` / `GEMINI.md` / `.agent/*` / `projects/*/CLAUDE.md` / `projects/*/GEMINI.md` / `projects/*/.agent/*`.
- `hooks/hooks.json` wiring both hooks; uses `${CLAUDE_PLUGIN_ROOT}` to reference scripts.
- `examples/codex-workflow.config.example.json` showing the config shape.
- Plugin + marketplace READMEs.
- Local tests:
  - All 4 JSON files validate with `jq -e`.
  - Bootstrap script tested against `aplicatudo-monorepo` → emits valid `SessionStart` JSON with ~10KB injected context. Matches inline version.
  - Bootstrap script tested on directory without a codex → silent no-op (exit 0, no output).
  - Allowlist script 16/16 test cases pass (CLAUDE.md / GEMINI.md / .agent/* allowed; README.md / AGENTS.md / docs/* blocked; outside-repo and non-.md pass through; Write tool passes through; Grep with explicit `.md` path blocked).

### Not done (next steps in order)

1. **Git init + push.** Repo isn't under version control yet. User wanted to decide between local-directory install vs GitHub push for the first install test.
2. **Live install test.** Either via `/plugin marketplace add <local-path>` or `/plugin marketplace add <github-owner>/codex-workflow-marketplace`, then `/plugin install codex-workflow@codex-workflow-marketplace`. After install, `/hooks` to reload watcher in the current session (or new session for clean test).
3. **Cleanup of the inline hooks in `aplicatudo-monorepo`** once plugin install is confirmed working. The inline setup is at `aplicatudo-monorepo/.claude/hooks/` + the `hooks` block in `aplicatudo-monorepo/.claude/settings.json`. Plugin hooks layer/merge with project hooks, so leaving both will double-fire — not incorrect, just wasteful.
4. **Layer 2 skills (planned for v0.2.0):**
   - `codex-init-workspace` — scaffold the CLAUDE.md tree (root + per-project) by interrogating `package.json` / `pubspec.yaml`.
   - `codex-init-vault` — scaffold the Obsidian vault skeleton.
   - `codex-init-rules` — drop cross-cutting `.agent/rules/*.md` files.
5. **Layer 3 skills (planned for v0.3.0):**
   - `codex-mine-style` — interactive walkthrough that mines authored commits to draft canonical-style-examples notes.
   - `codex-add-refactor-entry` — takes a commit hash, proposes an entry for the Style Refactor Catalog.

## Key decisions (confirmed)

- **Plugin name:** `codex-workflow`
- **Marketplace name:** `codex-workflow-marketplace`
- **Plugin ID at install time:** `codex-workflow@codex-workflow-marketplace`
- **Dev directory:** `/home/corporaterick/Documents/Projects/codex-workflow-marketplace`
- **Plugin owner:** Théo Carranza
- **Hook scripts** read config from `${CLAUDE_PROJECT_DIR}/.claude/codex-workflow.config.json` (JSON, not YAML — keeps `jq` as the only parsing dependency).
- **Config-driven everything** with sensible zero-config defaults. Most users won't need a config file.
- **Codex folder is always fully allowed** in the allowlist (autodetected or from config), so codex internal cross-references work without listing patterns.

## Background (compressed)

This plugin extracts the workflow built in the `aplicatudo-monorepo` over the same session. That work:

1. Built a CLAUDE.md tree at the monorepo + per-project level (root + 6 project files).
2. Established a markdown allowlist (only `CLAUDE.md`, `GEMINI.md`, `.agent/**.md` are agent-readable inside the monorepo; the Obsidian vault `AI_Codex_Aplicatudo/` is fully allowed).
3. Wired two inline hooks (SessionStart Codex bootstrap + PreToolUse allowlist enforcement) at `aplicatudo-monorepo/.claude/`.
4. Designed the AI Codex (`AI_Codex_Aplicatudo/`) as the central hub for persistent agent knowledge — rule files in `.agent/rules/` route to canonical content in `AI_Codex_Aplicatudo/Knowledge/`.
5. Created three new Knowledge notes (`Dart_Functional_Style_Examples`, `TypeScript_Functional_Style_Examples`, `Style_Refactor_Catalog`) by mining the user's authored commits — these document the user's functional style with file/line anchors and refactor before/after pairs.

This plugin captures (1)–(3) of that work as portable, redistributable artifacts. (4) and (5) are project-specific outputs of the workflow that the future `codex-mine-style` skill will help produce in other projects.

## Resumption protocol

To pick up:

1. `cd /home/corporaterick/Documents/Projects/codex-workflow-marketplace`
2. Read this STATUS.md.
3. Optionally read the plugin's `codex-workflow/README.md` for what's exposed.
4. Run the same test commands shown in the "Done" section to confirm scripts still work in your environment.
5. Proceed with the next item in "Not done".

Test recipe (reproduce all 16 allowlist cases + bootstrap):

```bash
SCRIPTS=/home/corporaterick/Documents/Projects/codex-workflow-marketplace/codex-workflow/hooks/scripts
export CLAUDE_PROJECT_DIR=/home/corporaterick/Documents/Projects/aplicatudo-monorepo
echo '{}' | "$SCRIPTS/codex-bootstrap.sh" | jq -r '.hookSpecificOutput.hookEventName'
echo '{"tool_name":"Read","tool_input":{"file_path":"README.md"}}' | "$SCRIPTS/markdown-allowlist.sh" | jq -r '.hookSpecificOutput.permissionDecision'
# expect: SessionStart, deny
```
