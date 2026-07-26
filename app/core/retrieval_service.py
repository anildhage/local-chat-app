import json
from pathlib import Path
from typing import List, Dict, Any

from .config import load_config
from .model_service import OllamaClient


class SimpleRetrievalService:
    def __init__(self, config: Dict[str, Any], client: OllamaClient):
        self.config = config
        self.client = client
        self.vault_path = Path(config["vault_path"])
        self.index_path = Path(config["index_path"])
        self.index_path.mkdir(parents=True, exist_ok=True)
        self.index_file = self.index_path / "notes_index.json"
        self.index = self._load_index()

    def _load_index(self) -> Dict[str, Any]:
        if self.index_file.exists():
            with self.index_file.open("r", encoding="utf-8") as handle:
                return json.load(handle)
        return {}

    def _write_index(self) -> None:
        with self.index_file.open("w", encoding="utf-8") as handle:
            json.dump(self.index, handle, indent=2)

    def index_notes(self) -> Dict[str, Any]:
        if not self.vault_path.exists():
            raise FileNotFoundError(f"Vault path not found: {self.vault_path}")

        notes = []
        for path in sorted(self.vault_path.rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            notes.append({
                "path": str(path),
                "text": text,
            })

        if not notes:
            self.index = {"notes": []}
            self._write_index()
            return self.index

        embeddings = self.client.embeddings(self.config["embedding_model"], [note["text"] for note in notes])
        for note, embedding in zip(notes, embeddings):
            note["embedding"] = embedding

        self.index = {"notes": notes}
        self._write_index()
        return self.index

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if not self.index.get("notes"):
            return []

        query_embedding = self.client.embeddings(self.config["embedding_model"], [query])[0]

        def cosine_similarity(a: List[float], b: List[float]) -> float:
            dot = sum(x * y for x, y in zip(a, b))
            mag_a = sum(x * x for x in a) ** 0.5
            mag_b = sum(y * y for y in b) ** 0.5
            if mag_a == 0 or mag_b == 0:
                return 0.0
            return dot / (mag_a * mag_b)

        scored = [
            {"note": note, "score": cosine_similarity(query_embedding, note["embedding"])}
            for note in self.index["notes"]
        ]
        scored.sort(key=lambda item: item["score"], reverse=True)
        return [item["note"] for item in scored[:top_k]]
