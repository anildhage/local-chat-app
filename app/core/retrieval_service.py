import json
import os
import re
from datetime import datetime, timezone
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

    def _chunk_markdown(self, text: str, path: str) -> List[Dict[str, Any]]:
        lines = text.splitlines()
        chunks: List[Dict[str, Any]] = []
        current_heading = "Start"
        buffer: List[str] = []

        def flush() -> None:
            nonlocal buffer
            chunk_text = "\n".join(buffer).strip()
            if chunk_text:
                chunks.append({
                    "path": path,
                    "heading": current_heading,
                    "text": chunk_text,
                })
            buffer = []

        for line in lines:
            if re.match(r"^#{1,6}\s+", line):
                flush()
                current_heading = line.lstrip("#").strip()
                buffer.append(line)
            else:
                buffer.append(line)

        flush()

        final_chunks: List[Dict[str, Any]] = []
        for chunk in chunks:
            text = chunk["text"]
            if len(text) <= 1800:
                final_chunks.append({**chunk})
                continue

            paragraphs = text.split("\n\n")
            temp: List[str] = []
            temp_len = 0
            part = 0

            for para in paragraphs:
                if temp_len + len(para) > 1800 and temp:
                    final_chunks.append({
                        **chunk,
                        "chunk_index": part,
                        "text": "\n\n".join(temp).strip(),
                    })
                    temp = temp[-1:]
                    temp_len = sum(len(x) for x in temp)
                    part += 1

                temp.append(para)
                temp_len += len(para)

            if temp:
                final_chunks.append({
                    **chunk,
                    "chunk_index": part,
                    "text": "\n\n".join(temp).strip(),
                })

        for i, chunk in enumerate(final_chunks):
            chunk.setdefault("chunk_index", i)

        return final_chunks

    def index_notes(self) -> Dict[str, Any]:
        if not self.vault_path.exists():
            raise FileNotFoundError(f"Vault path not found: {self.vault_path}")

        all_chunks: List[Dict[str, Any]] = []
        for root, _, files in os.walk(self.vault_path):
            for fname in files:
                if not fname.lower().endswith(".md"):
                    continue
                path = Path(root) / fname
                try:
                    text = path.read_text(encoding="utf-8")
                except Exception:
                    continue

                all_chunks.extend(self._chunk_markdown(text, str(path)))

        if not all_chunks:
            self.index = {
                "chunks": [],
                "embedding_model": self.config["embedding_model"],
                "last_refreshed": None,
            }
            self._write_index()
            return self.index

        embeddings = self.client.embeddings(
            self.config["embedding_model"],
            [chunk["text"] for chunk in all_chunks],
        )

        for chunk, embedding in zip(all_chunks, embeddings):
            chunk["embedding"] = embedding

        self.index = {
            "chunks": all_chunks,
            "embedding_model": self.config["embedding_model"],
            "last_refreshed": datetime.now(timezone.utc).isoformat(),
        }
        self._write_index()
        return self.index

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if not self.index.get("chunks"):
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
            {"chunk": chunk, "score": cosine_similarity(query_embedding, chunk["embedding"])}
            for chunk in self.index["chunks"]
        ]
        scored.sort(key=lambda item: item["score"], reverse=True)
        return [item["chunk"] for item in scored[:top_k]]
