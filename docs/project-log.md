# Project Log

Append-only record of development changes captured from repository work.

---

### 2026-07-26
- Set up a local Python development environment using `uv`, created `.venv`, installed dependencies from `requirements.txt`, and added `.venv`/`.uvcache` to `.gitignore`.
- Added initial app scaffolding for a local chat/RAG workflow, including core services, CLI entrypoint, FastAPI API, and a simple web UI.
- Added project documentation in `docs/uv-setup.md` and created Copilot customization files under `.copilot/` and `.github/agents/`.
- Added workspace/debug support through `.vscode/launch.json` and `.vscode/settings.json` for local development.

---

### 2026-08-01
- **Ollama integration:** Verified Ollama server reachable; tested `/api/chat` (streaming NDJSON) and `/api/embeddings` with curl to confirm response shapes.
- **Robust model client:** Updated `app/core/model_service.py` to handle streaming NDJSON chat responses, try non-stream and stream paths, try multiple endpoint variants, and to tolerate different embedding response shapes (pad/normalize empty or mismatched embeddings).
- **Config updates:** Pointed runtime config to the working model and vault:
	- Updated `config.json` and `app/core/config.py` defaults to use `qwen2.5-coder:1.5b` for `chat_model` and `embedding_model`.
	- Set `vault_path` to the user's Obsidian vault `/Users/anildhage/Downloads/anil`.
- **Web UI:** Confirmed the static browser interface lives at `app/interfaces/web/index.html` and sends chat requests to the FastAPI `/chat` API.
- **Indexing discovery:** Made `app/core/retrieval_service.py` use `os.walk` (and skip unreadable files) to find `.md` files more robustly.
- **Embeddings fallback:** Ensured `embeddings()` always returns one embedding per input (pads with empty lists when the model returns no embedding).
- **Diagnostics & testing:** Ran local probes and CLI checks. Encountered sandbox/permission differences when running indexing from the editor environment (Python process saw 0 `.md` files while shell `find` reported 77). Running the CLI in the normal terminal produced expected chat responses once `config.json` and model were set.
- **Next steps:** Index the vault from the normal terminal (or grant file-access to the process used for indexing) to populate `app/data/indexes/notes_index.json`, then run `python -m app.interfaces.cli.main chat "<question>"` to query indexed notes.
- **Today’s achievement:** Patched `app/core/model_service.py` so Ollama embeddings now fall back to `ollama run ... --format json --dimensions 768` when `/api/embeddings` returns empty arrays.
- **Problem fixed:** Before, `notes_index.json` stored `embedding: []` because Ollama HTTP embedding responses were invalid; now the index stores real numeric vectors and search can compute cosine similarity correctly.
- **Verification:** Confirmed indexing works with the local `.venv` interpreter and produced 404 indexed markdown chunks.

---

### 2026-08-02
- Added a UI index refresh workflow in `app/interfaces/web/index.html` with a small refresh button and timestamp display under the embedding model.
- Persisted embedding index metadata in `app/data/indexes/notes_index.json` through `app/core/retrieval_service.py`, including `last_refreshed` and the active `embedding_model`.
- Exposed refresh metadata via FastAPI `/config` and `/index` endpoints in `app/interfaces/api/main.py` so the web UI can show the latest index timestamp.
- Improved the web UI interaction experience:
  - changed the send button to pulse lighter instead of rotate while waiting,
  - added model load status and offload control,
  - persisted selected chat model in local storage,
  - added a compact refresh section under the embedding model status.
- Notes: The UI now supports live index refresh from the vault and displays the latest refresh time in a lightweight style beneath the embedding model.

