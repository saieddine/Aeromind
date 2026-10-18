from fastapi import APIRouter, HTTPException

from ..schemas.chat import ChatRequest, ChatResponse
from ..services.rag_service import get_rag_service
from ..services.graphrag_service import answer_with_graphrag

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    method = (request.method or "rag").strip().lower()

    if method not in {"rag", "graphrag"}:
        raise HTTPException(
            status_code=400,
            detail="Unsupported method. Use method='rag' or method='graphrag'.",
        )

    try:
        if method == "graphrag":
            return answer_with_graphrag(
                aircraft_id=request.aircraft_id,
                question=request.question,
                document_id=request.document_id,
                conversation_id=request.conversation_id,
                conversation_history=[],
            )

        # Existing normal RAG path intentionally preserved.
        service = get_rag_service()
        result = service.answer(
            aircraft_id=request.aircraft_id,
            question=request.question,
            document_id=request.document_id,
            conversation_history=[],
        )
        if request.conversation_id:
            result["metadata"]["conversation_id"] = request.conversation_id
        return result

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"{method.upper()} request failed: {exc}",
        ) from exc
