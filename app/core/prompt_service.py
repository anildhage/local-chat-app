from typing import List, Dict, Any


class PromptService:
    BASE_SYSTEM_PROMPT = (
        "You are a helpful local assistant. Use the provided note context to answer the user query. "
        "If the context is insufficient, be transparent about the limitations."
    )

    def build_chat_prompt(self, query: str, sources: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        context_snippets = []
        for source in sources:
            text = source.get("text", "")
            snippet = text.strip().replace("\n", " ")[:800]
            context_snippets.append(f"- {source.get('path')}\n{snippet}")

        context_block = "\n\n".join(context_snippets) if context_snippets else "No retrieved note context available."
        content = (
            f"{self.BASE_SYSTEM_PROMPT}\n\n" 
            f"Here are the retrieved notes:\n{context_block}\n\n"
            f"User question: {query}\n\n"
            f"Answer using the note content and cite note file paths when helpful."
        )

        return [
            {"role": "system", "content": self.BASE_SYSTEM_PROMPT},
            {"role": "user", "content": content},
        ]
