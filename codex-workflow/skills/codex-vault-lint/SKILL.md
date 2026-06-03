---
name: codex-vault-lint
description: Audit an AI Codex vault against its archetype spec and fix the drift — filename violations, frontmatter issues, stray files, duplicate/mixed-language notes — proposing renames and frontmatter fixes, then applying them (with backlink updates) on confirmation. Use when a vault has drifted, after adopting archetypes on an existing vault, or the user asks to "lint / normalize / clean up the vault".
disable-model-invocation: true
argument-hint: "[vault-path] [--type <archetype>]"
allowed-tools: Read Write Edit Glob Bash(python3 *) Bash(jq *) Bash(ls *) Bash(find *) Bash(grep *) Bash(git mv *) Bash(mv *) Bash(obsidian *) Bash(date *)
---

# Lint a vault against its archetype spec

Interactive walkthrough. Scan, judge, propose, confirm, fix, re-scan. The deterministic
structural scan is done by a bundled script; you add the semantic judgment a regex can't, then
apply fixes carefully (renames break wikilinks — you must repair them).

## Step 0 — Locate the vault and archetype

Find the vault (argument, or the codex folder via `AI_Codex*/`). Determine its archetype from
`<vault>/.codex-vault.json`; if there's no marker (a legacy vault), ask which `--type` to lint
against and offer to write the marker at the end so the enforcement hook activates going forward.

## Step 1 — Run the structural scan

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/vault-lint.py" "<vault>" [--type <archetype>] --json
```

This returns JSON `findings`: `naming` (filename shape), `frontmatter` (missing-required /
forbidden-present), `stray` (files in folders not in the spec), `duplicate_ticket` (same leading
id on multiple ticket files). Summarize the counts for the user.

## Step 2 — Add the semantic layer (what the script can't judge)

Inspect the file list and add findings a regex misses:

- **Non-English names/content** — e.g. Portuguese filenames; flag for translation + rename.
- **Near-duplicate notes** — the same concept in two files (often two languages), e.g.
  `5061-Descartar-Atendimento-sem-dados` vs `5061-Discard-Attendance-Without-Data`. Propose
  keeping one (the English one) and merging/removing the other.
- **Mangled names** — doubled or concatenated titles.
- **Stray subfolders** — folders the vault uses that the spec doesn't define; propose mapping
  them onto spec folders (e.g. `Architecture/Protocols/` → `Architecture/Patterns/`) or adding
  them to the spec if they're genuinely needed.

## Step 3 — Propose a fix plan

Group by fix type and, for each file, propose the concrete new state:

- **Rename** → the spec-compliant name. You generate it: transliterate to English if needed,
  then apply the target folder's style (e.g. `Domain_Legal.md` → `Domain Legal.md`;
  `606-Review-Discard-Attendance.md` → `606-review-discard-attendance.md`;
  `2026-05-18-general-session.md` → `2026-05-18-HHMMSS-general-session.md` — pick a time from
  the note's frontmatter/content or `000000`).
- **Frontmatter** → keys to add (`type: …`) or remove (`status`).
- **Duplicates** → which to keep, which to remove (deletion needs explicit per-file approval).

Show the plan and confirm — per file or per group. Never rename, edit, or delete without
confirmation.

## Step 4 — Apply (and repair links)

- Rename with **`git mv`** when the vault is in a git repo (preserves history), else `mv`.
- **Repair wikilinks after every rename** — Obsidian links resolve by basename, so a rename
  orphans `[[Old Name]]`. Find and update inbound references:

  ```bash
  obsidian backlinks file="<old basename>" format=tsv     # if Obsidian is running
  grep -rl "\[\[<old basename>" "<vault>" --include=*.md   # fallback
  ```

  Update each `[[Old Name]]` / `[[Old Name|alias]]` to the new basename.
- Fix frontmatter with `Edit` (add/remove keys). Apply the same safe-prepend pattern as
  `codex-mine-bases` when a note has no frontmatter block at all.

## Step 5 — Re-scan and confirm

Re-run the Step 1 scanner. Confirm findings dropped to zero (or only the items the user chose to
keep). If the vault had no marker, write it now so the `PreToolUse(Write)` hook enforces the
spec on all future writes:

```bash
jq -n --arg t "<archetype>" '{type:$t, specVersion:1}' > "<vault>/.codex-vault.json"
```

## Notes

- The scanner is **structural and deterministic**; your value-add is the **semantic** layer and
  generating good replacement names. Don't skip Step 2.
- **Renames are the dangerous part** — always repair backlinks, and prefer `git mv` so the diff
  is reviewable. Batch by folder and re-scan between batches on a large vault.
- This is the retrofit path for vaults that predate the archetype (like the original
  `AI_Codex_Aplicatudo`). For brand-new vaults, `codex-init-vault` + the hook keep things clean
  from the start, so the linter should mostly find nothing.
