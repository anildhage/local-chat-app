---
name: session-summary
description: Summarize the current Copilot chat or session and append the summary to a session log in the docs folder.
---

- Review the current Copilot chat or active session context.
- Summarize the meaningful discussion, decisions, explanations, code guidance, and next steps from this session.
- Focus on what was discussed, decided, changed, or learned during the current development session.
- Do not invent context that is not present in the current chat or accessible session history.
- Update documentation files only.
- Append a new dated entry to `docs/session-log.md`.
- Never overwrite previous entries.
- Keep the log append-only.
- Use a clear timestamp for each new entry.
- Include: session summary, key topics discussed, important decisions, actions taken or suggested, and next steps if relevant.
- Keep the wording brief, practical, and easy to scan.
- Do not modify application code unless explicitly asked.
- If the current session history is not available, say so briefly instead of creating a misleading summary.
