from typing import Dict, Any, List

from .model_service import OllamaClient
from .prompt_service import PromptService
from .retrieval_service import SimpleRetrievalService


class ChatService:
    def __init__(self, config: Dict[str, Any], client: OllamaClient):
        self.config = config
        self.client = client
        self.prompt_service = PromptService()
        self.retrieval_service = SimpleRetrievalService(config, client)

    def index_notes(self) -> Dict[str, Any]:
        return self.retrieval_service.index_notes()

    def search(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        if top_k is None:
            top_k = self.config.get("max_retrieved_chunks", 5)
        return self.retrieval_service.search(query, top_k=top_k)

    def chat(self, query: str, chat_model: str = None) -> Dict[str, Any]:
        model = chat_model or self.config["chat_model"]
        sources = self.search(query)
        messages = self.prompt_service.build_chat_prompt(query, sources)
        answer = self.client.chat(model, messages)
        return {
            "query": query,
            "answer": answer,
            "sources": [{"path": s["path"], "score": None} for s in sources],
        }
