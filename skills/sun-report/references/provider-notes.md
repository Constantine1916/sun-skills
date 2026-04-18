# Provider Notes

## GitHub

- Data source: `gh api /user` and `gh api /users/<login>/events`
- The report is based on remote push events, not local git history.
- GitHub Events API is not a complete audit log.
- Official limits relevant to this skill:
  - only recent events are available
  - responses are limited in volume
  - event delivery may lag behind the actual push time
- Daily and weekly personal reports are a reasonable use case, but very high-volume accounts can still lose detail.

## GitLab

- Data source: `glab api /user` and `glab api /users/<id>/events?action=pushed`
- Self-managed GitLab is supported as long as `glab` can authenticate to the instance.
- The skill must always ask for the GitLab hostname because many companies use self-managed GitLab.
- Common self-managed failure modes:
  - wrong hostname
  - VPN or network isolation
  - custom CA / TLS trust problems
  - reverse proxy differences

## Summary-Only Degradation

- Some GitLab push events expose only summary metadata such as `commit_title`, `commit_count`, and `ref`.
- Bulk push events may not expose every commit directly.
- When the compare or commit detail fetch cannot recover the pushed commits, keep the event as `summary-only`.
- Never fabricate missing commit messages or links.

## Reporting Guidance

- Treat commit messages as activity hints, not full business context.
- Label inferred next steps as inference.
- If provider data is incomplete, say so explicitly in the final report.
