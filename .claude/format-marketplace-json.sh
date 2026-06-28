#!/usr/bin/env bash
# PostToolUse: auto-formats marketplace.json with jq after edits.
input=$(cat)
f=$(echo "$input" | jq -r '.tool_input.file_path // ""' 2>/dev/null)
if [[ "$(basename "$f")" == "marketplace.json" ]] && command -v jq >/dev/null 2>&1; then
  tmp=$(mktemp)
  jq . "$f" > "$tmp" 2>/dev/null && mv "$tmp" "$f" || rm -f "$tmp"
fi
exit 0
