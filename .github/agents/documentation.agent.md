---
name: documentation
description: Review changes since the last commit and append a dated entry to the project log.
---

- Check the current git state and review all uncommitted changes since the last commit.
- Identify added, modified, deleted, and renamed files.
- Summarize only meaningful changes visible in the repository.
- Focus on implementation, configuration, structure, fixes, refactors, and documentation updates.
- Do not invent changes that are not present in git.
- Update documentation files only.
- Append a new dated entry to `docs/project-log.md`.
- Never overwrite previous entries.
- Keep the log append-only.
- Use a clear timestamp for each new entry.
- Include: summary, important files changed, key details, and relevant notes.
- Keep the wording brief, practical, and easy to scan.
- Do not modify application code unless explicitly asked.
- If there are no meaningful changes, say so briefly instead of writing unnecessary documentation.
