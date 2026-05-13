---
name: codex-mine-style
description: Mine an author's commits to draft a canonical-style-examples Knowledge note with file/line anchors and Agent Rules. Use when the user wants to capture their own (or a teammate's) idiomatic style in the AI Codex, or asks to "mine my commits for style examples" / "build a style guide from my authored code".
disable-model-invocation: true
allowed-tools: Read Write Glob Bash(git log *) Bash(git show *) Bash(git rev-parse *) Bash(git config *) Bash(rg *) Bash(wc *)
---

# Mine authored commits → canonical style examples

Interactive walkthrough. Discover, sample, draft, confirm, write.

## Step 1 — Gather inputs

Ask the user for these. Provide defaults; let the user override any.

- **Author identity (one or more emails).** Default: `git config user.email`. Multiple is common — someone might commit as personal + work emails.
- **Scope path.** Default: the repo root. Often narrowed (`projects/<one>`, `src/`).
- **File filter.** Default: all. Common narrowings: `*.dart`, `*.ts`, `*.tsx`, `*.py`.
- **Date range or commit count.** Default: last 12 months. The goal is "representative recent style", not a full archeological dig.
- **Stack label.** Default: inferred from the file filter (`Dart`, `TypeScript`, etc.). Used in the output filename.
- **Output destination.** Default: `<vault>/Knowledge/<Stack>_Functional_Style_Examples.md`. The skill assumes the codex vault has already been scaffolded (`codex-workflow:codex-init-vault`).

## Step 2 — Discover

Build the commit set:

```bash
git log \
  --author="<email-1>" --author="<email-2>" \
  --no-merges \
  --since="<date-range>" \
  --pretty=format:"%H%x09%ad%x09%s" --date=short \
  -- <scope-path>
```

Surface to the user:

- Total commit count.
- Top ~15 files touched (by number of times appearing in those commits) — these are your high-confidence sources of "this author's idiom".
- A handful of recent representative subjects (helps the user confirm they're looking at the right slice of history).

Optional second pass to focus on *refactor-heavy* commits (refactors expose style explicitly):

```bash
git log --author=<email> --no-merges --pretty=format:"%H %s" --grep="^refactor" -- <scope-path>
```

## Step 3 — Sample

Read the top high-frequency files in full (or the most recent representative versions of them). For each, look for *patterns the author returns to*. Examples of the kinds of patterns to look for — adapt to the actual code you find:

- **Type-level structure.** Sealed classes, discriminated unions, branded primitives, exhaustive `switch`/`match`, refined type guards.
- **Error handling.** `Either`/`Task`/`Option`, `fold` stacks, validation railways, `null`-at-seams.
- **Control flow.** Function composition vs. statement sequences, named predicates, comprehensions over loops, declarative reducers.
- **Boundaries.** Where impurity lives (gateway-then-fold, repository pattern, pure-shell/imperative-core).
- **Naming.** Verb vs. noun bias, what's allowed to be short, what must be long.

Pick **6–10 anchors** that together illustrate the idiom. Each anchor = one file + one line range (5–15 lines) + the pattern it exemplifies. Prefer anchors from different files; avoid stacking 4 examples from the same module.

## Step 4 — Draft

Propose the note structure to the user before writing. Default skeleton:

````markdown
---
date: <today>
type: knowledge
tags: [knowledge, style, <stack-lowercase>, functional]
---

# <Stack> Functional Style Examples

Annotated in-repo exemplars of <author or team>'s idiomatic <stack> style. Each example points at a real file + line range so the pattern stays anchored to live code, not paraphrased.

## How to use this note

- Treat these as *reference patterns*, not strict rules. The Agent Rules at the bottom distill the binding bits.
- When in doubt, read the anchor file in full — the surrounding code is part of the example.
- If an anchor's source has moved or changed substantially, flag it — the note is meant to track current code, not archived snapshots.

## Anchor 1 — <pattern name>

**Source:** `<relative/path/to/file.ext>:<start-line>-<end-line>`

```<lang>
<3–10 line excerpt that shows the pattern>
```

<2–4 sentences explaining what's idiomatic about this code: the choice the author made, what the alternative would have been, and why this is the preferred shape. Avoid abstract theory — point at the specific lines.>

## Anchor 2 — <pattern name>

*(same structure, repeated for each anchor)*

---

## Agent Rules

Distilled binding rules. Apply these when generating new code in <stack>.

1. **<Rule name>.** <One-sentence rule + when it applies + the anchor(s) it derives from.>
2. <…>

*(Aim for 6–10 rules. Each rule is one sentence + a parenthetical anchor reference.)*
````

Show the user the drafted note in chunks (anchor by anchor) so they can correct interpretations before the file is written.

## Step 5 — Write

Once the user approves:

- Confirm the output path (e.g. `<vault>/Knowledge/Dart_Functional_Style_Examples.md`).
- Refuse if the file exists, unless the user explicitly opts to overwrite (offer to write a `.draft.md` alongside instead).
- Write the file.

## Step 6 — Recommend follow-ups

After writing, tell the user:

- Add a row to `<vault>/Knowledge/Agent_Orientation.md` (Knowledge Index table) pointing to this note.
- Add a `**Codex Anchors:**` header in the relevant `.agent/rules/*.md` files (e.g. `rules-<stack>-style.md`) so rule consultations route to this canonical content.
- Consider running `/codex-workflow:codex-add-refactor-entry <commit-hash>` for each notable refactor commit to populate the Style Refactor Catalog with concrete before/after pairs.

## Notes

- This skill takes time. A 6–10 anchor note typically takes 20–40 minutes of interactive work. Don't try to one-shot it.
- Quality of the note is bounded by the quality of the commit history. If the author has a short history in the scope, surface that to the user and ask whether to broaden the scope before drafting.
- Quote real code, not paraphrased versions. If a snippet is too long, narrow the line range — don't summarize.
- Resist the urge to inflate the rules section. Six well-anchored rules beat fifteen abstract ones.
