import os
from typing import Dict, Any, List

import requests


class OllamaClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def embeddings(self, model: str, texts: List[str]) -> List[List[float]]:
        response = requests.post(
            f"{self.base_url}/api/embeddings",
            json={"model": model, "input": texts},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["embedding"]

    def chat(self, model: str, messages: List[Dict[str, str]], timeout: int = 60) -> str:
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={"model": model, "messages": messages},
            timeout=timeout,
        )
        response.raise_for_status()
        return response.json()["message"]["content"]


def get_client(config: Dict[str, Any]) -> OllamaClient:
    return OllamaClient(config["ollama_url"])
