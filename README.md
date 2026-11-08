<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/clever-cc-plugins/.github/main/assets/logo-dark.svg" />
    <img src="https://raw.githubusercontent.com/clever-cc-plugins/.github/main/assets/logo.svg" width="220" alt="clever [cc] plugins" />
  </picture>
</p>

# clever-cc-plugins marketplace

The umbrella marketplace catalog for Claude Code plugins. A single `/plugin marketplace add` gives you access to every plugin maintained under this catalog. Think of it as an `apt` source for the family: add the repository once, then install what you need.

## Installation

Open Claude Code in any project and add the marketplace:

```
# in any Claude Code project
$ /plugin marketplace add clever-cc-plugins/marketplace
✓ marketplace added · 8 plugins available
```

Then install any plugin from the catalog:

```
$ /plugin install cc-config@clever-cc-plugins
✓ cc-config installed

$ /plugin install cc-concept@clever-cc-plugins
✓ cc-concept installed

$ /plugin install cc-content@clever-cc-plugins
✓ cc-content installed

$ /plugin install cc-career@clever-cc-plugins
✓ cc-career installed

$ /plugin install cc-coach@clever-cc-plugins
✓ cc-coach installed

$ /plugin install cc-handoff@clever-cc-plugins
✓ cc-handoff installed

$ /plugin install cc-chime@clever-cc-plugins
✓ cc-chime installed

$ /plugin install cc-chef@clever-cc-plugins
✓ cc-chef installed
```

### Keeping Plugins Current

Auto-update is off by default for third-party marketplaces. To switch it on:

1. Run `/plugin` in Claude Code
2. Open the **Marketplaces** tab
3. Toggle auto-update for `clever-cc-plugins/marketplace`

Once it's on, Claude Code updates the plugins on startup whenever a new version is available.

### Uninstalling

To remove a single plugin and keep the marketplace:

```
/plugin uninstall cc-config@clever-cc-plugins
```

To remove the marketplace and every plugin you installed from it in one step:

```
/plugin marketplace remove clever-cc-plugins
```

## Available Plugins

