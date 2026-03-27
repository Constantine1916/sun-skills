# sun-release-skills

Internal skill for releasing sun-skills to ClawHub.

## Usage

```bash
/release-skills
```

## Workflow

1. Update `CHANGELOG.md` with new version and changes
2. Update `CHANGELOG.zh.md` with Chinese translations
3. Bump version in `marketplace.json`
4. Update `README.md` and `README.zh.md` if needed
5. Commit all changes
6. Create git tag

## Version Format

Uses semantic versioning: `MAJOR.MINOR.PATCH`

- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes and small changes
