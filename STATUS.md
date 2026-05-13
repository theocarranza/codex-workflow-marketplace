# codex-workflow — Build Status

Snapshot of the in-flight plugin build, captured for cross-session resumption. Update when state changes meaningfully.

## Where we are (2026-05-13)

**v0.2.0 — Layer 2 (init skills tranche) is built, validated, and pushed. v0.1.1 hooks are installed live.**

### Done

**v0.1.0 — Hooks tranche (committed `6d10cc8`, pushed to `origin/main`).**
- Marketplace + plugin scaffolding (`.claude-plugin/marketplace.json`, `codex-workflow/.claude-plugin/plugin.json`).
- Two portable hook scripts:
  - `hooks/scripts/codex-bootstrap.sh` — SessionStart, reads `.claude/codex-workflow.config.json` for `codex.folder` + `codex.bootstrap[]`, autodetects `AI_Codex*/` glob when no config, silent no-op when no codex folder exists.
  - `hooks/scripts/markdown-allowlist.sh` — PreToolUse on `Read|Grep`, reads config for `markdownAllowlist.patterns[]`, always allows the codex folder in full, defaults to `CLAUDE.md` / `GEMINI.md` / `.agent/*` / `projects/*/CLAUDE.md` / `projects/*/GEMINI.md` / `projects/*/.agent/*`.
- `hooks/hooks.json` wiring both hooks; uses `${CLAUDE_PLUGIN_ROOT}` to reference scripts.
- `examples/codex-workflow.config.example.json` showing the config shape.
- Plugin + marketplace READMEs.

**v0.1.1 — Hook portability patch (committed `b5782b2`, pushed; installed locally).**
- Glob relaxed `AI_Codex_*/` → `AI_Codex*/` so vaults named `AI_Codex/` are autodetected.
- Missing bootstrap files silently skipped (previously emitted noisy `(missing: ...)` placeholders).
- Marketplace + plugin manifests bumped to 0.1.1.
- Plugin installed via `/plugin marketplace add theocarranza/codex-workflow-marketplace` + `/plugin install codex-workflow@codex-workflow-marketplace` + `/reload-plugins`. Behavioral validation: Read on `aplicatudo-monorepo/README.md` is denied by the plugin's allowlist (confirmed live in-session).

**v0.2.0 — Init skills tranche (pushed; awaiting user-side refresh + verification).**
- Three new skills under `codex-workflow/skills/`:
  - `codex-init-workspace/SKILL.md` — interactive walkthrough that inspects `package.json` / `pubspec.yaml` / `angular.json` / `pnpm-workspace.yaml`, detects project shape (single vs monorepo) and per-project stacks, then scaffolds the root + per-project CLAUDE.md tree from stack-specific templates. Never overwrites without per-file approval.
  - `codex-init-vault/SKILL.md` — interactive walkthrough that picks a vault folder name (default `AI_Codex_<ProjectName>`), refuses if vault exists, scaffolds the full skeleton (`README.md`, `Knowledge/Agent_Orientation.md`, `Agent_Sessions/README.md`, plus `.gitkeep`-anchored empty dirs).
  - `codex-init-rules/SKILL.md` — drops a starter `.agent/rules/*.md` set (`strict-implementation-lock`, `rules-architect-protocol`, `rules-git-workflow`, `rules-date-time-handling`).
- All three carry `disable-model-invocation: true` (side effects → user-triggered only) and tight `allowed-tools` whitelists.
- v0.1.1 cosmetic: comment headers in both hook scripts aligned (`AI_Codex_*` → `AI_Codex*/`) to match what the code actually globs. Folded into the v0.2.0 push, no separate version bump.
- Plugin README rewritten to surface init skills first; roadmap table updated.
- Manifests bumped to 0.2.0; `jq -e` clean.

### Not done (next steps in order)

