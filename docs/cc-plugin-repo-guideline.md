# cc-plugins Plugin Repository Guideline

This document defines the standard structure and conventions for all plugin repositories
in the cc-plugins ecosystem. Every plugin repo — current and future — should follow this
layout so that the `cc-plugins` umbrella marketplace can reference them consistently.
Plugin repos are not standalone marketplaces — installation always goes through `cc-plugins`.

---

## Repository structure

```
repo-root/
├── .claude/
│   └── settings.json             # Claude Code permissions and env vars
├── .githooks/
│   └── pre-commit                # Secret scanning via gitleaks
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

- The repo is the **host** for the plugin directory referenced by the `cc-plugins` catalog.
  It does not expose a standalone marketplace — users install via `MichaelvanLaar/cc-plugins`.
- If a repo contains more than one plugin, add each as a sibling under `plugins/`:
  `plugins/<plugin-a>/`, `plugins/<plugin-b>/`, etc. Add each to `cc-plugins/marketplace.json`.

---

## Key files

### `plugins/<plugin-name>/.claude-plugin/plugin.json`

The plugin manifest. Consumed by the `cc-plugins` catalog when the plugin is installed.

```json
{
  "name": "<plugin-name>",
  "description": "<One-line description>",
  "author": {
    "name": "Michael van Laar"
  },
  "homepage": "https://github.com/MichaelvanLaar/<repo-name>",
  "repository": "https://github.com/MichaelvanLaar/<repo-name>",
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
      "Read(./.env.*)",
      "Read(./secrets/**)",
      "Bash(rm -rf:*)",
      "Bash(curl:*)",
      "Bash(wget:*)"
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
```

Activate it once after cloning: `chmod +x .githooks/pre-commit && git config core.hooksPath .githooks`

### `.gitignore`

```
.claude/settings.local.json
.claude/local.md
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

| File                                                 | Purpose                                    |
| ---------------------------------------------------- | ------------------------------------------ |
| `CLAUDE.md`                                          | Project instructions, loaded every message |
| `.claude/settings.json`                              | Permissions, hooks, environment variables  |
| `plugins/<plugin-name>/.claude-plugin/plugin.json`   | Plugin manifest                            |
| `plugins/<plugin-name>/skills/<skill-name>/SKILL.md` | Skill definition                           |

## Don't

- Don't commit secrets or credentials to git
- Don't use `--force` flags — fix the underlying issue instead

## Learnings

When the user corrects a mistake or points out a recurring issue, append a one-line
summary to `.claude/learnings.md`. Don't modify `CLAUDE.md` directly.
```

---

## How the `cc-plugins` catalog references this repo

The `cc-plugins/marketplace.json` references the plugin via `git-subdir`, pointing to
the `plugins/<plugin-name>/` subdirectory:

```json
{
  "name": "<plugin-name>",
  "source": {
    "source": "git-subdir",
    "url": "https://github.com/MichaelvanLaar/<repo-name>.git",
    "path": "plugins/<plugin-name>"
  },
  "description": "<One-line description>"
}
```

This means no files need to move when a new plugin repo is added to the catalog —
just add an entry to `cc-plugins/marketplace.json`.

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

- [ ] Create repo as `MichaelvanLaar/cc-<topic>` on GitHub
- [ ] Add standard directory structure (see above)
- [ ] Fill in `plugins/<plugin-name>/.claude-plugin/plugin.json`
- [ ] Add skills under `plugins/<plugin-name>/skills/<skill-name>/SKILL.md`
- [ ] Add `.claude/settings.json` with baseline permissions
- [ ] Add `.githooks/pre-commit` and activate: `chmod +x .githooks/pre-commit && git config core.hooksPath .githooks`
- [ ] Add `.gitignore`, `.claudeignore`, `CLAUDE.md`, `LICENSE`, `README.md`
- [ ] Add entry to `cc-plugins/.claude-plugin/marketplace.json`
