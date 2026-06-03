---
name: codex-research-ingest
description: Fetch an external web page as clean markdown with the Defuddle CLI and save it into the vault's Knowledge/ folder as a source-stamped reference note following the frontmatter convention. Use when the user wants to capture external docs, articles, or blog posts into the AI Codex, or asks to "ingest this URL into the vault" / "save this article to Knowledge".
disable-model-invocation: true
argument-hint: <url>
allowed-tools: Read Write Glob Bash(defuddle *) Bash(command -v *) Bash(date *)
---

# URL → source-stamped Knowledge note

Interactive walkthrough. Fetch, propose, confirm, write, validate. This composes the
`obsidian-skills` Defuddle capability (clean extraction) with the codex frontmatter
convention (a `type: reference` note) and the vault's Knowledge index — it does more than
fetch: it files the result so it's discoverable and provenance-stamped.

## Step 0 — Preconditions

```bash
command -v defuddle    # must resolve; if not: npm install -g defuddle
```

If Defuddle isn't installed, tell the user the one-line install and stop.

**Skip Defuddle for `.md` URLs** — those are already markdown; fetch them with `WebFetch`
directly (Defuddle is for cluttered HTML pages, not raw markdown).

## Step 1 — Resolve the URL and pull metadata

The URL is `$ARGUMENTS` (or ask). Extract title, domain, and the clean body:

```bash
defuddle parse "$ARGUMENTS" -p title
defuddle parse "$ARGUMENTS" -p domain
defuddle parse "$ARGUMENTS" --md          # the cleaned markdown body
```

If extraction is empty or errors (paywall, JS-only page, 404), report it and ask whether to
fall back to `WebFetch` or abort — don't write an empty note.

## Step 2 — Propose the note

Show the user, and confirm, before writing:

- **Filename** — a sanitized form of the title (Title_Case_With_Underscores), default path
  `<vault>/Knowledge/<Filename>.md`. Refuse to overwrite an existing note unless the user opts
  in.
- **Frontmatter** (the reference shape of the convention — no `status`, it's not a ticket):

  ```yaml
  ---
  type: reference
  source: <url>
  domain: <domain>
  retrieved: <today>          # date +%Y-%m-%d
  tags: [reference, research]
  ---
  ```

  Add topical tags / an `area` if the content clearly belongs to one (e.g. `area: flutter`).

## Step 3 — Write the note

Layout: frontmatter, then an H1 of the title, then a provenance callout, then the body.

```markdown
---
…frontmatter…
---

# <Title>

> [!info] Source
> Ingested from [<domain>](<url>) on <retrieved>. Cleaned with Defuddle — verify against the
> original before relying on specifics.

<defuddle markdown body>
```

The provenance callout matters: an ingested note is a *snapshot*, and readers (human or agent)
must be able to tell distilled-external content from first-party Knowledge.

## Step 4 — Validate

```bash
python3 -c "import io,yaml; t=io.open(PATH,encoding='utf-8').read(); assert t.startswith('---'); yaml.safe_load(t.split('---',2)[1]); print('frontmatter ok')"
```

Confirm the file wrote, frontmatter parses, and the body isn't truncated/empty.

## Step 5 — Recommend follow-ups

- Add a row to `Knowledge/Agent_Orientation.md`'s Knowledge Index pointing at the new note.
- Wikilink it from any related Knowledge/Feature notes so it joins the graph (and shows up in
  `codex-canvas-map`).
- For multi-page sources, ingest each page as its own note and link them.

## Notes

- This is distinct from the raw `obsidian:defuddle` skill (which just extracts to stdout/file):
  this one **files the result into the vault** with convention frontmatter, provenance, and an
  index entry.
- Always preserve the `source` URL and `retrieved` date — provenance is the whole point of a
  reference note.
- Quote the cleaned body faithfully; don't summarize during ingest. Summaries belong in a
  separate first-party Knowledge note that *links* to this reference.
