# local-chat-app

A local-first chat application scaffold for Ollama-powered RAG.

## Setup

1. Activate the repo environment:
   ```bash
   source .venv/bin/activate
   ```
2. Install dependencies if needed:
   ```bash
   uv pip install -r requirements.txt
   ```
3. Create a `vault` directory at the repository root and add markdown notes.
4. Run indexing:
   ```bash
   python -m app.interfaces.cli.main index
   ```
5. Run a chat query:
   ```bash
   python -m app.interfaces.cli.main chat "What is my note about?"
   ```

## Dev workflow

Start the API server from the activated environment:
```bash
uvicorn app.interfaces.api.main:app --reload --host 0.0.0.0 --port 8000
```

Then open `app/interfaces/web/index.html` in your browser.

## Notes

- Config is loaded from `config.json`.
- Model profiles are defined in `config.json`.
- Use `.venv` for development so dependencies stay scoped to this repo.
- If you forget the setup, read `docs/uv-setup.md` for the uv workflow.




