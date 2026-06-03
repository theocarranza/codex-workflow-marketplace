# Vault archetypes

A **vault archetype** is a research-backed template for an AI Codex vault: its folder
structure, naming conventions, and per-folder frontmatter rules. `codex-init-vault --type
<archetype>` scaffolds one; the `PreToolUse(Write)` enforcement hook reads it to gate writes;
`codex-vault-lint` audits an existing vault against it.

## The four archetypes

| `type` | For | Method basis |
|---|---|---|
| `software-project` | Agile/XP codebases (the original codex shape, refined) | Project + knowledge-base hybrid; status-by-folder |
| `research` | Academic / research projects | Zettelkasten (Fleeting/Literature/Permanent) + PARA + MOCs |
| `personal-pkm` | General life/knowledge management | PARA (Projects/Areas/Resources/Archive) |
| `technical-docs` | Product/library/API documentation | Diátaxis (Tutorials/How-to/Reference/Explanation) |

Design principles drawn from the research (see `../docs/obsidian-leverage.md` → references):
flat over deep (≤3–4 levels), folders answer *where it belongs* while tags/properties answer
*what it's about*, English-only filenames, date/timestamp IDs for journal notes, and a `Meta/`
folder for plumbing.

## The marker file

`codex-init-vault` writes `.codex-vault.json` at the vault root:

```json
{ "type": "software-project", "specVersion": 1 }
```

This is how the hook and linter know **which** archetype applies to a given vault. No marker →
the hook is a silent no-op (fail-open) and the linter asks which archetype to check against.

## Spec schema (`<type>.json`)

```jsonc
{
  "type": "software-project",
  "title": "Software / Agile Project Vault",
  "description": "...",
  "folders": [
    { "path": "Knowledge", "purpose": "Permanent distilled knowledge notes + MOC" }
    // gitkeep'd on scaffold; "seed" notes (README etc.) handled by codex-init-vault
  ],
  "naming": {
    "language": "en",
    // ordered rules; FIRST whose `match` glob hits the file's vault-relative dir wins.
    // `filename` is a regex tested against the basename WITHOUT the .md extension.
    "rules": [
      { "match": "Agent_Sessions/**", "filename": "^\\d{4}-\\d{2}-\\d{2}-\\d{6}-[a-z0-9-]+$",
        "style": "YYYY-MM-DD-HHMMSS-kebab-slug", "example": "2026-06-02-143000-terms-spec-alignment" }
    ],
    "default": { "filename": "^[a-z0-9-]+$", "style": "kebab-case" }
  },
  "frontmatter": [
    // FIRST matching glob wins. required/forbidden are hard (hook-enforced);
    // optional is advisory (documents the convention, not gated).
    { "match": "Tickets/**", "required": ["type"],
      "optional": ["ticket","area","stack","tags","created"], "forbidden": ["status"] }
  ]
}
```

### Notes on enforcement scope

- The **hook** enforces only what regex/sets can decide: filename **shape** and
  **required/forbidden** frontmatter keys, and only inside a vault that declares its `type`.
  It cannot judge meaning (English vs. other languages, near-duplicate notes) — that's the
  linter's job.
- Patterns are intentionally **permissive** (catch egregious structural drift, avoid blocking
  legitimate writes). `status` is `forbidden` in ticket frontmatter because status is encoded
  by the folder lane — see `../references/frontmatter-convention.md`.
- `**` in `match` globs means "this folder and anything under it."
