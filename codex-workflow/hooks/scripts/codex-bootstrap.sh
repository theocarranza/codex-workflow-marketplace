#!/usr/bin/env bash
# SessionStart hook: inject Codex orientation as additionalContext.
#
# Config: $CLAUDE_PROJECT_DIR/.claude/codex-workflow.config.json
#   .codex.folder         — codex folder name (defaults to glob AI_Codex_*)
#   .codex.bootstrap[]    — relative paths to inject (defaults to
#                           README.md + Knowledge/Agent_Orientation.md)
#
# Behavior:
#   - If config exists, its values win.
#   - If no config and no AI_Codex_* folder found, the hook is a silent no-op.
#   - Missing individual files are noted inline rather than aborting.

set -euo pipefail

project_dir="${CLAUDE_PROJECT_DIR:-$PWD}"
config="$project_dir/.claude/codex-workflow.config.json"

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

if [[ -z "$codex_folder" ]] || [[ ! -d "$project_dir/$codex_folder" ]]; then
  exit 0
fi

files=()
if [[ -f "$config" ]]; then
  while IFS= read -r f; do
    [[ -n "$f" ]] && files+=("$f")
  done < <(jq -r '.codex.bootstrap[]? // empty' "$config")
fi
if [[ ${#files[@]} -eq 0 ]]; then
  files=("README.md" "Knowledge/Agent_Orientation.md")
fi

codex_root="$project_dir/$codex_folder"

# Only include files that actually exist; silently skip missing ones.
present_files=()
for f in "${files[@]}"; do
  [[ -f "$codex_root/$f" ]] && present_files+=("$f")
done

if [[ ${#present_files[@]} -eq 0 ]]; then
  exit 0
fi

context="$(
  printf '=== Codex bootstrap (auto-loaded via SessionStart hook) ===\n'
  printf 'Source: %s\n' "$codex_folder"
  for f in "${present_files[@]}"; do
    printf '\n--- %s/%s ---\n' "$codex_folder" "$f"
    cat -- "$codex_root/$f"
  done
)"

jq -n --arg ctx "$context" '{
  hookSpecificOutput: {
    hookEventName: "SessionStart",
    additionalContext: $ctx
  }
}'
