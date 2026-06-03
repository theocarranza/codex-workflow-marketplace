# codex-workflow — Build Status

Snapshot of the in-flight plugin build, captured for cross-session resumption. Update when state changes meaningfully.

## Where we are (2026-06-02)

**v0.4.0 — Bases tranche shipped, pushed, and validated both ways. Adds the `codex-mine-bases` skill, the frontmatter convention reference, and `.base` emission in `codex-init-vault`. Validated (a) migrate-existing: full `AI_Codex_Aplicatudo` migration — 100% frontmatter coverage across Tickets/Features/Agent_Sessions, 9 backfilled + 12 legacy notes normalized (stale `status:` drift removed, id fields unified to `ticket`), 3 Bases rendering live in Obsidian; and (b) cold-start: a fresh `codex-init-vault` scaffold whose Board populates and whose "Needs metadata" view correctly catches a frontmatter-less note. All tranches v0.1.0–v0.4.0 shipped and pushed.**

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

**v0.2.0 — Init skills tranche (committed `9af4b88`, pushed; live-validated).**
- Three new skills under `codex-workflow/skills/`:
  - `codex-init-workspace/SKILL.md` — interactive walkthrough that inspects `package.json` / `pubspec.yaml` / `angular.json` / `pnpm-workspace.yaml`, detects project shape (single vs monorepo) and per-project stacks, then scaffolds the root + per-project CLAUDE.md tree from stack-specific templates. Never overwrites without per-file approval.
  - `codex-init-vault/SKILL.md` — interactive walkthrough that picks a vault folder name (default `AI_Codex_<ProjectName>`), refuses if vault exists, scaffolds the full skeleton (`README.md`, `Knowledge/Agent_Orientation.md`, `Agent_Sessions/README.md`, plus `.gitkeep`-anchored empty dirs).
  - `codex-init-rules/SKILL.md` — drops a starter `.agent/rules/*.md` set (`strict-implementation-lock`, `rules-architect-protocol`, `rules-git-workflow`, `rules-date-time-handling`).
- All three carry `disable-model-invocation: true` (side effects → user-triggered only) and tight `allowed-tools` whitelists.
- v0.1.1 cosmetic: comment headers in both hook scripts aligned (`AI_Codex_*` → `AI_Codex*/`) to match what the code actually globs. Folded into the v0.2.0 push, no separate version bump.
- Plugin README rewritten to surface init skills first; roadmap table updated.
- Manifests bumped to 0.2.0; `jq -e` clean.
- Live-validated post-refresh: `/skills` lists all three with `locked by author` (matches `disable-model-invocation: true`) at ~100–120 tokens each.

**v0.3.0 — Mining skills tranche (pushed; awaiting user-side refresh + verification).**
- Two new skills under `codex-workflow/skills/`:
  - `codex-mine-style/SKILL.md` — interactive walkthrough that gathers commits via `git log --author --no-merges`, surfaces high-frequency files, samples patterns, drafts a `<Stack>_Functional_Style_Examples.md` Knowledge note with 6–10 file/line anchors and an Agent Rules block.
  - `codex-add-refactor-entry/SKILL.md` — takes a commit hash via `$ARGUMENTS`, validates with `git rev-parse`, reads the diff, drafts a before/after Catalog entry annotated with the principle applied, appends after confirmation.
- Both carry `disable-model-invocation: true`. `codex-add-refactor-entry` declares `argument-hint: <commit-hash>`.
- Plugin README rewritten to surface both layers; roadmap table marks v0.3.0 shipped (no more "(planned)" rows).
- Manifests bumped to 0.3.0; `jq -e` clean.

**v0.4.0 — Bases tranche (built locally, not yet committed/pushed).**
- New reference `codex-workflow/references/frontmatter-convention.md` — the property schema (`ticket`/`type`/`area`/`stack`/`tags`/`created`), the core rule (**status encoded by folder, never in frontmatter**), and the tested Bases formula gotcha (no list `.last()`/index — derive the status lane with `file.folder.replace("Tickets/", "")`, not `split("/").last()`).
- New skill `codex-workflow/skills/codex-mine-bases/SKILL.md` — interactive: survey vault → confirm vocabulary → backfill frontmatter on notes lacking it (safe prepend, skips notes that already have `---`) → write `Tickets.base`/`Features.base`/`Agent_Sessions.base` (each with a self-tracking "Needs metadata" view) → optional in-vault convention note. `disable-model-invocation: true`.
- `codex-init-vault/SKILL.md` updated: Tickets skeleton now `Active/Ready/Closed/Resolved`; emits the three `.base` dashboards; `.gitkeep` list, Agent_Orientation slash-command table, and Agent Guidelines updated for the convention.
- Plugin README rewritten to surface the Bases tranche; roadmap table marks v0.4.0 shipped. Manifests bumped 0.3.0 → 0.4.0.
- **Live prototype on the real vault** (kept): `AI_Codex_Aplicatudo/Tickets.base` + frontmatter backfilled on `Feature 6196` and `feature-5632`. Board groups by the four status lanes; user confirmed it renders.

