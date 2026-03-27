# sun-skills

English | [中文](./README.zh.md)

Skills shared by Sun for improving daily work efficiency with Claude Code.

## Prerequisites

- Node.js environment installed
- Ability to run `npx bun` commands

## Installation

### Quick Install (Recommended)

```bash
npx skills add sun/sun-skills
```

### Publish to ClawHub / OpenClaw

This repository now supports publishing each `skills/sun-*` directory as an individual ClawHub skill.

```bash
# Preview what would be published
./scripts/sync-clawhub.sh --dry-run

# Publish all changed skills from ./skills
./scripts/sync-clawhub.sh --all
```

ClawHub installs skills individually, not as one marketplace bundle. After publishing, users can install specific skills such as:

```bash
clawhub install sun-imagine
clawhub install sun-markdown-to-html
```

Publishing to ClawHub releases the published skill under `MIT-0`, per ClawHub's registry rules.

### Register as Plugin Marketplace

Run the following command in Claude Code:

```bash
/plugin marketplace add Constantine1916/sun-skills
```

### Install Skills

**Option 1: Via Browse UI**

1. Select **Browse and install plugins**
2. Select **sun-skills**
3. Select the **sun-skills** plugin
4. Select **Install now**

**Option 2: Direct Install**

```bash
# Install the marketplace's single plugin
/plugin install sun-skills@sun-skills
```

**Option 3: Ask the Agent**

Simply tell Claude Code:

> Please install Skills from github.com/Constantine1916/sun-skills

### Available Plugin

The marketplace now exposes a single plugin so each skill is registered exactly once.

| Plugin | Description | Includes |
|--------|-------------|----------|
| **sun-skills** | Skills for daily work efficiency | All skills in this repository |

## Update Skills

To update skills to the latest version:

1. Run `/plugin` in Claude Code
2. Switch to **Marketplaces** tab (use arrow keys or Tab)
3. Select **sun-skills**
4. Choose **Update marketplace**

You can also **Enable auto-update** to get the latest versions automatically.

## Available Skills

Stay tuned! This repository is under active development.

## Environment Configuration

Some skills require API keys or custom configuration. Environment variables can be set in `.env` files:

1. CLI environment variables (e.g., `OPENAI_API_KEY=xxx /sun-skill ...`)
2. `process.env` (system environment)
3. `<cwd>/.sun-skills/.env` (project-level)
4. `~/.sun-skills/.env` (user-level)

## Disclaimer

This project is provided as-is for personal and educational use.

## Credits

This project was inspired by [baoyu-skills](https://github.com/JimLiu/baoyu-skills).
