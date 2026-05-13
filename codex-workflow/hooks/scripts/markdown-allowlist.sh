#!/usr/bin/env bash
# PreToolUse hook for Read|Grep: enforce a markdown allowlist scoped to
# the project tree.
#
# Config: $CLAUDE_PROJECT_DIR/.claude/codex-workflow.config.json
#   .codex.folder                 — codex folder (always allowed in full)
#   .markdownAllowlist.patterns[] — bash case-glob patterns (relative paths)
#
# Defaults when no config:
#   - CLAUDE.md, GEMINI.md at any level
#   - any *.md under .agent/ (recursive, root or per-project)
#   - the autodetected AI_Codex_* folder, in full
#
# Behavior:
#   - Only intervenes on *.md (case-insensitive) inside the project tree.
#   - Reads outside the project tree are unaffected.
#   - Non-Read/Grep tools pass through.
#   - Grep only triggers when its `path` parameter is a single explicit file.

set -euo pipefail

project_dir="${CLAUDE_PROJECT_DIR:-$PWD}"
config="$project_dir/.claude/codex-workflow.config.json"

input="$(cat)"
tool="$(jq -r '.tool_name // ""' <<<"$input")"

case "$tool" in
  Read) target="$(jq -r '.tool_input.file_path // ""' <<<"$input")" ;;
  Grep) target="$(jq -r '.tool_input.path // ""' <<<"$input")" ;;
  *)    exit 0 ;;
esac

[[ -z "$target" ]] && exit 0

abs="$(realpath -m -- "$target" 2>/dev/null || printf '%s' "$target")"

shopt -s nocasematch
if [[ "$abs" != *.md ]]; then
  shopt -u nocasematch
  exit 0
fi
shopt -u nocasematch

if [[ "$abs" != "$project_dir"/* ]]; then
  exit 0
fi

rel="${abs#"$project_dir"/}"

# Resolve codex folder (config wins; else autodetect)
codex_folder=""
if [[ -f "$config" ]]; then
  codex_folder="$(jq -r '.codex.folder // ""' "$config")"
fi
if [[ -z "$codex_folder" ]]; then
  for d in "$project_dir"/AI_Codex*/; do
    [[ -d "$d" ]] || continue
    codex_folder="$(basename "$d")"
    break
  done
fi
if [[ -n "$codex_folder" ]]; then
  case "$rel" in
    "$codex_folder"/*) exit 0 ;;
  esac
fi

# Resolve allowlist patterns
patterns=()
if [[ -f "$config" ]]; then
  while IFS= read -r p; do
    [[ -n "$p" ]] && patterns+=("$p")
  done < <(jq -r '.markdownAllowlist.patterns[]? // empty' "$config")
fi
if [[ ${#patterns[@]} -eq 0 ]]; then
  patterns=(
    "CLAUDE.md"
    "GEMINI.md"
    ".agent/*"
    "projects/*/CLAUDE.md"
    "projects/*/GEMINI.md"
    "projects/*/.agent/*"
  )
fi

allowed=0
for p in "${patterns[@]}"; do
  case "$rel" in
    $p) allowed=1; break ;;
  esac
done

if (( allowed )); then
  exit 0
fi

jq -n --arg p "$rel" --arg t "$tool" --arg cf "${codex_folder:-}" '{
  hookSpecificOutput: {
    hookEventName: "PreToolUse",
    permissionDecision: "deny",
    permissionDecisionReason: (
      "codex-workflow markdown allowlist blocks " + $t + " on " + $p + ". " +
      "Allowed: the codex folder (" + (if $cf == "" then "<none autodetected>" else $cf end) + ") in full, plus the configured patterns " +
      "(default: CLAUDE.md, GEMINI.md, .agent/**, projects/*/CLAUDE.md, projects/*/GEMINI.md, projects/*/.agent/**). " +
      "Extend via .claude/codex-workflow.config.json (markdownAllowlist.patterns)."
    )
  }
}'
