
import logging

from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool

from ..schemas.chat import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    method = (request.method or "rag").strip().lower()

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    if method not in {"rag", "lightrag", "graphrag"}:
        raise HTTPException(
            status_code=400,
            detail="Unsupported RAG method. Use 'rag', 'lightrag', or 'graphrag'.",
        )

    try:
        if method == "lightrag":
            # Use the backend service adapter for LightRAG.
            from ..services.lightrag_service import answer_with_lightrag

            result = await answer_with_lightrag(
                aircraft_id=request.aircraft_id,
                question=request.question,
                document_id=request.document_id,
                conversation_id=request.conversation_id,
                conversation_history=[],
            )

        elif method == "graphrag":
            # Preserve the existing GraphRAG implementation.
            from ..services.graphrag_service import answer_with_graphrag

            result = await run_in_threadpool(
                answer_with_graphrag,
                aircraft_id=request.aircraft_id,
                question=request.question,
                document_id=request.document_id,
                conversation_id=request.conversation_id,
                conversation_history=[],
            )

        else:
            # Preserve the existing standard RAG implementation.
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
            detail=str(exc),
        ) from exc

    except FileNotFoundError as exc:
        logger.exception("Required file missing for %s", method)
        raise HTTPException(
            status_code=503,
            detail="The requested chat service is not fully configured.",
        ) from exc

    except Exception as exc:
        logger.exception("%s request failed", method.upper())
        raise HTTPException(
            status_code=500,
            detail="The chat service encountered an error.",
        ) from exc
