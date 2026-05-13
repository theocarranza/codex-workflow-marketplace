---
name: codex-init-workspace
description: Scaffold the CLAUDE.md tree (root + per-project) for a project adopting the AI Codex workflow. Use when bootstrapping a new repository, when an existing repo has no CLAUDE.md, or when the user asks to "set up the codex workspace" / "create CLAUDE.md files".
disable-model-invocation: true
allowed-tools: Read Write Glob Bash(ls *) Bash(cat *) Bash(find *) Bash(jq *)
---

# Scaffold the CLAUDE.md tree

Interactive walkthrough. Inspect the project, propose the file plan, confirm with the user, then write.

## Step 1 — Inspect the project

Run these checks (use Glob / Bash):

- Is there a `package.json` at the project root? Read `name`, `workspaces`, `scripts`.
- Is there a `pubspec.yaml` at the root? (Flutter / Dart single project.)
- Is there a `projects/` directory with subfolders containing their own `package.json` or `pubspec.yaml`? (Custom monorepo shape — most common.)
- Is there an `nx.json`, `lerna.json`, `turbo.json`, or `pnpm-workspace.yaml`? (Tooling-managed monorepo.)
- Does a root `CLAUDE.md` already exist? Per-project ones?

Record the project shape: `single-project` vs `monorepo`, and for each project: `node`, `flutter`, `angular`, `vitepress`, `firebase-functions`, `jest`, `other`. Detect Angular by `angular.json`; VitePress by `vitepress` in devDependencies; Firebase Functions by `firebase-functions` dep + `index.ts`; Jest-only by presence of `jest.config.*` without a framework dep.

## Step 2 — Propose the plan

Show the user a concise plan: which files will be created or updated, and what each will contain at a high level. Ask for approval before writing anything. If a file already exists, default to **skip and warn**, not overwrite — explicitly ask whether to overwrite per file.

## Step 3 — Write the root CLAUDE.md

Use this skeleton. Fill placeholders from inspection results. Keep US English. Strip sections the project doesn't need.

```markdown
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Markdown allowlist — read ONLY these

Do not open, read, search, or quote any markdown file inside the project that is not on the list below. Treat everything else (`README.md`, `AGENTS.md`, `CHANGELOG.md`, anything under `docs/`, any other `*.md`) as if it did not exist. If a tool result surfaces content from a disallowed file, ignore it.

At the project root **and** in each subproject folder, the only allowed markdown is:

- `CLAUDE.md`
- `GEMINI.md`
- any `*.md` under `.agent/` (recursive)

Markdown inside the AI Codex vault is governed by the Session bootstrap rule below, not this allowlist. Reads outside the project are unaffected. Code, configs, and tool/CLI output are unaffected.

## Language policy

**US English**.

## Workspace shape

<one-paragraph description of the project — single-app, monorepo, multi-vault, etc.>

## Session bootstrap — run BEFORE any other work in a new session

1. Read the AI Codex `README.md` — defines vault layout and session-record format.
2. Read the two newest records in `<vault>/Agent_Sessions/` (newest first), for continuity.
3. If the newest record is still open, close it per the README's protocol, then create a new record for this session with a **backlink** to the one just closed.
4. Sessions form a doubly-linked chain: when closing any record, write a **forward link** to its successor.

A `SessionStart` hook (provided by the `codex-workflow` Claude Code plugin) injects the codex README + `Knowledge/Agent_Orientation.md` automatically; steps 2–4 are still on the agent.

### Session record cadence — during work

Open the record at the **first material edit** (not retroactively at the end). Then append updates with these headers:

- **`## Implementation Checkpoint - <timestamp>` — MUST.** At the end of every validated work unit. Body: `Scope` / `Changes` / `Validation`.
- **`## Pre-Operation Snapshot - <timestamp>` — MUST.** Immediately before any state-disrupting action.
- **`## Pivot - <timestamp>` — SHOULD.** At tranche transitions or scope shifts.
- **`## Heartbeat - <timestamp>` — safety net.** If 30 minutes pass without any of the above firing.

