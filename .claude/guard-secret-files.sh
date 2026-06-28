#!/usr/bin/env bash
# PreToolUse: blocks reads/edits of secret .env files; allows .env.example and similar templates.
input=$(cat)
f=$(echo "$input" | jq -r '.tool_input.file_path // .tool_input.path // ""' 2>/dev/null)
b=$(basename "$f")
if [[ "$b" =~ ^\.env(\.[^.]+)?$ ]] && [[ ! "$b" =~ \.(example|sample|template|dist)$ ]] && [[ "$b" != "example.env" ]]; then
  echo "Blocked: $b matches secret env-file pattern" >&2
  exit 2
fi
