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
| `.githooks/pre-commit`                     | Secret scanning (gitleaks) + CLAUDE.md table sync                   |
| `.github/workflows/claude-code-review.yml` | Automated Claude Code PR review on pull requests                    |
| `.github/workflows/claude.yml`             | Claude Code GitHub Actions agent triggered by @claude mentions      |
| `.github/workflows/doc-sync.yml`           | Runs the doc drift check on README/catalog PRs and weekly           |
| `.gitignore`                               | Git ignore patterns                                                 |
| `CLAUDE.md`                                | Project instructions, loaded every message                          |
| `scripts/sync-config-table.sh`             | Keeps the CLAUDE.md Key Config Files table in sync on each commit   |

<!-- cc-config: key-config-excluded
docs/cc-plugin-repo-guideline.md — sync-config-table.sh doesn't scan docs/; documented under References instead — 2026-11-05
-->
<!-- cc-config: last-optimize-run: 2026-11-05 ca018c9 -->

## Commands

- Validate marketplace JSON: `jq . .claude-plugin/marketplace.json`
- Check docs across the plugin family: `python3 scripts/check-doc-sync.py` (add `--root <dir with all clones>` to use local repos)
- Test the drift check: `python3 -m unittest discover -s tests -v`
- Activate hooks (once per clone): `chmod +x .githooks/pre-commit && git config core.hooksPath .githooks`

## References

`docs/cc-plugin-repo-guideline.md` — read it (not auto-loaded) when: adding a plugin to the catalog or setting up a plugin repo

## Conventions

- Plugin repos are named `cc-<topic>` (e.g., `cc-config`, `cc-content`)
- Each plugin entry in marketplace.json uses `"source": "git-subdir"` pointing to `plugins/<plugin-name>/` in the plugin's own repo
- Plugin manifests, skills, and settings live entirely in the plugin's own repo — nothing is duplicated here
- When a plugin gains or loses a skill, or a plugin is added, run `scripts/check-doc-sync.py` and fix every README it names (this one, the org profile in `.github/profile/README.md`, the plugin's own)
- learnings-protocol.md must stay identical in every plugin repo; check-doc-sync.py reports a missing or differing copy
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