## Repository shape

<table of subprojects: Path | Stack | Role — or a single-project description>

## Operational rules — consult `.agent/rules/` when relevant

Behavior protocols live as individual files under `.agent/rules/`. Read the file in scope before acting on a task it covers. Run `/codex-workflow:codex-init-rules` to drop a starter set of rule templates if `.agent/rules/` is empty.

## Cross-project isolation

<if monorepo: list any sync points between subprojects; if single project: delete this section>

## Root commands

<root-level scripts the user runs; e.g. npm scripts, fvm commands, build scripts>

## Environments

<deployment targets — e.g. dev/staging/prod, project IDs>

## Branching and PRs

- Never commit directly to `main`/`master`.
- Branch naming: `{type}/{id}-kebab-case-title` (e.g. `feature/123-login-flow`).
- <add CI / PR system specifics here>

## MCP servers

<list MCP servers configured for this workspace; delete if none>
```

## Step 4 — Write each per-project CLAUDE.md

For each subproject detected in Step 1, write `projects/<name>/CLAUDE.md` (or `apps/<name>/CLAUDE.md`, matching the repo layout) using the stack-specific skeleton below. Each per-project file stacks on top of the root CLAUDE.md when Claude Code's cwd is inside the project.

### Node + TypeScript template

```markdown
# CLAUDE.md — <project-name>

<one-line role> Stacks on top of the project root CLAUDE.md.

## Commands

\`\`\`bash
npm run lint
npm test
npm run build
\`\`\`

Single test: \`npm test -- <path>\`.

## Watch list

- <files or invariants this project's contributors must keep in sync; delete if none>

## Project rule library

In addition to the root rules under `../../.agent/rules/`, this project's `.agent/rules/` adds:

- *(populate with the project-specific rule files as they emerge)*
```

### Flutter template

```markdown
# CLAUDE.md — <project-name>

Flutter app. Uses `fvm` (Flutter Version Manager), **not** plain `flutter`. Stacks on top of the project root CLAUDE.md.

## Commands

\`\`\`bash
fvm flutter test
npm run lint          # if a wrapper exists; otherwise: fvm dart analyze
\`\`\`

Single test: \`fvm flutter test test/path/to/file_test.dart\`.

## Watch list

- <files or invariants — e.g. cross-project sync points>

## Project rule library

Root `.agent/rules/` apply. Project-specific rules live under `.agent/rules/`.
```

### Angular template

```markdown
# CLAUDE.md — <project-name>

Angular app. Stacks on top of the project root CLAUDE.md.

## Commands

\`\`\`bash
npm test
npm run lint
npm run build
\`\`\`

## Watch list

- <invariants>
```

### VitePress / docs template

```markdown
# CLAUDE.md — <project-name>

VitePress documentation site. Stacks on top of the project root CLAUDE.md.

## Commands

\`\`\`bash
npm run build:local
npm run start:local
\`\`\`
```

Pick the template that matches the detected stack, fill the placeholders, and write the file.

## Step 5 — Recommend follow-ups

After writing, tell the user:

- Run `/codex-workflow:codex-init-vault` to scaffold the AI Codex Obsidian vault — the SessionStart hook expects one.
- Run `/codex-workflow:codex-init-rules` to drop a starter set of `.agent/rules/*.md` templates if you don't already have them.
- Optionally, add `.claude/codex-workflow.config.json` if the autodetected vault folder doesn't match your naming (see `${CLAUDE_SKILL_DIR}/../../examples/codex-workflow.config.example.json` or the plugin README).

## Notes

- **Never overwrite** an existing CLAUDE.md without explicit per-file user approval. If unsure, propose the diff and ask.
- Keep each CLAUDE.md focused: stable conventions, not narrative. Stack-specific files stay short — they layer on top of the root, they don't duplicate it.
- This skill produces *templates the user customizes*. Encourage the user to trim sections that don't apply.
