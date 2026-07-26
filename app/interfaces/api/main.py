from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import load_config
from app.core.model_service import get_client
from app.core.chat_service import ChatService
from app.interfaces.api.schemas import ChatRequest

app = FastAPI(title="Local Chat App API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

config = load_config()
client = get_client(config)
service = ChatService(config, client)


@app.get("/health")
def health():
    return {"status": "ok", "active_profile": config.get("active_profile")}


@app.post("/index")
def index_notes():
    try:
        result = service.index_notes()
        return {"indexed_notes": len(result.get("notes", []))}
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.get("/search")
def search(query: str, top_k: int = 5):
    results = service.search(query, top_k=top_k)
    return {"results": [{"path": item["path"], "text": item["text"]} for item in results]}


@app.post("/chat")
def chat(request: ChatRequest):
    if not request.query:
        raise HTTPException(status_code=400, detail="Query is required")
    return service.chat(request.query)


@app.get("/config")
def get_config():
    return {
        "active_profile": config.get("active_profile"),
        "chat_model": config.get("chat_model"),
        "embedding_model": config.get("embedding_model"),
        "profiles": list(config.get("profiles", {}).keys()),
    }
