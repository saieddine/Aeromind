
"""FastAPI service adapter for AeroMind's existing LightRAG implementation."""
from __future__ import annotations

from typing import Any


async def answer_with_lightrag(
    *,
    aircraft_id: str,
    question: str,
    document_id: str | None = None,
    conversation_id: str | None = None,
    conversation_history: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Run LightRAG and return the response expected by FastAPI."""

    # Import lazily so the other chat methods do not depend on LightRAG.
    from LighRag.lightrag_service import ask

    result = await ask(
        aircraft_id=aircraft_id,
        question=question,
        conversation_id=conversation_id or "",
        mode="hybrid",
    )

    # Keep the response compatible with ChatResponse and the other services.
    metadata = result.setdefault("metadata", {})
    metadata["method"] = "lightrag"
    metadata["aircraft_id"] = aircraft_id

    if conversation_id:
        metadata["conversation_id"] = conversation_id

    if document_id:
        metadata["document_id"] = document_id

    return {
        "answer": result.get("answer", ""),
        "sources": result.get("sources", []),
        "metadata": metadata,
    }
