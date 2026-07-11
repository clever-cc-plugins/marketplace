# clever-cc-plugins Plugin Repository Guideline

This document defines the standard structure and conventions for all plugin repositories
in the clever-cc-plugins ecosystem. Every plugin repo — current and future — should follow this
layout so that the `clever-cc-plugins` umbrella marketplace can reference them consistently.
Plugin repos are not standalone marketplaces — installation always goes through `clever-cc-plugins`.

---

## Repository structure

```
repo-root/
├── .claude/
│   ├── settings.json             # Claude Code permissions, hooks, env vars
│   ├── guard-secret-files.sh     # PreToolUse hook: blocks reads/edits/writes of secret .env files
│   └── format-markdown.sh        # PostToolUse hook: formats .md files with prettier
├── .githooks/
│   └── pre-commit                # Secret scanning (gitleaks) + CLAUDE.md table sync
├── scripts/
│   └── sync-config-table.sh      # Keeps CLAUDE.md's Key Config Files table in sync on each commit
├── plugins/
│   └── <plugin-name>/
│       ├── .claude-plugin/
│       │   └── plugin.json       # Plugin manifest
│       └── skills/
│           └── <skill-name>/
│               └── SKILL.md      # Skill definition
├── .claudeignore                 # Paths excluded from Claude Code indexing
├── .gitignore
├── CLAUDE.md                     # Project instructions for Claude Code
├── LICENSE
└── README.md
```

### Notes

- The repo is the **host** for the plugin directory referenced by the `clever-cc-plugins` catalog.
  It does not expose a standalone marketplace — users install via `clever-cc-plugins/marketplace`.
- If a repo contains more than one plugin, add each as a sibling under `plugins/`:
  `plugins/<plugin-a>/`, `plugins/<plugin-b>/`, etc. Add each to `marketplace/.claude-plugin/marketplace.json`.

---

## Key files

### `plugins/<plugin-name>/.claude-plugin/plugin.json`

The plugin manifest. Consumed by the `clever-cc-plugins` catalog when the plugin is installed.

```json
{
  "name": "<plugin-name>",
  "description": "<One-line description>",
  "author": {
    "name": "Michael van Laar"
  },
  "homepage": "https://github.com/clever-cc-plugins/<repo-name>",
  "repository": "https://github.com/clever-cc-plugins/<repo-name>",
  "license": "MIT"
}
```

### `plugins/<plugin-name>/skills/<skill-name>/SKILL.md`

The skill definition file. The frontmatter `description` field is what Claude Code
displays and uses to match the skill to user requests.

```markdown
---
name: <skill-name>
description: <When to trigger this skill — written from Claude's perspective>
---

<Skill content>
```

### `.claude/settings.json`

Standard baseline permissions. Extend as needed for the plugin's specific requirements.

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": ["Bash(git *)", "Bash(chmod +x *)"],
    "deny": [
      "Read(./.env)",
      "Read(./.env.local)",
      "Read(./.env.*.local)",
      "Read(./.env.development)",
      "Read(./.env.production)",
      "Read(./.env.staging)",
      "Read(./.env.test)",
      "Read(./secrets/**)",
      "Bash(rm -rf:*)",
      "Bash(curl:*)",
      "Bash(wget:*)"
    ]
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Read|Edit|Write",
        "hooks": [
          { "type": "command", "command": "bash .claude/guard-secret-files.sh" }
        ]
      }
    ]
  },
  "env": {
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "50",
    "MAX_THINKING_TOKENS": "10000",
    "CLAUDE_CODE_MAX_OUTPUT_TOKENS": "16000",
    "CLAUDE_CODE_SUBAGENT_MODEL": "haiku"
  }
}
```

Note: `Read(./.env.*)` (a broad glob) also matches `.env.example`/`.env.sample`/etc. and blocks
Claude from reading legitimate template files. Use the enumerated list above instead — it covers
real secret-bearing variants without catching examples.

### `.claude/guard-secret-files.sh`

Defense-in-depth PreToolUse hook: `permissions.deny` only covers the enumerated `.env` names above,
so this hook catches any other `.env.*` variant (e.g. `.env.foo`) across Read, Edit, and Write.
It must exit with code **2** to actually block the call — any other non-zero exit code is treated
as a non-fatal hook error and the tool call proceeds anyway.

```bash
#!/usr/bin/env bash
# PreToolUse: blocks reads/edits/writes of secret .env files; allows .env.example and similar templates.
input=$(cat)
f=$(echo "$input" | jq -r '.tool_input.file_path // .tool_input.path // ""' 2>/dev/null)
b=$(basename "$f")
case "$b" in
  *.example|*.sample|*.template|*.dist|example.env|sample.env) exit 0 ;;
esac
case "$b" in
  .env|.env.*)
    echo "Blocked: $b matches secret env-file pattern" >&2
    exit 2
    ;;
