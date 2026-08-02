from pathlib import Path
from typing import Dict, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = {
    "vault_path": str(BASE_DIR / "../vault"),
    "ollama_url": "http://localhost:11434",
    "embedding_model": "qwen2.5-coder:1.5b",
    "chat_model": "qwen2.5-coder:1.5b",
    "active_profile": "fast-local",
    "profiles": {
        "fast-local": {
            "embedding_model": "qwen2.5-coder:1.5b",
            "chat_model": "qwen2.5-coder:1.5b",
        },
        "balanced-local": {
            "embedding_model": "qwen2.5-coder:1.5b",
            "chat_model": "qwen2.5-coder:1.5b",
        },
        "large-local": {
            "embedding_model": "qwen2.5-coder:1.5b",
            "chat_model": "qwen2.5-coder:1.5b",
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


def save_config(config: Dict[str, Any], config_path: Path = None) -> None:
    if config_path is None:
        config_path = BASE_DIR.parent / "config.json"
    import json

    with config_path.open("w", encoding="utf-8") as handle:
        json.dump(config, handle, indent=2)


def set_active_profile(profile_name: str, config_path: Path = None) -> Dict[str, Any]:
    config = load_config(config_path)
    profiles = config.get("profiles", {})
    if profile_name not in profiles:
        raise ValueError(f"Unknown profile: {profile_name}")
    config["active_profile"] = profile_name
    config.update(profiles[profile_name])
    save_config(config, config_path)
    return config


def set_active_model(chat_model: str, embedding_model: Optional[str] = None, config_path: Path = None) -> Dict[str, Any]:
    config = load_config(config_path)
    config["chat_model"] = chat_model
    config["embedding_model"] = embedding_model or chat_model
    config["active_profile"] = "custom"
    save_config(config, config_path)
    return config
