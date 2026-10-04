from fastapi import FastAPI
from pydantic import BaseModel
from typing import Literal

from backend.routes.aircraft import router as aircraft_router


app = FastAPI(
    title="AeroMind API",
    description="Interactive Aircraft Intelligence Lab",
    version="0.1.0"
)


class ChatRequest(BaseModel):
    aircraft_id: str
    question: str
    conversation_id: str
    method: Literal["rag", "graphrag", "lightrag"] = "rag"


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "project": "AeroMind"
    }


@app.post("/api/chat")
def chat(request: ChatRequest):
    return {
        "answer": (
            f"Mock response for {request.aircraft_id}: "
            f"{request.question}"
        ),
        "sources": [],
        "metadata": {
            "method": request.method,
            "latency_ms": 10
        }
    }


app.include_router(aircraft_router)