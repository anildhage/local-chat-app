from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import requests

from app.core.config import load_config
from app.core.model_service import get_client
from app.core.chat_service import ChatService
from app.interfaces.api.schemas import ChatRequest, ModelActionRequest

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
        return {
            "indexed_chunks": len(result.get("chunks", [])),
            "last_refreshed": result.get("last_refreshed"),
            "embedding_model": result.get("embedding_model"),
        }
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
    try:
        return service.chat(request.query, chat_model=request.chat_model)
    except requests.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/model/status")
def model_status(model: str):
    try:
        running_models = client.list_running_models()
        loaded = model in running_models
        return {"model": model, "loaded": loaded}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/model/offload")
def model_offload(request: "ModelActionRequest"):
    if not request.model:
        raise HTTPException(status_code=400, detail="Model is required")
    loaded = request.model in client.list_running_models()
    if not loaded:
        return {"model": request.model, "offloaded": False, "status": "not_loaded"}
    success = client.stop_model(request.model)
    if not success:
        raise HTTPException(status_code=500, detail=f"Failed to offload model {request.model}")
    return {"model": request.model, "offloaded": True, "status": "offloaded"}


@app.get("/config")
def get_config():
    return {
        "active_profile": config.get("active_profile"),
        "chat_model": config.get("chat_model"),
        "embedding_model": config.get("embedding_model"),
        "profiles": list(config.get("profiles", {}).keys()),
        "last_indexed": service.retrieval_service.index.get("last_refreshed"),
        "index_embedding_model": service.retrieval_service.index.get("embedding_model"),
    }