| Plugin                                                                                                                                                                                                               | Skills                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | What it does                                                                                        |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| <img src="https://raw.githubusercontent.com/clever-cc-plugins/.github/main/assets/plugin-icons/cc-config.svg" width="48" height="48" alt="" /><br />[`cc-config`](https://github.com/clever-cc-plugins/cc-config)    | `/cc-config:bootstrapping-config`, `/cc-config:auditing-config`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | Bootstrap and audit Claude Code configurations                                                      |
| <img src="https://raw.githubusercontent.com/clever-cc-plugins/.github/main/assets/plugin-icons/cc-concept.svg" width="48" height="48" alt="" /><br />[`cc-concept`](https://github.com/clever-cc-plugins/cc-concept) | `/cc-concept:strategy-onboarding`, `/cc-concept:audience-personas`, `/cc-concept:positioning`, `/cc-concept:competitive-research`, `/cc-concept:seo-research`, `/cc-concept:campaign-concept`, `/cc-concept:channel-advisor`, `/cc-concept:editorial-strategy`, `/cc-concept:gtm-plan`, `/cc-concept:strategy-orchestrator`, `/cc-concept:marketing-advisor`, `/cc-concept:strategy-performance-review`, `/cc-concept:learnings-promotion`                                                                                                                                                                                                              | Marketing-strategy skills: positioning, competitive analysis, go-to-market, and campaign concepting |
| <img src="https://raw.githubusercontent.com/clever-cc-plugins/.github/main/assets/plugin-icons/cc-content.svg" width="48" height="48" alt="" /><br />[`cc-content`](https://github.com/clever-cc-plugins/cc-content) | `/cc-content:content-onboarding`, `/cc-content:register-context`, `/cc-content:brand-voice`, `/cc-content:samples-curation`, `/cc-content:research-prompt`, `/cc-content:content-ideation`, `/cc-content:linkedin-post`, `/cc-content:x-post`, `/cc-content:facebook-post`, `/cc-content:instagram-post`, `/cc-content:blog-article`, `/cc-content:marketing-email`, `/cc-content:press-release`, `/cc-content:landing-page`, `/cc-content:gated-long-form-content`, `/cc-content:long-tail-copy`, `/cc-content:atomize`, `/cc-content:humanize`, `/cc-content:content-performance-review`, `/cc-content:session-wrap`, `/cc-content:new-content-skill` | Content creation skills for marketing projects                                                      |
| <img src="https://raw.githubusercontent.com/clever-cc-plugins/.github/main/assets/plugin-icons/cc-career.svg" width="48" height="48" alt="" /><br />[`cc-career`](https://github.com/clever-cc-plugins/cc-career)    | `/cc-career:career-onboarding`, `/cc-career:career-plan`, `/cc-career:personal-branding-strategy`, `/cc-career:career-performance-review`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | Career planning, upleveling, and personal-branding strategy skills                                  |
| <img src="https://raw.githubusercontent.com/clever-cc-plugins/.github/main/assets/plugin-icons/cc-coach.svg" width="48" height="48" alt="" /><br />[`cc-coach`](https://github.com/clever-cc-plugins/cc-coach)       | `/cc-coach:career-coach`, `/cc-coach:life-coach`, `/cc-coach:networking-coach`, `/cc-coach:presentation-coach`, `/cc-coach:productivity-coach`, `/cc-coach:research-prompt`, `/cc-coach:new-coaching-skill`                                                                                                                                                                                                                                                                                                                                                                                                                                             | Live-coaching skills for job-related and personal-life topics                                       |
| <img src="https://raw.githubusercontent.com/clever-cc-plugins/.github/main/assets/plugin-icons/cc-handoff.svg" width="48" height="48" alt="" /><br />[`cc-handoff`](https://github.com/clever-cc-plugins/cc-handoff) | `/cc-handoff:handoff`, `/cc-handoff:handoff-install`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | Create and restore handoff summaries for moving work between machines and sessions                  |
| <img src="https://raw.githubusercontent.com/clever-cc-plugins/.github/main/assets/plugin-icons/cc-chime.svg" width="48" height="48" alt="" /><br />[`cc-chime`](https://github.com/clever-cc-plugins/cc-chime)       | _(hook-based, no slash commands)_                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | Plays an audio notification at the end of every Claude turn and when Claude needs your input        |
| <img src="https://raw.githubusercontent.com/clever-cc-plugins/.github/main/assets/plugin-icons/cc-chef.svg" width="48" height="48" alt="" /><br />[`cc-chef`](https://github.com/clever-cc-plugins/cc-chef)          | `/cc-chef:chef-onboarding`, `/cc-chef:create-recipe`, `/cc-chef:rework-recipe`, `/cc-chef:dietary-guidelines`, `/cc-chef:research-prompt`, `/cc-chef:export-recipe`, `/cc-chef:tandoor-food-cleanup`                                                                                                                                                                                                                                                                                                                                                                                                                                                    | Create, adapt, rework, and export grounded everyday recipes                                         |

Each plugin's repository has the full usage documentation.

## How This Works

Each plugin lives in its own repository, and this catalog references it via `git-subdir` in `.claude-plugin/marketplace.json`. When Claude Code installs a plugin from this marketplace, it fetches the `plugins/<name>/` subdirectory directly from the plugin's own repo. Nothing is duplicated here.

To add a new plugin to the catalog, you only need a new entry in `.claude-plugin/marketplace.json`.

## License

[MIT](LICENSE), Copyright (c) 2026 Michael van Laar

---

<p align="center">
  Part of the <a href="https://github.com/clever-cc-plugins">clever-cc-plugins</a> family · <a href="https://github.com/clever-cc-plugins/cc-config">cc-config</a> · <a href="https://github.com/clever-cc-plugins/cc-concept">cc-concept</a> · <a href="https://github.com/clever-cc-plugins/cc-content">cc-content</a> · <a href="https://github.com/clever-cc-plugins/cc-career">cc-career</a> · <a href="https://github.com/clever-cc-plugins/cc-coach">cc-coach</a> · <a href="https://github.com/clever-cc-plugins/cc-handoff">cc-handoff</a> · <a href="https://github.com/clever-cc-plugins/cc-chime">cc-chime</a> · <a href="https://github.com/clever-cc-plugins/cc-chef">cc-chef</a>
</p>
