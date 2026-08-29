# UV Setup for local-chat-app

This repo is set up for local Python development using `uv`.

## Why `uv` was chosen

- `uv` is the requested package manager and environment tool for this project.
- It creates a clean local virtual environment with a single command.
- It works well for fast local development without adding Poetry, Pipenv, or other tooling.
- It keeps dependency installation scoped to the repo and avoids modifying system Python.

## What was completed

- Created a local virtual environment at `.venv` with `uv venv .venv`.
- Bootstrapped `pip` inside `.venv` when the new environment did not include it by default.
- Installed dependencies from `requirements.txt` into `.venv`.
- Updated `.gitignore` so `.venv/` and `.uvcache/` are ignored by git.
- Used a repo-local uv cache directory (`.uvcache`) because the default system cache location on this machine had permission issues.

## Why the cache directory is required

- `uv` installs packages into the virtual environment, but it also downloads and resolves package metadata in a cache location.
- If the default cache path is not writable, package installation can fail before the packages are placed into `.venv`.
- Using `UV_CACHE_DIR=./.uvcache` keeps the cache local to the repo and avoids system permission problems.

## What this gives you

- A reproducible local development environment.
- A private Python interpreter at `.venv/bin/python`.
- Installed dependencies available only inside the repo's `.venv`.
- A simple workflow for starting the app locally.
