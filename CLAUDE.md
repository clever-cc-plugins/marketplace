# clever-cc-plugins marketplace

Umbrella marketplace catalog for Claude Code plugins — each plugin lives in its own repo and is referenced here via `git-subdir`.

## Key Config Files

| File                                       | Purpose                                                             |
| ------------------------------------------ | ------------------------------------------------------------------- |
| `.claude-plugin/marketplace.json`          | Umbrella marketplace catalog listing all plugins                    |
| `.claude/format-markdown.sh`               | PostToolUse hook: formats Markdown files with prettier after edits  |
| `.claude/format-marketplace-json.sh`       | PostToolUse hook: auto-formats marketplace.json with jq after edits |
| `.claude/guard-secret-files.sh`            | PreToolUse hook: blocks reads/edits/writes of secret .env files     |
| `.claude/settings.json`                    | Permissions, hooks, environment variables                           |
| `.claudeignore`                            | Paths excluded from Claude Code indexing                            |
| `.githooks/pre-commit`                     | Secret scanning (gitleaks) + CLAUDE.md table sync                   |
| `.github/workflows/claude-code-review.yml` | Automated Claude Code PR review on pull requests                    |
| `.github/workflows/claude.yml`             | Claude Code GitHub Actions agent triggered by @claude mentions      |
| `.gitignore`                               | Git ignore patterns                                                 |
| `CLAUDE.md`                                | Project instructions, loaded every message                          |
| `scripts/sync-config-table.sh`             | Keeps the CLAUDE.md Key Config Files table in sync on each commit   |

<!-- cc-config: key-config-excluded
docs/cc-plugin-repo-guideline.md — sync-config-table.sh v6 dropped the docs/ scan; row kept as a manual exclusion, file still referenced via @-import in References — 2026-07-31
-->
<!-- cc-config: last-optimize-run: 2026-07-31 20cea97 -->

## Commands

- Validate marketplace JSON: `jq . .claude-plugin/marketplace.json`
- Activate hooks (once per clone): `chmod +x .githooks/pre-commit && git config core.hooksPath .githooks`

## References

@docs/cc-plugin-repo-guideline.md **Read when:** adding a plugin to the catalog or setting up a plugin repo

## Conventions

- Plugin repos are named `cc-<topic>` (e.g., `cc-config`, `cc-content`)
- Each plugin entry in marketplace.json uses `"source": "git-subdir"` pointing to `plugins/<plugin-name>/` in the plugin's own repo
- Plugin manifests, skills, and settings live entirely in the plugin's own repo — nothing is duplicated here
- `scripts/sync-config-table.sh` auto-sorts the CLAUDE.md Key Config Files table on pre-commit; pre-populate descriptions before committing new files so the hook preserves them

## Don't

- Don't commit secrets or credentials to git
- Don't use `--force` flags — fix the underlying issue instead
- Don't copy plugin skill files into this repo — reference them via `git-subdir` instead

## Learnings

When the user corrects a mistake or points out a recurring issue, append a one-line
summary to `.claude/learnings.md`. Don't modify `CLAUDE.md` directly.

## Compact Instructions

When compacting, preserve: list of modified files, current test status, open TODOs, and key decisions made.
