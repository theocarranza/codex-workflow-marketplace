---
name: codex-add-refactor-entry
description: Given a commit hash, derive a before/after entry for the AI Codex Style Refactor Catalog with the principle applied. Use when the user wants to capture a notable refactor as a teaching example, or asks to "add this commit to the refactor catalog" / "log this refactor".
disable-model-invocation: true
argument-hint: <commit-hash>
allowed-tools: Read Write Edit Glob Bash(git show *) Bash(git rev-parse *) Bash(git log *)
---

# Commit hash → Style Refactor Catalog entry

Inspect a commit, derive a before/after entry, append to the catalog. Interactive: never overwrites or appends without confirmation.

## Step 1 — Resolve the commit

The commit hash is passed as `$ARGUMENTS`. Validate first:

```bash
git rev-parse --verify "$ARGUMENTS^{commit}"
```

If validation fails, ask the user for a valid hash and stop. Otherwise, capture:

- Full hash (`git rev-parse "$ARGUMENTS"`).
- Subject + date + author (`git log -1 --pretty=format:"%h %ad %an %s" --date=short "$ARGUMENTS"`).
- File list (`git show --stat --format= "$ARGUMENTS"`).

Show this summary to the user so they confirm they're pointing at the right commit.

## Step 2 — Inspect the diff

```bash
git show "$ARGUMENTS" --no-color
```

Read every file change. For each substantive transformation in the diff (a commit can contain more than one), identify:

- **What changed shape-wise.** "Staircase of locals → named functional decomposition". "`for` loop accumulating errors → validation railway with `Either`". "`fold((f) => f, (v) => v)` collapse → `flatMap`".
- **The principle being applied.** Why the new shape is better. One sentence, anchored to a property of the new code (composability, exhaustiveness, removal of nullability, etc.).
- **The minimal before/after snippets.** 3–10 lines each. Trim aggressively — leave just enough context for the transformation to make sense in isolation.

Skip purely mechanical changes (formatting, renames without semantic shift, dependency bumps). The catalog is for *style transformations*, not changelogs.

If the commit contains zero substantive transformations, tell the user and stop — don't manufacture an entry.

## Step 3 — Locate the catalog

Default path: `<vault>/Knowledge/Style_Refactor_Catalog.md`.

The vault is autodetected the same way the codex hooks do it: glob `AI_Codex*/` at the project root, or read `codex.folder` from `.claude/codex-workflow.config.json`. If multiple match or none match, ask the user.

If the catalog file doesn't exist, propose creating it with this header:

```markdown
---
date: <today>
type: knowledge
tags: [knowledge, style, refactor, catalog]
---

# Style Refactor Catalog

Before/after pairs from authored refactor commits, each annotated with the principle applied. Anchored to commit hashes so the transformation can be inspected in full when the snippet isn't enough.

---
```

## Step 4 — Draft the entry

Use this format:

```markdown
## <Short imperative title> (`<short-hash>`)

**Date:** <YYYY-MM-DD> · **Author:** <name> · **Subject:** <commit subject>

**Principle:** <one sentence — what property of the code improved and why.>

### Before

```<lang>
<3–10 line snippet>
```

### After

```<lang>
<3–10 line snippet>
```

**Notes:** <0–3 sentences. Why the after-shape is preferred. Edge cases where the before-shape is still acceptable, if any.>
```

For multi-transformation commits, repeat the **Before / After / Notes** triplet for each transformation under the same top-level commit heading. Don't split a commit across multiple entries.

Show the drafted entry to the user. Iterate on snippets and principle wording until they approve.

## Step 5 — Append

Once approved:

- Append the entry to the end of the catalog file.
- Add a `---` separator before the new entry if the file already had entries.
- Never re-order existing entries.

## Step 6 — Recommend follow-ups

After appending, tell the user:

- If the entry illustrates a pattern not yet covered in a `<Stack>_Functional_Style_Examples.md` Knowledge note, consider promoting it to an anchor there (or running `/codex-workflow:codex-mine-style` for a broader pass).
- If the catalog has crossed ~10–15 entries, consider organizing by stack or principle (sub-headings) — the linear list scales poorly past that.

## Notes

- One commit = one entry, even if multi-faceted. The commit hash is the join key.
- Snippets are quoted verbatim from the diff. Don't paraphrase; if a snippet would be too long, narrow the range.
- The Style Refactor Catalog is a *teaching* artifact, not a changelog. Entries earn their place by being instructive in isolation — if someone can't learn the principle from the before/after pair alone, the entry isn't ready.
