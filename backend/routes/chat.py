from fastapi import APIRouter, HTTPException

from ..schemas.chat import ChatRequest, ChatResponse
from ..services.rag_service import get_rag_service


router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if request.method.lower() != "rag":
        raise HTTPException(
            status_code=400,
            detail="Only method='rag' is available in this RAG integration.",
        )

    try:
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
        raise HTTPException(status_code=400, detail=str(exc))

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"RAG request failed: {exc}",
        )
