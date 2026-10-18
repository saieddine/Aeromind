
import logging

from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool

from ..schemas.chat import ChatRequest, ChatResponse


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    method = request.method.lower().strip()

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    if method not in {"rag", "lightrag", "graphrag"}:
        raise HTTPException(
            status_code=400,
            detail="Unsupported RAG method.",
        )

    if method == "graphrag":
        raise HTTPException(
            status_code=501,
            detail="GraphRAG is not available yet.",
        )

    try:
        if method == "lightrag":
            # Import only when LightRAG is requested.
            from LighRag.lightrag_service import ask

            result = await ask(
                aircraft_id=request.aircraft_id,
                question=request.question,
                conversation_id=request.conversation_id or "",
                mode="hybrid",
            )

        else:
            # Preserve Seif's existing normal RAG implementation.
            from ..services.rag_service import get_rag_service

            service = get_rag_service()

            result = await run_in_threadpool(
                service.answer,
                aircraft_id=request.aircraft_id,
                question=request.question,
                document_id=request.document_id,
                conversation_history=[],
            )

            if request.conversation_id:
                result["metadata"]["conversation_id"] = (
                    request.conversation_id
                )

        return result

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid chat request.",
        ) from exc

    except Exception:
        logger.exception("Chat request failed")
        raise HTTPException(
            status_code=500,
            detail="The chat service encountered an error.",
        )
