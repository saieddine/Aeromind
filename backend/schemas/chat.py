from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    aircraft_id: str = Field(..., min_length=1)
    question: str = Field(..., min_length=1)
    conversation_id: str | None = None
    document_id: str | None = None
    method: str = "rag"


class ChatSource(BaseModel):
    document_id: str | None = None
    title: str | None = None
    section: str | None = None
    page: int | str | None = None
    chunk_id: str | None = None


class ChatMetadata(BaseModel):
    method: str
    aircraft_id: str
    document_id: str | None = None
    retrieved_chunks: int = 0
    latency_ms: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[ChatSource]
    metadata: ChatMetadata
