---
name: codex-query-vault
description: Query the AI Codex vault live via the Obsidian CLI — list and query Bases (open tickets, features by area, recent sessions), full-text search, and backlinks — instead of raw file reads. Use when you need current vault state ("what tickets are open?", "what do we know about X?", "which sessions touched Y?", "what links to this note?") and Obsidian is running with the vault open. Read-only.
allowed-tools: Bash(obsidian *)
---

# Query the AI Codex vault (live, via the Obsidian CLI)

Read-only. This is the **sanctioned channel** for reading vault state: the `markdown-allowlist`
hook denies raw `Read`/`Grep` on vault markdown, so reach for the `obsidian` CLI instead. It
returns structured rows from Bases and is far cheaper than reading whole notes.

## Step 0 — Precondition: is the CLI live?

The CLI requires the **Obsidian app running with the target vault open**. Check first and
**degrade gracefully** — never hard-fail a task because the vault is closed.

```bash
obsidian vault    # prints the active vault name + path, or errors if nothing is reachable
```

If it errors or returns nothing:
- Tell the user the vault query channel is unavailable (open Obsidian to enable it), and
- Fall back to allowlist-permitted reads (`CLAUDE.md`, `.agent/**`) or proceed without the
  vault context — don't block.

## Step 1 — Discover what's queryable

```bash
obsidian bases    # lists the .base files (e.g. Tickets.base, Features.base, Agent_Sessions.base)
```

## Step 2 — Query patterns

Bases resolve by **`path=`** (e.g. `Tickets.base`), **not `file=`**. Use `format=json` to
parse, `format=md` to show the user a table. (`base:views` is unreliable — it tends to return
the *active* base's views; pass a `view=` name you already know from the `.base` file.)

**Open tickets** — query the board, then filter by the `path` lane (Board's JSON rows carry
`path`/`ticket`/`type`/`area`/`tags` but no `status` column; status lives in the folder, so
read it off `path`):

```bash
obsidian base:query path="Tickets.base" view="Board" format=json
# "open" = rows whose path contains /Active/ or /Ready/ ; "done" = /Closed/ or /Resolved/
```

**Features by area:**

```bash
obsidian base:query path="Features.base" view="By area" format=json
```

**Recent sessions** (filename prefix `YYYY-MM-DD-HHMMSS-` sorts chronologically):

```bash
obsidian base:query path="Agent_Sessions.base" view="Sessions" format=json
```

**Full-text search** — "what do we know about X?":

```bash
obsidian search query="terms versioning" format=tsv          # files that match
obsidian search query="terms versioning" path="Knowledge" limit=10
obsidian search:context query="idempotency"                  # matches with line context
```

**Relationships** — what references a note:

```bash
obsidian backlinks path="Knowledge/Domain_Legal.md" format=tsv
```

## Step 3 — Answer, then cite

Synthesize the rows into the answer the task needs (e.g. "3 tickets open: 2 Active, 1 Ready").
When you point at a note, cite it by vault path so the user can open it. If you then need a
specific note's *full body*, that's the moment to read the file directly (the vault folder is
allowlisted for the agent; raw greps across it are not — that's what this skill replaces).

## Notes

- **Read-only, so this skill allows model invocation** (unlike the side-effecting `codex-*`
  skills). Reach for it whenever you need vault state instead of guessing or bulk-reading.
- Prefer one `base:query` over reading every note in a folder — it's the whole point.
- All commands are safe to retry; none mutate the vault.
- If a `view=` name is wrong, `base:query` errors clearly — list the `.base` file's views by
  reading the `.base` file (it's YAML, not blocked by the markdown allowlist) and retry.
- **`base:query` returns only a view's `order` columns, not its `groupBy` property.** If a
  grouped column comes back blank (e.g. `area` in a "By area" view), the data is fine — the
  Base just doesn't list that property in `order`. Read the `.base` YAML to confirm, and prefer
  views whose `order` includes everything you need.
