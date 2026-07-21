<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/clever-cc-plugins/.github/main/assets/logo-dark.svg" />
    <img src="https://raw.githubusercontent.com/clever-cc-plugins/.github/main/assets/logo.svg" width="220" alt="clever [cc] plugins" />
  </picture>
</p>

# clever-cc-plugins marketplace

Umbrella marketplace catalog for Claude Code plugins — a single `/plugin marketplace add` gives you access to all plugins maintained under this catalog.

## Installation

Open Claude Code in any project and add the marketplace:

```
# in any Claude Code project
$ /plugin marketplace add clever-cc-plugins/marketplace
✓ marketplace added · 5 plugins available
```

Then install any plugin from the catalog:

```
$ /plugin install cc-config@clever-cc-plugins
✓ cc-config installed

$ /plugin install cc-concept@clever-cc-plugins
✓ cc-concept installed

$ /plugin install cc-content@clever-cc-plugins
✓ cc-content installed

$ /plugin install cc-handoff@clever-cc-plugins
✓ cc-handoff installed

$ /plugin install cc-chime@clever-cc-plugins
✓ cc-chime installed
```

### Keeping plugins current

Auto-update is disabled by default for third-party marketplaces. To enable it:

1. Run `/plugin` in Claude Code
2. Go to the **Marketplaces** tab
3. Toggle auto-update for `clever-cc-plugins/marketplace`

Once enabled, plugins update automatically on startup when new versions are available.

### Uninstalling

To remove the marketplace and all plugins installed from it in one step:

```
/plugin marketplace remove clever-cc-plugins
```

To remove a single plugin while keeping the marketplace:

```
/plugin uninstall cc-config@clever-cc-plugins
```

## Available plugins

| Plugin                                                          | Skills                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | What it does                                                                                        |
| --------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| [`cc-config`](https://github.com/clever-cc-plugins/cc-config)   | `/cc-config-init`, `/cc-config-optimize`                                                                                                                                                                                                                                                                                                                                                                                                                                | Bootstrap and audit Claude Code configurations                                                      |
| [`cc-concept`](https://github.com/clever-cc-plugins/cc-concept) | `/cc-concept-onboarding`, `/cc-concept-audience`, `/cc-concept-positioning`, `/cc-concept-competitive-research`, `/cc-concept-seo-research`, `/cc-concept-campaign-concept`, `/cc-concept-channel-advisor`, `/cc-concept-content-strategy`, `/cc-concept-gtm`, `/cc-concept-orchestrator`, `/cc-concept-learnings-promotion`, `/cc-concept-marketing-advisor`, `/cc-concept-performance-review`                                                                         | Marketing-strategy skills: positioning, competitive analysis, go-to-market, and campaign concepting |
| [`cc-content`](https://github.com/clever-cc-plugins/cc-content) | `/cc-content-onboarding`, `/cc-content-promote`, `/cc-content-research-prompt`, `/cc-content-ideation`, `/cc-content-atomize`, `/cc-content-linkedin-post`, `/cc-content-blog-article`, `/cc-content-facebook-post`, `/cc-content-instagram-post`, `/cc-content-press-release`, `/cc-content-x-post`, `/cc-content-text`, `/cc-content-samples-curation`, `/cc-content-session-wrap`, `/cc-content-new-skill`, `/cc-content-humanize`, `/cc-content-performance-review` | Content creation skills for marketing projects                                                      |
| [`cc-handoff`](https://github.com/clever-cc-plugins/cc-handoff) | `/handoff`, `/handoff-install`                                                                                                                                                                                                                                                                                                                                                                                                                                          | Create and restore machine-transfer handoff summaries between sessions                              |
| [`cc-chime`](https://github.com/clever-cc-plugins/cc-chime)     | _(hook-based, no slash commands)_                                                                                                                                                                                                                                                                                                                                                                                                                                       | Plays an audio notification at the end of every Claude turn                                         |

See each plugin's repository for full usage documentation.

## How this works

Each plugin lives in its own repository and is referenced here via `git-subdir` in `.claude-plugin/marketplace.json`. When Claude Code installs a plugin from this marketplace, it fetches the `plugins/<name>/` subdirectory directly from the plugin's own repo — nothing is duplicated here.

Adding a new plugin to the catalog only requires a new entry in `.claude-plugin/marketplace.json`.

## License

[MIT](LICENSE)

---

<p align="center">
  Part of the <a href="https://github.com/clever-cc-plugins">clever-cc-plugins</a> family · <a href="https://github.com/clever-cc-plugins/cc-config">cc-config</a> · <a href="https://github.com/clever-cc-plugins/cc-concept">cc-concept</a> · <a href="https://github.com/clever-cc-plugins/cc-content">cc-content</a> · <a href="https://github.com/clever-cc-plugins/cc-handoff">cc-handoff</a> · <a href="https://github.com/clever-cc-plugins/cc-chime">cc-chime</a>
</p>
