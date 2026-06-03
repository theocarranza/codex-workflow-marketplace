---
name: codex-mine-bases
description: Backfill the frontmatter convention across an existing AI Codex vault and scaffold Obsidian Bases (.base) over its folders (Tickets, Features, Agent_Sessions). Use when a vault already has notes but no property schema or Base dashboards, or when the user asks to "add bases to the vault" / "turn the tickets folder into a board" / "backfill frontmatter".
disable-model-invocation: true
allowed-tools: Read Write Glob Bash(ls *) Bash(find *) Bash(head *) Bash(basename *) Bash(date *) Bash(python3 *)
---

# Backfill frontmatter + scaffold Bases over an existing vault

Interactive walkthrough. Inspect, propose, confirm, write. Existing files are never
overwritten without per-file approval.

This skill assumes the vault already exists (scaffolded by `codex-workflow:codex-init-vault`
or grown organically). It does two things, in order: (1) establish the property schema on
notes that lack it, then (2) lay Bases over the folders that now have a schema to query.

**Read the convention first:** `${CLAUDE_PLUGIN_ROOT}/references/frontmatter-convention.md`.
It defines the property schema and the Bases formula gotchas. Everything below follows it.

## Step 1 — Locate the vault and survey it

Find the codex folder (config `codex.folder`, else glob `AI_Codex*/`). Then survey the
collection folders the user wants dashboards over — default `Tickets/`, `Features/`,
`Agent_Sessions/`. For each, report:

- How notes are organized (flat files vs. status subfolders like `Active/Ready/Closed/Resolved`).
- How many notes already carry frontmatter vs. none (check whether the file starts with `---`).

Surface the split to the user — e.g. "Tickets: 18 notes across 4 status folders; 3 have
frontmatter, 15 don't." This is the adoption baseline.

## Step 2 — Confirm the schema vocabulary

The property schema is fixed (see the reference). What's project-specific is the **vocabulary**:
the set of `type`, `area`, and `stack` values in use. Propose a small starting vocabulary
inferred from the notes you surveyed and let the user correct it. Keep these lists short and
stable — they're what Bases group by.

Reaffirm the core rule with the user: **status stays encoded by folder; never written into
frontmatter.** If the user's folders don't encode status (everything is flat), ask whether to
(a) introduce status subfolders, or (b) make `status` a genuine frontmatter property because
there's nothing else to derive it from. Default to (a) — it matches the convention.

## Step 3 — Backfill frontmatter

For each note lacking frontmatter, derive the properties from what's knowable:

- `ticket` — from a leading number in the filename when present.
- `type` — inferred from filename/content (`tech-debt-*` → `tech-debt`, `Feature *` → `feature`),
  confirmed against the Step 2 vocabulary.
- `area`, `stack` — best-effort from content; leave blank rather than guess wildly.
- `created` — the note's authoring date if discernible, else its file ctime as a fallback.

Show the user the proposed frontmatter block for each note (or in batches, grouped by folder)
**before** writing. Prepend the block; do not touch existing body content. Skip — loudly — any
note that already starts with `---` rather than risk clobbering existing properties.

A safe prepend (never overwrites an existing frontmatter block):

```python
import io
with io.open(path, encoding="utf-8") as f:
    body = f.read()
if body.lstrip().startswith("---"):
    print("SKIP (already has frontmatter):", path)
else:
    with io.open(path, "w", encoding="utf-8") as f:
        f.write("---\n" + "\n".join(fm_lines) + "\n---\n\n" + body)
```

## Step 4 — Scaffold the Bases

Write one `.base` per collection folder, at the vault root so it shows in Obsidian's tree.
Each Base derives its status lane from the folder (per the convention) and surfaces a
**triage view** listing notes that still lack the schema — so adoption is self-tracking.

`Tickets.base` (the canonical example — adapt names for `Features.base`, `Agent_Sessions.base`):

```yaml
filters:
  and:
    - file.inFolder("Tickets")
    - 'file.ext == "md"'

formulas:
  # Parent folder minus the prefix = the status lane. NOT split().last() — see reference.
  status: 'file.folder.replace("Tickets/", "")'
  age_days: '(now() - file.ctime).days'
  has_meta: 'if(type, "✅", "⚠️ no frontmatter")'

properties:
  ticket: { displayName: "#" }
  formula.status: { displayName: Status }
  formula.age_days: { displayName: "Age (d)" }
  formula.has_meta: { displayName: Meta }

views:
  - type: table
    name: "Board"
    groupBy: { property: formula.status, direction: ASC }
    order: [file.name, ticket, type, area, tags, formula.age_days]

  - type: table
    name: "Needs metadata"
    filters:
      not: [type]
    order: [file.name, formula.status, file.mtime]
```

For folders without status subfolders (e.g. a flat `Features/`), drop the `status` formula and
group by `area` or `type` instead. For `Agent_Sessions/`, sort by `file.name` (the
`YYYY-MM-DD-HHMMSS-` prefix sorts chronologically) and surface `created` + a session summary.

**Validate every `.base` as YAML before declaring done** (`python3 -c "import yaml; yaml.safe_load(open(p))"`).
A `.base` that fails to parse renders blank in Obsidian.

## Step 5 — Optional: drop the convention into the vault

Offer to write `${vault}/Knowledge/Frontmatter_Convention.md` — a `type: reference` note copying
the schema from the bundled reference — so the convention is discoverable inside the vault, not
just in the plugin. Link it from `Agent_Orientation.md`'s Knowledge Index.

## Step 6 — Recommend follow-ups

- Open each `.base` in Obsidian to confirm it renders (a YAML error shows blank; a bad formula
  shows red text in the column — the most common cause is the `.last()` trap in the reference).
- Work the **Needs metadata** view down over time — it's the backlog of un-migrated notes.
- Re-run this skill after adding new collection folders, or extend `codex-init-vault` to emit
  Bases for new vaults from the start.

## Notes

- This is migration work on real notes. Go folder by folder, confirm before each write, and
  never overwrite a note that already has frontmatter.
- The vocabulary (`type`/`area`/`stack` values) is the load-bearing decision — a sprawling
  vocabulary makes Bases useless. Fewer, stabler values beat precise-but-unique ones.
- Bases are cheap to iterate: if a view isn't useful, edit the `.base` YAML and reopen. The
  expensive, careful part is the frontmatter backfill — get the schema right first.