esac
exit 0
```

### `.githooks/pre-commit`

Secret scanning hook. Blocks commits if secrets are detected. Requires
[gitleaks](https://github.com/gitleaks/gitleaks).

```bash
#!/usr/bin/env bash
if command -v gitleaks &> /dev/null; then
  gitleaks git --pre-commit --staged || exit 1
else
  echo "Warning: gitleaks not installed — secret scanning skipped."
  echo "Install: brew install gitleaks (macOS) or https://github.com/gitleaks/gitleaks"
fi

# Keep CLAUDE.md config file table in sync
bash scripts/sync-config-table.sh
```

Activate it once after cloning: `chmod +x .githooks/pre-commit && git config core.hooksPath .githooks`

### `scripts/sync-config-table.sh`

Keeps the CLAUDE.md "Key Config Files" table in sync with the filesystem: adds rows for new
config files, removes rows for deleted ones, and preserves hand-written descriptions for existing
rows. Invoked automatically by `.githooks/pre-commit`. Copy the version from an existing repo
(e.g. `cc-chime/scripts/sync-config-table.sh`) and adjust the scanned directories if this repo's
layout differs (e.g. add a `.claude/context/` or `docs/` section).

### `.gitignore`

```
.claude/settings.local.json
.claude/local.md

# Headroom — machine-local session cache and learnings
.headroom/

# MCP tool-local caches
.codegraph/
.serena/
.tokensave/
```

### `.claudeignore`

Start empty with a comment. Add entries as the project grows:

```
# Paths excluded from Claude Code indexing (add entries here as the project grows)
```

### `CLAUDE.md`

Project-level instructions for Claude Code. Keep it concise. Minimal recommended content:

```markdown
# <repo-name>

<One-line description of what this plugin does.>

## Key Config Files

| File                                                 | Purpose                                                            |
| ---------------------------------------------------- | ------------------------------------------------------------------ |
| `CLAUDE.md`                                          | Project instructions, loaded every message                         |
| `.claude/settings.json`                              | Permissions, hooks, environment variables                          |
| `.claude/guard-secret-files.sh`                      | PreToolUse hook: blocks reads/edits/writes of secret .env files    |
| `.claude/format-markdown.sh`                         | PostToolUse hook: formats Markdown files with prettier after edits |
| `.githooks/pre-commit`                               | Secret scanning (gitleaks) + CLAUDE.md table sync                  |
| `scripts/sync-config-table.sh`                       | Keeps Key Config Files table in sync on each commit                |
| `plugins/<plugin-name>/.claude-plugin/plugin.json`   | Plugin manifest                                                    |
| `plugins/<plugin-name>/skills/<skill-name>/SKILL.md` | Skill definition                                                   |

## Don't

- Don't commit secrets or credentials to git
- Don't use `--force` flags — fix the underlying issue instead

## Learnings

When the user corrects a mistake or points out a recurring issue, append a one-line
summary to `.claude/learnings.md`. Don't modify `CLAUDE.md` directly.
```

---

## How the `clever-cc-plugins` catalog references this repo

The marketplace repo's `marketplace.json` references the plugin via `git-subdir`, pointing to
the `plugins/<plugin-name>/` subdirectory:

```json
{
  "name": "<plugin-name>",
  "source": {
    "source": "git-subdir",
    "url": "https://github.com/clever-cc-plugins/<repo-name>.git",
    "path": "plugins/<plugin-name>"
  },
  "description": "<One-line description>"
}
```

This means no files need to move when a new plugin repo is added to the catalog —
just add an entry to the marketplace repo's `marketplace.json`.

---

## Naming conventions

| Thing                       | Convention              | Example                   |
| --------------------------- | ----------------------- | ------------------------- |
| Repository name             | `cc-<topic>`            | `cc-config`, `cc-content` |
| Plugin name (in manifests)  | same as repo name       | `cc-config`               |
| Skill directory name        | kebab-case, descriptive | `cc-config-init`          |
| Skill `name` in frontmatter | same as directory name  | `cc-config-init`          |

---

## Checklist for a new plugin repo

- [ ] Create repo as `clever-cc-plugins/cc-<topic>` on GitHub
- [ ] Add standard directory structure (see above)
- [ ] Fill in `plugins/<plugin-name>/.claude-plugin/plugin.json`
- [ ] Add skills under `plugins/<plugin-name>/skills/<skill-name>/SKILL.md`
- [ ] Add `.claude/settings.json` with baseline permissions and the PreToolUse guard hook
- [ ] Add `.claude/guard-secret-files.sh` and `.claude/format-markdown.sh`
- [ ] Add `scripts/sync-config-table.sh` and wire it into `.githooks/pre-commit`
- [ ] Add `.githooks/pre-commit` and activate: `chmod +x .githooks/pre-commit && git config core.hooksPath .githooks`
- [ ] Add `.gitignore`, `.claudeignore`, `CLAUDE.md`, `LICENSE`, `README.md`
- [ ] Add entry to the marketplace repo's `.claude-plugin/marketplace.json`
