from typing import Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    query: str
    chat_model: Optional[str] = None


class ModelActionRequest(BaseModel):
    model: str
