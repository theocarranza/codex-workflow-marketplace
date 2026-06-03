#!/usr/bin/env python3
"""Deterministic vault linter: audit an AI Codex vault against its archetype spec.

Usage:
  vault-lint.py <vault-path> [--type <archetype>] [--json]

Reads <vault>/.codex-vault.json for the archetype (or --type), loads the matching spec from
../archetypes/<type>.json, and reports STRUCTURAL issues across every existing note:
  - filename shape violations (vs the per-folder naming rules)
  - frontmatter: missing-required / forbidden-present keys
  - stray .md files in folders not declared by the spec
  - duplicate ticket ids (same leading number on multiple ticket files)

Semantic issues a script can't judge reliably (mixed languages, near-duplicate prose) are left
to the codex-vault-lint skill, which layers human/agent judgment on top of this report.
"""
import sys, os, json, re

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def match_dir(glob, reldir):
    pref = glob[:-3] if glob.endswith("/**") else glob
    return reldir == pref or reldir.startswith(pref + "/")


def fm_keys(path):
    try:
        t = open(path, encoding="utf-8").read()
    except Exception:
        return None
    m = re.match(r"^﻿?---\s*\n(.*?)\n---\s*(\n|$)", t, re.S)
    if not m:
        return set()
    return {mm.group(1) for mm in (re.match(r"^([A-Za-z0-9_-]+)\s*:", ln) for ln in m.group(1).splitlines()) if mm}


def main():
    args = [a for a in sys.argv[1:]]
    as_json = "--json" in args
    args = [a for a in args if a != "--json"]
    vtype = None
    if "--type" in args:
        i = args.index("--type"); vtype = args[i + 1]; del args[i:i + 2]
    vault = os.path.abspath(args[0]) if args else os.getcwd()

    if not vtype:
        try:
            vtype = json.load(open(os.path.join(vault, ".codex-vault.json"))).get("type")
        except Exception:
            print("No .codex-vault.json marker found; pass --type <archetype>.", file=sys.stderr)
            sys.exit(2)
    spec_path = os.path.join(PLUGIN_ROOT, "archetypes", f"{vtype}.json")
    if not os.path.isfile(spec_path):
        print(f"Unknown archetype '{vtype}' (no {spec_path}).", file=sys.stderr)
        sys.exit(2)
    spec = json.load(open(spec_path))
    naming = spec.get("naming", {})
    exempt = naming.get("exempt", {})
    spec_dirs = {f["path"] for f in spec.get("folders", [])}

    findings = {"naming": [], "frontmatter": [], "stray": [], "duplicate_ticket": []}
    ticket_ids = {}

    for root, dirs, files in os.walk(vault):
        dirs[:] = [d for d in dirs if d not in (".obsidian", ".git", ".trash")]
        for fn in files:
            if not fn.lower().endswith(".md"):
                continue
            p = os.path.join(root, fn)
            rel = os.path.relpath(p, vault).replace(os.sep, "/")
            reldir = os.path.dirname(rel)
            top = rel.split("/", 1)[0] if "/" in rel else ""
            base = fn[:-3]
            if fn in exempt.get("basenames", []) or top in exempt.get("folders", []):
                continue

            # stray: in a dir not covered by any spec folder
            if reldir and reldir not in spec_dirs and not any(reldir.startswith(sd + "/") for sd in spec_dirs):
                findings["stray"].append(rel)

            # naming
            rule = next((r for r in naming.get("rules", []) if match_dir(r["match"], reldir)), naming.get("default"))
            if rule and not re.match(rule["filename"], base):
                findings["naming"].append({"file": rel, "expected": rule.get("style", ""), "example": rule.get("example", "")})

            # frontmatter
            fr = next((f for f in spec.get("frontmatter", []) if match_dir(f["match"], reldir)), None)
            if fr:
                keys = fm_keys(p) or set()
                miss = [k for k in fr.get("required", []) if k not in keys]
                forb = [k for k in fr.get("forbidden", []) if k in keys]
                if miss or forb:
                    findings["frontmatter"].append({"file": rel, "missing": miss, "forbidden": forb})

            # duplicate ticket id
            if reldir.startswith("Tickets"):
                mid = re.match(r"^(\d+)", base)
                if mid:
                    ticket_ids.setdefault(mid.group(1), []).append(rel)

    findings["duplicate_ticket"] = [{"id": k, "files": v} for k, v in ticket_ids.items() if len(v) > 1]

    total = sum(len(v) for v in findings.values())
    if as_json:
        print(json.dumps({"type": vtype, "vault": vault, "total": total, "findings": findings}, indent=2))
        return

    print(f"Vault lint — {vtype} — {vault}")
    print(f"  {total} finding(s)\n")
    for label, key in [("Filename violations", "naming"), ("Frontmatter issues", "frontmatter"),
                       ("Stray files (folder not in spec)", "stray"), ("Duplicate ticket ids", "duplicate_ticket")]:
        items = findings[key]
        print(f"## {label}: {len(items)}")
        for it in items:
            if key == "naming":
                print(f"  - {it['file']}\n      expected: {it['expected']} (e.g. {it['example']})")
            elif key == "frontmatter":
                bits = []
                if it["missing"]:
                    bits.append("missing " + ",".join(it["missing"]))
                if it["forbidden"]:
                    bits.append("forbidden " + ",".join(it["forbidden"]))
                print(f"  - {it['file']}: {'; '.join(bits)}")
            elif key == "duplicate_ticket":
                print(f"  - #{it['id']}: {', '.join(it['files'])}")
            else:
                print(f"  - {it}")
        print()


if __name__ == "__main__":
    main()
