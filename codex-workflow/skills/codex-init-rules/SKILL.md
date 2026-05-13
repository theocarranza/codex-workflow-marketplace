---
name: codex-init-rules
description: Drop a starter set of `.agent/rules/*.md` template files (strict-implementation-lock, rules-architect-protocol, rules-git-workflow, rules-date-time-handling) at the project root. Use when bootstrapping a project that has no `.agent/rules/` yet, or when the user asks to "scaffold the agent rules" / "drop starter rule templates".
disable-model-invocation: true
allowed-tools: Read Write Glob Bash(ls *) Bash(mkdir *)
---

# Drop the starter `.agent/rules/` set

Interactive walkthrough. Inspect, propose, confirm, write.

## Step 1 — Inspect

Check for `.agent/rules/` at the project root. If it exists, list its contents.

## Step 2 — Propose

Show the user the four starter files this skill writes:

| File | Purpose |
| --- | --- |
| `strict-implementation-lock.md` | Plan-then-execute gate. Explicit user approval required before mutating code on substantial work. |
| `rules-architect-protocol.md` | Global posture, conservatism stance, anti-ambiguity defaults. |
| `rules-git-workflow.md` | Conventional commits, atomicity, branching. |
| `rules-date-time-handling.md` | UTC immutability and timezone-anchored bucketing. |

For each file that **already exists**, ask the user per-file whether to skip or overwrite. Default to skip.

Confirm before writing.

## Step 3 — Write the files

If `.agent/rules/` doesn't exist, create it.

### `.agent/rules/strict-implementation-lock.md`

```markdown
# Strict Implementation Lock

**Plan-then-execute gate.** For any non-trivial change, propose a plan and wait for explicit user approval before mutating code.

## What counts as "substantial work"

- Anything spanning more than one file, *unless* it's a single-line typo fix.
- Anything touching production code paths (not just tests or docs).
- Anything that introduces a new dependency, abstraction, or pattern.
- Refactors of any size.

## What does NOT need approval

- Reading, searching, browsing the codebase.
- Running tests, linters, type-checkers, formatters in read-only mode.
- Editing your own scratch notes, session records, or task lists.

## Protocol

1. State your plan: which files, what changes, why.
2. Wait for explicit approval (e.g., "proceed", "go ahead", "do it"). Silence is not approval.
3. After implementation, summarize what changed and what's next.

## Why

Past incidents where speculative edits broke unrelated areas. The cost of a 30-second pause is far lower than the cost of an unwanted change being reverted.
```

### `.agent/rules/rules-architect-protocol.md`

```markdown
# Architect Protocol

Global posture for agent-driven work in this project.

## Conservatism

- **Edit existing files** over creating new ones. New files require justification.
- **No speculative abstractions.** Two similar lines beats a premature helper.
- **No backwards-compat shims** when you can just change the code.
- **Don't add error handling for scenarios that can't happen.** Trust internal code and framework guarantees. Validate at system boundaries only.

## Anti-ambiguity

- If the user's request is genuinely ambiguous, ask **one specific question** rather than guessing. But spend up to a minute on read-only investigation first — many "ambiguous" requests resolve with a grep.
- Prefer the smallest interpretation that satisfies the request.

## Code quality

- Default to **no comments**. Add one only when the *why* is non-obvious.
- Don't narrate what the code does — well-named identifiers do that.
- Don't reference the current task, fix, or callers in comments. That belongs in the commit message.

## Communication

- Match response length to task complexity. A simple question gets a direct answer, not headers and sections.
- Don't summarize what you just did at the end of every response — the user can read the diff.
```

### `.agent/rules/rules-git-workflow.md`

```markdown
# Git Workflow

## Commit messages

[Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <subject>

<body — optional, wrapped at 72 chars>
```

Types: `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `chore`, `style`, `ci`, `build`.

## Atomicity

- One logical change per commit. If you need "and" in the subject, split.
- Tests, types, and the code they verify can land together — they're one logical change.
- Don't mix mechanical refactors (renames, moves) with behavior changes.

## Branching

- Never commit directly to `main`/`master` / `develop`.
- Branch naming: `{type}/{id}-kebab-case-title` (e.g. `feature/123-login-flow`, `bugfix/456-fix-crash`).
- Rebase onto the integration branch before opening a PR. No merge commits in feature branches.

## Hooks and signing

- Never skip hooks (`--no-verify`) or bypass signing unless the user explicitly asks for it. If a hook fails, fix the underlying issue.
- Don't update git config (user.email, user.name, signing keys) without explicit user direction.

## Destructive operations

Always confirm with the user before:

- `git reset --hard`, `git push --force` / `--force-with-lease`.
- `git checkout .` / `git restore .` / `git clean -f`.
- `git branch -D` on anything not strictly local-throwaway.
```

### `.agent/rules/rules-date-time-handling.md`

```markdown
# Date and Time Handling

## Storage

- **Always store timestamps in UTC.** Never store local time.
- Store as ISO-8601 strings (`2026-05-13T11:24:59Z`) or as `Timestamp`/`DateTime` types that preserve the UTC instant.

## Display

- Convert UTC → user's local time at the display layer only. Never re-store the converted value.
- Display layer is always closest to the user (UI, API response serialization).

## Bucketing

- "Day", "week", "month" boundaries are **timezone-anchored**, not UTC-anchored, when the bucket is user-visible.
  - Example: "today's attendance" for a user in `America/Sao_Paulo` means `[2026-05-13T00:00:00-03:00, 2026-05-14T00:00:00-03:00)`, not `[2026-05-13T00:00:00Z, 2026-05-14T00:00:00Z)`.
- Always anchor the bucket to a specific IANA timezone (`America/Sao_Paulo`, `Europe/Paris`, etc.). Never use "server time" or "system time".

## Comparisons

- Compare two `Date`/`DateTime` instances directly. Never compare string representations.
- Never compare instances from different timezones without converting to the same zone first.

## What to avoid

- `new Date(string)` parsing without an explicit timezone — the result is implementation-defined for some formats.
- Storing offsets (e.g. `-03:00`) instead of named zones — offsets don't survive DST changes.
- Manipulating dates by adding/subtracting milliseconds for human-meaningful intervals like "one day" or "one month" (DST + variable month lengths break this). Use a dedicated date library.
```

## Step 4 — Recommend follow-ups

After writing, tell the user:

- Run `/codex-workflow:codex-init-workspace` if the project doesn't have a CLAUDE.md tree yet — the root CLAUDE.md should reference `.agent/rules/`.
- Customize each rule to the project's actual conventions. The templates are opinionated defaults — feel free to delete sections that don't apply or add project-specific ones.
- As patterns emerge, anchor rules to canonical content in your AI Codex `Knowledge/` folder (use a `**Codex Anchors:**` header in the rule file pointing to the relevant Knowledge note).

## Notes

- Each rule file is **intentionally short**. Rules are operational, not encyclopedic. Long-form context belongs in the codex `Knowledge/`.
- Never overwrite an existing rule file without per-file explicit user approval.
- Project-specific rules (Flutter, Angular, Firebase, etc.) belong in `projects/<name>/.agent/rules/`, not at the root. This skill only seeds cross-cutting rules.
