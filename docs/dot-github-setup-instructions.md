# AI setup instructions for reusable .github configuration

Use this file as a handoff document for an AI agent or Copilot assistant that is setting up a similar repository workflow on another machine.

## Goal

Create a lightweight but useful GitHub Copilot setup for a project so that AI assistance follows consistent rules:

- prefer minimal, targeted changes
- avoid destructive edits
- keep documentation updates separate from code changes
- support reusable documentation and session-summary agents

## Expected result

The agent should create the following structure:

```text
.github/
  copilot-instructions.md
  agents/
    documentation.agent.md
    session-summary.agent.md
```

## Instructions for the agent

1. Create the `.github/agents` folder if it does not exist.
2. Create the three files listed above.
3. Use the exact content below.
4. Do not change any existing application code unless the user explicitly asks for it.
5. Keep the setup simple and reusable for future projects.

## File contents

### 1) .github/copilot-instructions.md

```md
# Copilot Instructions

Follow these rules when helping with this repository.

- Only work on the files I explicitly mention.
- Do not erase, replace, or refactor existing code unless I clearly ask for it.
- Prefer appending code, comments, or documentation over rewriting existing content.
- Only edit or delete exactly what I ask for, nothing more.
- If my request is unclear, ask a clarifying question first.
- In Agent mode, do only the actions I ask for.
- In Ask mode, answer only what I ask and keep responses short, practical, and sufficient.
- Keep changes minimal and targeted.
- Before making changes, briefly state what you are about to do.

Response style:
- Default to the shortest useful answer.
- Do not provide extra explanation, alternatives, or background unless I ask.
- Do not suggest unrelated improvements or next steps unless I ask.
- Use bullets instead of long paragraphs when possible.
- For simple questions, answer in 1 to 5 lines.

Scope:
- Keep the focus on coding, repo changes, and implementation help.
- Do not do deep research or long background analysis unless I explicitly ask for it.
- If a request needs deeper research or learning, keep the answer brief and let me use Perplexity for that separately.
```

### 2) .github/agents/documentation.agent.md

```md
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
```

### 3) .github/agents/session-summary.agent.md

```md
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
```

## Notes for reuse

- This setup works well for personal projects, local-first tools, and small repositories.
- It is especially useful when you want Copilot to stay disciplined and avoid broad rewrites.
- If the target repository already has a `docs` folder, keep the same log file names.
- If the target repository does not have a `docs` folder, create it first.

## Quick validation

After creating the files, the agent should confirm that:

- the `.github` folder exists
- the three files were created
- the content matches the templates above
- no unrelated files were modified
