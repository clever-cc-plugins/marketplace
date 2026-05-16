# cc-plugins

Umbrella marketplace catalog for Claude Code plugins — each plugin lives in its own repo and is referenced here via `git-subdir`.

## Key Config Files

| File | Purpose |
|------|---------|
| `.claudeignore` | Paths excluded from Claude Code indexing              |
| `.claude-plugin/marketplace.json` | Umbrella marketplace catalog listing all plugins      |
| `.claude/settings.json` | Permissions, hooks, environment variables             |
| `docs/cc-plugin-repo-guideline.md` | Conventions for all plugin repos in the ecosystem     |
| `.gitignore` | Git ignore patterns                                   |

## Commands

- Validate marketplace JSON: `jq . .claude-plugin/marketplace.json`
- Activate hooks (once per clone): `chmod +x .githooks/pre-commit && git config core.hooksPath .githooks`

## References

@docs/cc-plugin-repo-guideline.md **Read when:** adding a plugin to the catalog or setting up a plugin repo

## Conventions

- Plugin repos are named `cc-<topic>` (e.g., `cc-config`, `cc-content`)
- Each plugin entry in marketplace.json uses `"source": "git-subdir"` pointing to `plugins/<plugin-name>/` in the plugin's own repo
- Plugin manifests, skills, and settings live entirely in the plugin's own repo — nothing is duplicated here

## Don't

- Don't commit secrets or credentials to git
- Don't use `--force` flags — fix the underlying issue instead
- Don't copy plugin skill files into this repo — reference them via `git-subdir` instead

## Learnings

When the user corrects a mistake or points out a recurring issue, append a one-line
summary to `.claude/learnings.md`. Don't modify `CLAUDE.md` directly.

## Compact Instructions

When compacting, preserve: list of modified files, current test status, open TODOs, and key decisions made.