1. **User-side refresh of v0.2.0.** `/plugin marketplace update codex-workflow-marketplace` (expect "1 plugin bumped") then `/reload-plugins`. Verify `/codex-workflow:codex-init-workspace`, `:codex-init-vault`, `:codex-init-rules` all appear in `/skills`. Optional: invoke one in a scratch directory and watch the inspection step run.
2. **Layer 3 skills (planned for v0.3.0):**
   - `codex-mine-style` — interactive walkthrough that mines authored commits (`git log --author=<email> --no-merges --name-only`), reads anchor files, drafts canonical-style-examples notes with file/line anchors.
   - `codex-add-refactor-entry` — takes a commit hash via `$ARGUMENTS`, runs `git show`, drafts a before/after entry for the Style Refactor Catalog.
3. **Deferred (parked by user):** cleanup of the inline hooks in `aplicatudo-monorepo/.claude/` (would otherwise double-fire alongside plugin hooks). Tracked in the prior session's Pending Tasks.

## Key decisions (confirmed)

- **Plugin name:** `codex-workflow`
- **Marketplace name:** `codex-workflow-marketplace`
- **Plugin ID at install time:** `codex-workflow@codex-workflow-marketplace`
- **Dev directory:** `/home/corporaterick/Documents/Projects/codex-workflow-marketplace`
- **Plugin owner:** Théo Carranza
- **Hook scripts** read config from `${CLAUDE_PROJECT_DIR}/.claude/codex-workflow.config.json` (JSON, not YAML — keeps `jq` as the only parsing dependency).
- **Config-driven everything** with sensible zero-config defaults. Most users won't need a config file.
- **Codex folder is always fully allowed** in the allowlist (autodetected or from config), so codex internal cross-references work without listing patterns.
- **Skills are Claude-driven interactive walkthroughs**, not shell-scripted scaffolds. Each one inspects → proposes → confirms → writes. Existing files never overwritten without per-file approval.
- **All skills carry `disable-model-invocation: true`** — they have side effects (file creation), so they're user-triggered only.

## Background (compressed)

This plugin extracts the workflow built in the `aplicatudo-monorepo` over the same day. That workflow:

1. CLAUDE.md tree at the monorepo + per-project level (root + 6 project files) — what `codex-init-workspace` produces.
2. Markdown allowlist (only `CLAUDE.md`, `GEMINI.md`, `.agent/**.md` agent-readable; vault fully allowed) — what the `markdown-allowlist.sh` hook enforces.
3. Two inline hooks (SessionStart codex bootstrap + PreToolUse allowlist enforcement) — what the plugin's hooks tranche is.
4. The AI Codex (`AI_Codex_Aplicatudo/`) as the central hub for persistent agent knowledge — what `codex-init-vault` scaffolds.
5. Three Knowledge notes mined from authored commits (`Dart_Functional_Style_Examples`, `TypeScript_Functional_Style_Examples`, `Style_Refactor_Catalog`) — what the future `codex-mine-style` + `codex-add-refactor-entry` skills will help produce in other projects.

## Resumption protocol

To pick up:

1. `cd /home/corporaterick/Documents/Projects/codex-workflow-marketplace`.
2. Read this STATUS.md.
3. Optionally read the plugin's `codex-workflow/README.md` for what's exposed.
4. Run the validation recipe below to confirm scripts + manifests still work.
5. Proceed with the next item in "Not done" (v0.2.0 user-side refresh, then v0.3.0 work).

Test recipe (manifests + hook scripts):

```bash
cd /home/corporaterick/Documents/Projects/codex-workflow-marketplace
jq -e . codex-workflow/.claude-plugin/plugin.json
jq -e . .claude-plugin/marketplace.json

SCRIPTS=codex-workflow/hooks/scripts
export CLAUDE_PROJECT_DIR=/home/corporaterick/Documents/Projects/aplicatudo-monorepo
echo '{}' | "$SCRIPTS/codex-bootstrap.sh" | jq -r '.hookSpecificOutput.hookEventName'
echo '{"tool_name":"Read","tool_input":{"file_path":"README.md"}}' | "$SCRIPTS/markdown-allowlist.sh" | jq -r '.hookSpecificOutput.permissionDecision'
# expect: SessionStart, deny
```
