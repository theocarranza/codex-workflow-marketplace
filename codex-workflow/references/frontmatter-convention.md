# Codex vault frontmatter convention

The convention the codex-workflow Bases tooling assumes. It is deliberately small:
**location encodes status; frontmatter encodes what location cannot.**

Skills that read or write vault notes (`codex-mine-bases`, `codex-init-vault`) follow
this. Bases (`*.base`) query against it.

## Core principle: one source of truth per fact

A fact lives in exactly one place.

- **Status is the folder.** A ticket under `Tickets/Active/` *is* active. Do not also
  write `status: active` in frontmatter — the two will drift, and the folder wins
  anyway (it's what you move a note between). Bases derive the status lane from the
  parent folder.
- **Identity and classification are frontmatter.** A ticket number, what kind of note
  it is, what area it touches — none of that is encoded by where the file sits, so it
  goes in frontmatter.

## Property schema

Every property is optional; fill what you know. Types/areas are project vocabularies —
keep them small and consistent so Bases can group cleanly.

| Property  | Type        | Example                          | Notes |
|-----------|-------------|----------------------------------|-------|
| `ticket`  | number/str  | `6196`                           | Tracker id. Omit for notes that aren't tickets. |
| `type`    | enum        | `feature`                        | `feature` \| `tech-debt` \| `bug` \| `task` (tickets); `knowledge` \| `orientation` \| `index` \| `reference` (other notes). |
| `area`    | string      | `terms-of-use`                   | Functional domain. Stable kebab-case vocabulary. |
| `stack`   | list        | `[flutter, cloud-functions]`     | Tech surfaces touched. |
| `tags`    | list        | `[ticket, terms]`                | Obsidian tags; keep `ticket`/`knowledge` etc. as the first tag. |
| `created` | date        | `2026-05-28`                     | `YYYY-MM-DD`. Authoring date, not file ctime. |

Example (a ticket note — note the absence of `status`):

```yaml
---
ticket: 6196
type: feature
area: terms-of-use
stack: [flutter, cloud-functions]
tags: [ticket, terms]
created: 2026-05-28
---
```

## Bases formula gotchas (tested)

The Bases formula language is **not** JavaScript. Two traps worth pre-empting because
each vault otherwise rediscovers them:

1. **No list index / `.last()` accessor.** Lists support `slice`, `join`, `reverse`,
   `filter`, `map`, `unique` — but there is no `[n]` indexing and no `.last()`.
   To get the status lane from the parent folder, **strip the prefix** rather than
   split-and-index:

   ```yaml
   # WRONG — "cannot find function last on type list"
   status: 'file.folder.split("/").last()'

   # RIGHT — single source of truth, renders cleanly
   status: 'file.folder.replace("Tickets/", "")'
   ```

   This assumes tickets sit exactly one level under `Tickets/`. For deeper trees,
   `file.folder.split("/", n)` (split has an optional limit) or `slice` are the tools.

2. **Duration is not a number.** Subtracting dates yields a Duration; access `.days`
   before applying `.round()` etc.: `'(now() - file.ctime).days'`.

## Obsidian normalizes `.base` files on open

Obsidian rewrites a `.base` the first time it loads it. Expect:

- **Comments are stripped.** Any `#` comment headers the skills emit vanish — they're
  authoring aids only, never load-bearing.
- **Flow style becomes block style.** `{ displayName: "#" }` and `[a, b]` are rewritten
  to multi-line block form.
- **`columnSize` is added** once you resize a column in the UI.

None of this changes behavior — the file stays valid and equivalent. Don't fight it: write
whatever's clearest, and let Obsidian canonicalize. Just don't rely on comments persisting.

## Why this matters for agents

With the schema in place, an agent answers "what's in flight?" by querying a Base
(`obsidian base:query`, when Obsidian is running) instead of reading every file under
`Tickets/`. The `markdown-allowlist` hook can keep denying raw `Read`/`Grep` on vault
markdown — the Base is a structured, allowlist-free channel that returns exactly the
properties above.
