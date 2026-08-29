# BotZapp

BotZapp is an open-source, local-first chatbot application for running retrieval-augmented generation (RAG) over Markdown notes.

This repo is built for local use only, with a focus on:
- working with markdown notes stored in a local vault
- using Ollama-compatible models for embeddings and chat
- keeping everything on your machine rather than deploying to production
- iterating quickly on UI and CLI workflows

## What is built today

- CLI chat interface with interactive commands
- local index generation from markdown notes
- a simple browser-based web UI served by FastAPI
- model management commands for Ollama
- config-driven profiles and active model switching
- local RAG over `.md` files

## What you can do

- index markdown notes from a vault
- ask questions against your notes
- switch chat and embedding models locally
- list and offload running Ollama models
- use either a command-line REPL or a browser UI

## Quick start

### 1. Clone the repo

```bash
git clone <repo-url>
cd local-chat-app
```

### 2. Create and activate a Python environment

Recommended if you have Python installed:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

If you use `uv`, you can also create the env with:

```bash
uv venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Prepare your vault

Add Markdown files to your local notes directory. The current config points to a vault path in `config.json`.

By default, the project uses `vault_path` from `config.json`.

### 5. Index your notes

```bash
python -m app.interfaces.cli.main index
```

### 6. Ask a chat query

```bash
python -m app.interfaces.cli.main chat "What is my note about?"
```

## Recommended local commands

### CLI chat

Start the interactive CLI:

```bash
./botzapp-cli
```

If you are not using the launcher script, use:

```bash
python -m app.interfaces.cli.main chat
```

### Web UI

Launch the web UI locally:

```bash
./botzapp-web
```

Or use the manual command:

```bash
uvicorn app.interfaces.api.main:app --reload --host 0.0.0.0 --port 8000
```

Then open `http://127.0.0.1:8000` in your browser.

There is also a macOS starter script at `start-ui.command` for double-click launch.

## CLI features

When running the CLI, the interactive mode supports:

- `/help` — show CLI command help
- `/bye` — exit chat mode
- `/list-models` — list installed Ollama models
- `/list-running` — list currently running models
- `/offload <model>` — unload a running model
- `/offload-all` — unload all running models
- `/model <name> [embedding]` — set active chat and embedding models
- `/status` — show active profile, models, and running model state

## Project structure

- `app/interfaces/cli/main.py` — CLI entrypoint
- `app/interfaces/api/main.py` — FastAPI server for the web UI and API
- `app/interfaces/web/index.html` — browser UI
- `app/core/chat_service.py` — chat orchestration and RAG logic
- `app/core/model_service.py` — Ollama model and embedding integration
- `app/core/retrieval_service.py` — index creation and search over markdown
- `app/core/config.py` — config load/save and profile management
- `config.json` — runtime settings and model profiles
- `requirements.txt` — Python dependencies
- `pyproject.toml` — package metadata and `botzapp-cli` script entrypoint
- `start-ui.command` — macOS double-click UI launcher

## Config and vault

The app uses `config.json` for:
- `vault_path`
- `ollama_url`
- `chat_model`
- `embedding_model`
- `active_profile`
- model profiles
- local index path
- retrieval settings

Update `vault_path` to point to your local markdown directory.

## Goals and direction

BotZapp is intended as a local knowledge assistant for your own notes.

Current goals:
- make the app easy to run locally
- support RAG over `.md` notes
- enable fast experimentation with Ollama models
- keep the workflow simple for personal/desktop use
- avoid production deployment complexity

Future improvements can include:
- richer web UI interactions
- better markdown parsing and indexing
- more robust local model/offload controls
- native Obsidian vault integration
- improved app branding and user experience

## Open source

This project is open source under the MIT License.

Feel free to fork it, improve it, and use it as a local-first knowledge assistant.

## Troubleshooting

- If `requests` or other dependencies are missing, activate `.venv` and reinstall:
  ```bash
  source .venv/bin/activate
  pip install -r requirements.txt
  ```
- If `botzapp-cli` is not found, ensure `.venv/bin` is active or run `./botzapp-cli` from the repo root.
- If the web UI does not start, verify `uvicorn` is installed and `app.interfaces.api.main` is reachable.
- Check `config.json` for your vault and model settings.




