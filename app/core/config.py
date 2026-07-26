from pathlib import Path
from typing import Dict, Any

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = {
    "vault_path": str(BASE_DIR / "../vault"),
    "ollama_url": "http://localhost:11434",
    "embedding_model": "llama2-mini-alpha-7b",
    "chat_model": "llama2-mini-alpha-7b",
    "active_profile": "fast-local",
    "profiles": {
        "fast-local": {
            "embedding_model": "llama2-mini-alpha-7b",
            "chat_model": "llama2-mini-alpha-7b",
        },
        "balanced-local": {
            "embedding_model": "llama2-small",
            "chat_model": "llama2-small",
        },
        "large-local": {
            "embedding_model": "llama2",
            "chat_model": "llama2",
        },
    },
    "index_path": str(BASE_DIR / "../app/data/indexes"),
    "max_retrieved_chunks": 5,
    "debug": False,
}


def load_config(config_path: Path = None) -> Dict[str, Any]:
    if config_path is None:
        config_path = BASE_DIR.parent / "config.json"

    if config_path.exists():
        import json

        with config_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        merged = {**DEFAULT_CONFIG, **data}
        active_profile = merged.get("active_profile")
        profile = merged.get("profiles", {}).get(active_profile, {})
        merged.update(profile)
        return merged

    return DEFAULT_CONFIG
