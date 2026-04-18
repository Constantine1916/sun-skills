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
clawhub install sun-md2xhs
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

### Content Generation Skills

#### sun-md2xhs

Convert Markdown articles into Xiaohongshu (Little Red Book) style long-form image card sequences. Each card features user avatar, blue verified badge, and date — mimicking Xiaohongshu's native post style (white background, PingFang font). Content is precisely cut by height with no blank space.

```bash
# First-time setup: save name & avatar to ~/.md2xhsrc
bun ~/.claude/skills/sun-md2xhs/scripts/md2xhs.ts --init \
  --name "Your Name" \
  --avatar /path/to/avatar.jpg

# Daily usage: convert MD file to XHS image cards
bun ~/.claude/skills/sun-md2xhs/scripts/md2xhs.ts ~/article.md --out ~/Desktop/xhs-output/
```

**Options:**

| Option | Description | Required |
|--------|-------------|----------|
| `--init` | Initialize mode, saves config to `~/.md2xhsrc` | First-time only |
| `--name <name>` | Display name | After init: optional |
| `--avatar <path>` | Avatar image path | After init: optional |
| `--out <dir>` | Output directory | No, default `./output` |
| `--date <date>` | Date string (e.g., `2026年03月25日`) | No, default today |
| `--width <px>` | Card width in px | No, default `1080` |

**Markdown Support:**

| Element | Rendered As |
|---------|-------------|
| `## Heading` / `### Subheading` | Bold title text |
| `**Bold**` | Bold text |
| `- List item` | Bulleted list |
| `> Quote` | Gray text paragraph |
| `---` divider | Ignored |
| Emoji | Preserved as-is |

**Output Structure:**

```
<out-dir>/
  <filename>-01.png   ← Page 1
  <filename>-02.png   ← Page 2
  ...
  .tmp-html/          ← Intermediate HTML files
```

### Report Generation Skills

#### sun-report

Generate developer daily or weekly reports from account-level remote commits on GitHub, GitLab, or both. The skill summarizes pushed work into module-level output instead of listing raw commits.

**Installation:**

Install the `sun-skills` marketplace/plugin using the instructions above. `sun-report` is included once the repository is installed.

**Usage in Claude Code / Codex:**

```text
$sun-report 帮我写一个日报
$sun-report 帮我写一个周报
```

The skill will:

- Ask whether your work is on GitHub, GitLab, or both
- Check `gh` / `glab` login status before collecting data
- Support self-hosted GitLab instances by hostname
- Only count commits that have already been pushed to the remote platform
- Use Beijing time for daily and weekly windows

**Direct script usage:**

```bash
python3 ~/.codex/skills/sun-report/scripts/sun_report.py \
  --report-type weekly \
  --providers github
```

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
