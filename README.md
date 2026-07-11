# clever-cc-plugins marketplace

Umbrella marketplace catalog for Claude Code plugins — a single `/plugin marketplace add` gives you access to all plugins maintained under this catalog.

## Installation

Open Claude Code in any project and add the marketplace:

```
/plugin marketplace add clever-cc-plugins/marketplace
```

Then install any plugin from the catalog:

```
/plugin install cc-config@clever-cc-plugins
/plugin install cc-content@clever-cc-plugins
/plugin install cc-chime@clever-cc-plugins
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

| Plugin                                                          | Skills                                                                                                                                                                                            | What it does                                                |
| --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| [`cc-config`](https://github.com/clever-cc-plugins/cc-config)   | `/cc-config-init`, `/cc-config-optimize`                                                                                                                                                          | Bootstrap and audit Claude Code configurations              |
| [`cc-content`](https://github.com/clever-cc-plugins/cc-content) | `/cc-content:cc-content-onboarding`, `/cc-content:cc-content-linkedin-post`, `/cc-content:cc-content-samples-curation`, `/cc-content:cc-content-session-wrap`, `/cc-content:cc-content-new-skill` | Content creation skills for marketing projects              |
| [`cc-chime`](https://github.com/clever-cc-plugins/cc-chime)     | _(hook-based, no slash commands)_                                                                                                                                                                 | Plays an audio notification at the end of every Claude turn |

See each plugin's repository for full usage documentation.

## How this works

Each plugin lives in its own repository and is referenced here via `git-subdir` in `.claude-plugin/marketplace.json`. When Claude Code installs a plugin from this marketplace, it fetches the `plugins/<name>/` subdirectory directly from the plugin's own repo — nothing is duplicated here.

Adding a new plugin to the catalog only requires a new entry in `.claude-plugin/marketplace.json`.

## License

[MIT](LICENSE)
