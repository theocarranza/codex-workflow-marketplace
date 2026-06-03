---
name: codex-canvas-map
description: Generate an Obsidian Canvas (.canvas) relationship map for a hub note — the note in the center, its outgoing links to one side and its backlinks to the other, wired with edges — saved into the vault's Architecture/ folder. Uses the Obsidian CLI to read the link graph. Use when the user wants a visual map of how a note connects to the rest of the vault, an architecture/dependency diagram, or asks to "make a canvas for X" / "map what links to X".
disable-model-invocation: true
argument-hint: <hub-note-name>
allowed-tools: Read Write Glob Bash(obsidian *) Bash(python3 *)
---

# Hub note → relationship Canvas

Interactive walkthrough. Gather the link graph, propose the layout, confirm, write, validate.
Composes the `codex-query-vault` channel (the Obsidian CLI) with the JSON Canvas format.

## Step 0 — Precondition: is the CLI live?

The link graph comes from the Obsidian CLI, which needs the **app running with the vault open**.

```bash
obsidian vault     # active vault name + path, or error
```

If unavailable, tell the user to open Obsidian (the map can't be built from raw reads reliably)
and stop — don't fabricate a graph.

## Step 1 — Resolve the hub note

The hub note name is passed as `$ARGUMENTS` (or ask). Resolve and sanity-check it exists:

```bash
obsidian backlinks file="$ARGUMENTS" format=tsv     # files that link TO the hub
obsidian links     file="$ARGUMENTS" format=tsv     # files the hub links OUT to
```

Report the counts ("12 backlinks, 3 outgoing") so the user sees the map's size before you draw
it. If a hub has dozens of links, offer to cap each side (e.g. top 15) or scope to a folder.

## Step 2 — Propose the layout

Three columns, hub centered:

```
   backlinks            HUB              outgoing links
  (x = -700)          (x = 0)              (x = +700)
   [note] ──arrow──▶ [ HUB ] ──arrow──▶ [note]
   [note] ──────────▶       ─────────▶ [note]
```

- Each related note is a **file node** (`type: "file"`, `file: "<vault-relative path>"`).
- Stack each column vertically; ~180px node height + ~60px gap. Center the hub vertically
  against the taller column.
- Edges: `backlink → hub` and `hub → outgoing`, `toEnd: "arrow"`. Optionally color the two
  sides differently (`color` "4"/"5") so direction reads at a glance.

Confirm the hub, the per-side counts/caps, and the output path before writing.

## Step 3 — Write the canvas

Default path: `<vault>/Architecture/<HubName> Map.canvas`. Refuse to overwrite an existing
canvas unless the user opts in (offer a `.draft.canvas` instead).

A `.canvas` is JSON: `{"nodes": [...], "edges": [...]}`. Build it programmatically — generate a
unique 16-char hex `id` per node and edge, required fields `id/type/x/y/width/height`, file
nodes carry `file`, edges carry `fromNode`/`toNode`/`toEnd: "arrow"`. Generating with a small
`python3` script (one node per CLI line) is more reliable than hand-writing JSON. Use real `\n`
in any text nodes, never literal `\\n`.

## Step 4 — Validate

Non-negotiable, or Obsidian shows a broken/blank canvas:

```bash
python3 - <<'PY'
import json
c=json.load(open(PATH))
ids={n["id"] for n in c["nodes"]}
assert all(e["fromNode"] in ids and e["toNode"] in ids for e in c["edges"]), "dangling edge"
assert len(ids)==len(c["nodes"]), "duplicate node id"
print("canvas valid:", len(c["nodes"]), "nodes,", len(c["edges"]), "edges")
PY
```

Check: valid JSON, every `fromNode`/`toNode` resolves to a node, all ids unique, every `file`
path actually exists in the vault.

## Step 5 — Recommend follow-ups

- Open the canvas in Obsidian; drag to fine-tune (Obsidian persists positions).
- Link the canvas from the hub note or `Architecture/`'s index so it's discoverable.
- Re-run after the note's link graph changes — the canvas is a snapshot, not live.

## Notes

- File nodes use **vault-relative paths** (e.g. `Knowledge/Domain_Legal.md`), exactly as the
  CLI prints them.
- A canvas is a point-in-time snapshot; it doesn't auto-update when links change.
- Keep maps focused — one hub, capped sides. A 60-node hairball helps no one; for "everything
  by domain" use a Base, not a canvas.