**v0.4.0 validation (both paths exercised).**
- Committed `41a6bc6`, pushed to `origin/main`; user ran `/plugin marketplace update` + `/reload-plugins`.
- **Migrate-existing path** — drove `codex-mine-bases` by hand over `AI_Codex_Aplicatudo`: backfilled the 7 Tickets + 2 Features lacking frontmatter, normalized 12 legacy notes (renamed `work_item_id`/`ticket_id`/`id` → `ticket`, dropped stale `status:` incl. two `status: active` notes mis-sitting in `Resolved/`, stripped folder-encoded tags, added `area`/`stack`), wrote `Features.base` + `Agent_Sessions.base`, removed an empty `Untitled.md` stub, moved a misfiled ValueNotifier article to `Knowledge/`. Result: 63 frontmatter blocks parse clean, all 3 Bases render in Obsidian (Obsidian normalized them on open). Vocab settled to `type ∈ {feature, tech-debt, ticket}`, `area ∈ {terms-of-use, attendance, calendar, onboarding}`.
- **Cold-start path** — scaffolded a fresh vault per `codex-init-vault` v0.4.0 in `/tmp`; Board populated from sample tickets grouped by status folder, and a deliberately bare note surfaced only in "Needs metadata". Confirms the from-scratch flow.
- **Finding folded into the reference:** Obsidian rewrites `.base` files on open — strips comments, normalizes flow-style to block-style, adds `columnSize` on column resize. Emitted comments are cosmetic-only.

### Not done (next steps in order)

1. **Commit the `aplicatudo` vault migration** in the monorepo repo (separate from this plugin repo) — the backfill/normalization edits are currently uncommitted working-tree changes. (User's content; left for the user to commit.)
2. **Deferred (parked by user):** cleanup of the inline hooks in `aplicatudo-monorepo/.claude/` (would otherwise double-fire alongside plugin hooks). Tracked in the 2026-05-13 06:56:37 session's Pending Tasks.

The original roadmap is feature-complete: v0.4.0 is shipped and validated both ways.

**Beyond v0.4.0 — obsidian-skills leverage runway** (full map in `codex-workflow/docs/obsidian-leverage.md`):

- **v0.5.0 — obsidian-cli tranche (SHIPPED, validated; awaiting push + user refresh).** New read-only skill `codex-query-vault` wraps the `obsidian` CLI for live vault state: `base:query` (open tickets via path-lane, features by area, recent sessions), `search`/`search:context`, `backlinks`. First skill that **allows model invocation** (read-only). Degrades gracefully when Obsidian isn't running. Dogfooded against the live `AI_Codex_Aplicatudo`: returns the 3 open tickets (1 Active, 2 Ready) correctly. Manifests bumped 0.4.0 → 0.5.0. CLI gotchas captured: bases resolve by `path=` not `file=`; `base:views` is unreliable; Board JSON has no `status` column (read it off `path`).
- **v0.6.0 — json-canvas tranche (SHIPPED, validated; awaiting push + user refresh).** New skill `codex-canvas-map` (`disable-model-invocation`, `argument-hint: <hub-note-name>`): builds an Obsidian `.canvas` relationship map — hub note centered, outgoing `links` one side, `backlinks` the other, arrowed edges — into `Architecture/`. Composes the v0.5.0 CLI channel (`obsidian links`/`backlinks`) with the JSON Canvas spec; validates node/edge integrity + file-path existence before declaring done. Dogfooded: generated `Architecture/Domain_Legal Map.canvas` (10 nodes / 9 edges, all paths resolve). Manifests 0.5.0 → 0.6.0.
- **v0.7.0 — defuddle tranche (SHIPPED, validated; awaiting push + user refresh).** Defuddle CLI installed (`npm i -g defuddle`, v0.18.1). New skill `codex-research-ingest` (`disable-model-invocation`, `argument-hint: <url>`): `defuddle parse <url> --md` + `-p title`/`-p domain` → a `type: reference` Knowledge note with `source`/`domain`/`retrieved` frontmatter and a provenance callout; skips Defuddle for `.md` URLs; degrades when Defuddle absent. Distinct from raw `obsidian:defuddle` (which only extracts) — this files the result into the vault + index. Dogfooded: ingested `https://jsoncanvas.org/spec/1.0/` → `Knowledge/JSON_Canvas_Spec.md` (3827 chars, frontmatter parses). Manifests 0.6.0 → 0.7.0.

**Runway complete.** All three obsidian-skills leverage items (A obsidian-cli, B json-canvas, C defuddle) are shipped and validated, on top of the v0.4.0 bases+markdown work. Every one of the five obsidian-skills is now leveraged by codex-workflow.

## Vault archetypes initiative (v0.8.0+)

Motivated by an audit of the live vault showing severe naming/structure drift (30/69 files off-pattern) and the realization that folder structure was never researched. Decisions: ship all four archetypes; **hard hook only** for enforcement; build a linter. Research synthesized into `codex-workflow/docs/obsidian-leverage.md` references + `archetypes/README.md` (PARA / Zettelkasten / MOC / Diataxis; flat-over-deep; folders=where, tags=what; literature-driven naming, not vault-driven).

- **v0.8.0 — archetype specs + spec-driven init (SHIPPED, validated; awaiting push + user refresh).** Four machine-readable specs in `codex-workflow/archetypes/*.json` (folders[], naming rules[], frontmatter rules[]) + format `README.md`. Naming chosen from the literature (Obsidian-native Title Case for notes; Nygard ADR convention for `Architecture/ADR`; citekeys for Literature; kebab for Diataxis docs; timestamp IDs for journals). `codex-init-vault` rewritten to be archetype-driven: `--type`, scaffolds folders from the spec, writes a `.codex-vault.json` marker (type+specVersion) that the hook/linter key off. Dogfooded: all four archetypes scaffold cleanly; software-project spec flags exactly the 30 off-pattern files in the live vault. Manifests 0.7.0 → 0.8.0.
- **v0.9.0 — PreToolUse(Write) structural-enforcement hook (NEXT).** Reads the marker → the spec; rejects wrong filename shape / missing-required / forbidden frontmatter; fail-open outside a marked vault.
- **v0.10.0 — codex-vault-lint skill.** Semantic audit (language, duplicates, stray files) + rename/fix proposals.

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
