"""FastAPI service adapter for AeroMind's existing GraphRAG components."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from time import perf_counter
from typing import Any

from GraphRAG.qa.qa_service import GraphRAGQAService
from GraphRAG.retrieval.chroma_reader import open_existing_collection
from GraphRAG.retrieval.graph_retriever import GraphRetriever
from GraphRAG.retrieval.hybrid_retriever import HybridRetriever
from rag.assistant.llm.llm_client import LLM
from rag.ingestion.embedder_aeromind import generate_embedding

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_AIRCRAFT_ID = "a320"
DEFAULT_DOCUMENT_ID = "a320_ac_0624"
DEFAULT_COLLECTION_NAME = "aeromind_knowledge"


@lru_cache(maxsize=8)
def get_graphrag_service(
    aircraft_id: str = DEFAULT_AIRCRAFT_ID,
    document_id: str | None = None,
) -> GraphRAGQAService:
    """Initialize and cache GraphRAG resources for the current A320 graph."""
    aircraft_id = (aircraft_id or DEFAULT_AIRCRAFT_ID).strip().lower()
    selected_document_id = (document_id or DEFAULT_DOCUMENT_ID).strip()

    if aircraft_id != DEFAULT_AIRCRAFT_ID:
        raise ValueError(
            f"GraphRAG is currently configured for aircraft_id='{DEFAULT_AIRCRAFT_ID}' only."
        )
    if selected_document_id != DEFAULT_DOCUMENT_ID:
        raise ValueError(
            "GraphRAG is currently configured for document_id='a320_ac_0624' only."
        )

    graph_path = PROJECT_ROOT / "GraphRAG" / "storage" / "a320_ac_0624_graph.json"
    graph_retriever = GraphRetriever(
        graph_path,
        aircraft_id=aircraft_id,
        document_id=selected_document_id,
    )
    _client, collection = open_existing_collection(
        project_root=PROJECT_ROOT,
        collection_name=DEFAULT_COLLECTION_NAME,
    )
    hybrid_retriever = HybridRetriever(
        graph_retriever=graph_retriever,
        collection=collection,
        embed_query=generate_embedding,
        aircraft_id=aircraft_id,
        document_id=selected_document_id,
        vector_top_k=5,
        graph_top_k=10,
    )
    return GraphRAGQAService(
        retriever=hybrid_retriever,
        llm=LLM(),
        aircraft_id=aircraft_id,
        method="graphrag",
    )


def answer_with_graphrag(
    *,
    aircraft_id: str,
    question: str,
    document_id: str | None = None,
    conversation_id: str | None = None,
    conversation_history: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Run GraphRAG and normalize its output to the FastAPI ChatResponse schema."""
    service = get_graphrag_service(aircraft_id, document_id)
    started = perf_counter()
    result = service.answer(
        question=question,
        conversation_id=conversation_id,
        conversation_history=conversation_history or [],
        aircraft_id=aircraft_id,
    )
    latency_ms = (perf_counter() - started) * 1000

    normalized_sources = []
    seen = set()
    for source in result.get("sources", []):
        key = (source.get("document_id"), source.get("page"), source.get("chunk_id"))
        if key in seen:
            continue
        seen.add(key)
        normalized_sources.append({
            "document_id": source.get("document_id") or document_id or DEFAULT_DOCUMENT_ID,
            "title": source.get("document") or source.get("title") or source.get("document_id"),
            "section": source.get("section"),
            "page": source.get("page"),
            "chunk_id": source.get("chunk_id"),
        })

    return {
        "answer": result.get("answer", ""),
        "sources": normalized_sources,
        "metadata": {
            "method": "graphrag",
            "aircraft_id": aircraft_id,
            "document_id": document_id or DEFAULT_DOCUMENT_ID,
            "retrieved_chunks": len(normalized_sources),
            "latency_ms": round(latency_ms, 2),
        },
    }
