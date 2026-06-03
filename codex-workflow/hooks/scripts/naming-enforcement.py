#!/usr/bin/env python3
"""PreToolUse(Write) hook: structural naming + frontmatter enforcement for AI Codex vaults.

Activates only when the target .md file lives inside a vault that declares its archetype
via a .codex-vault.json marker (written by codex-init-vault). Outside such a vault it is a
silent no-op (fail-open), so it never blocks ordinary code/file writes.

It enforces only what regex/sets can decide — filename SHAPE and required/forbidden
frontmatter keys — per the active archetype spec in ../archetypes/<type>.json. Semantic
issues (language, near-duplicates, stray files) are the linter's job, not this hook's.

Disable per project via .claude/codex-workflow.config.json -> {"namingEnforcement":{"enabled":false}}.
"""
import sys, os, json, re


def allow():
    sys.exit(0)


def deny(reason):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}))
    sys.exit(0)


def match_dir(glob, reldir):
    pref = glob[:-3] if glob.endswith("/**") else glob
    return reldir == pref or reldir.startswith(pref + "/")


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        allow()

    if data.get("tool_name") != "Write":
        allow()
    fp = (data.get("tool_input") or {}).get("file_path", "")
    if not fp:
        allow()
    fp_abs = os.path.abspath(fp)
    if not fp_abs.lower().endswith(".md"):
        allow()

    # Find the vault root: walk up for the marker.
    d = os.path.dirname(fp_abs)
    vault = None
    while True:
        if os.path.isfile(os.path.join(d, ".codex-vault.json")):
            vault = d
            break
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    if not vault:
        allow()  # not inside a marked vault -> fail-open

    # Optional per-project disable.
    proj = os.environ.get("CLAUDE_PROJECT_DIR", "")
    cfg = os.path.join(proj, ".claude", "codex-workflow.config.json") if proj else ""
    if cfg and os.path.isfile(cfg):
        try:
            c = json.load(open(cfg))
            if c.get("namingEnforcement", {}).get("enabled", True) is False:
                allow()
        except Exception:
            pass

    try:
        vtype = json.load(open(os.path.join(vault, ".codex-vault.json"))).get("type", "")
    except Exception:
        allow()
    plugin_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    spec_path = os.path.join(plugin_root, "archetypes", f"{vtype}.json")
    if not os.path.isfile(spec_path):
        allow()  # unknown archetype -> fail-open
    spec = json.load(open(spec_path))

    rel = os.path.relpath(fp_abs, vault).replace(os.sep, "/")
    reldir = os.path.dirname(rel)
    base = os.path.basename(rel)[:-3]  # strip .md
    top = rel.split("/", 1)[0] if "/" in rel else ""

    naming = spec.get("naming", {})
    exempt = naming.get("exempt", {})
    if os.path.basename(rel) in exempt.get("basenames", []):
        allow()
    if top in exempt.get("folders", []):
        allow()

    # Filename shape: first rule whose match-glob covers reldir, else default.
    rule = None
    for r in naming.get("rules", []):
        if match_dir(r["match"], reldir):
            rule = r
            break
    if rule is None:
        rule = naming.get("default")
    if rule and not re.match(rule["filename"], base):
        deny(
            f"codex-workflow naming ({vtype}): '{base}.md' does not match the convention for "
            f"{(reldir + '/') if reldir else 'the vault root'} — expected {rule.get('style','')} "
            f"(e.g. {rule.get('example','')}). Rename to match, or see archetypes/{vtype}.json."
        )

    # Frontmatter keys: parse the leading --- block of the content being written.
    fm_keys = set()
    content = (data.get("tool_input") or {}).get("content", "")
    m = re.match(r"^﻿?---\s*\n(.*?)\n---\s*(\n|$)", content, re.S)
    if m:
        for line in m.group(1).splitlines():
            mm = re.match(r"^([A-Za-z0-9_-]+)\s*:", line)
            if mm:
                fm_keys.add(mm.group(1))

    fmrule = None
    for fr in spec.get("frontmatter", []):
        if match_dir(fr["match"], reldir):
            fmrule = fr
            break
    if fmrule:
        missing = [k for k in fmrule.get("required", []) if k not in fm_keys]
        forbidden = [k for k in fmrule.get("forbidden", []) if k in fm_keys]
        if missing or forbidden:
            parts = []
            if missing:
                parts.append("missing required key(s): " + ", ".join(missing))
            if forbidden:
                parts.append("forbidden key(s) present: " + ", ".join(forbidden))
            deny(
                f"codex-workflow frontmatter ({vtype}, {(reldir + '/') if reldir else 'root'}): "
                + "; ".join(parts)
                + f". required={fmrule.get('required', [])}, forbidden={fmrule.get('forbidden', [])}."
            )

    allow()


if __name__ == "__main__":
    main()
