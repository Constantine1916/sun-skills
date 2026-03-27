# CLAUDE.md

## Project Overview

This is the **sun-skills** repository — a collection of skills for improving daily work efficiency with Claude Code.

## Workflow

### Release Process

Use `/release-skills` workflow. Never skip:

1. `CHANGELOG.md` + `CHANGELOG.zh.md`
2. `marketplace.json` version bump
3. `README.md` + `README.zh.md` if applicable
4. All files committed together before tag

### Code Style

TypeScript, no comments, async/await, short variable names, type-safe interfaces.

### Adding New Skills

All skills MUST use `sun-` prefix.

## Reference Docs

| Topic | File |
|-------|------|
| ClawHub/OpenClaw publishing | docs/publishing.md |

## Security

- No secret keys in code — use environment variables
- Validate and sanitize all user inputs
- Handle errors gracefully with meaningful messages

## Skill Loading Rules

| Rule | Description |
|------|-------------|
| Load project skills first | Project skills override system/user-level skills with same name |

Priority: project `skills/` → `$HOME/.sun-skills/` → system-level.

## Conventions

- All public skills go in `skills/` directory
- Internal/development skills go in `.claude/skills/`
- Screenshots for documentation go in `screenshots/`
- Scripts for publishing go in `scripts/`
