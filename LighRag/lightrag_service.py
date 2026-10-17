
import time
from pathlib import Path

from lightrag import QueryParam

if __package__:
    from .rag_factory import get_rag
else:
    from rag_factory import get_rag


_instances = {}


async def _get_instance(aircraft_id: str):
    if aircraft_id not in _instances:
        _instances[aircraft_id] = await get_rag(aircraft_id)
    return _instances[aircraft_id]


def _extract_sources(data: dict) -> list[dict]:
    """Build source records from actual retrieved document chunks."""
    chunks = data.get("chunks") or []
    sources = []
    seen = set()

    for chunk in chunks:
        file_path = chunk.get("file_path")

        if not file_path:
            continue

        title = Path(file_path).name

        # Avoid duplicate document entries.
        if title in seen:
            continue

        seen.add(title)
        sources.append({"title": title})

    return sources


async def ask(
    aircraft_id: str,
    question: str,
    conversation_id: str,
    mode: str = "hybrid",
):
    if not isinstance(question, str) or not question.strip():
        raise ValueError("Question cannot be empty.")

    if mode not in {
        "local", "global", "hybrid", "naive", "mix", "bypass"
    }:
        raise ValueError("Unsupported LightRAG query mode.")

    start = time.perf_counter()

    rag = await _get_instance(aircraft_id)

    result = await rag.aquery_llm(
        question,
        param=QueryParam(
            mode=mode,
            enable_rerank=False,
            include_references=True,
            stream=False,
        ),
    )

    if result.get("status") != "success":
        raise RuntimeError(
            result.get("message", "LightRAG query failed.")
        )

    llm_response = result.get("llm_response") or {}
    answer = llm_response.get("content") or "No answer returned."

    data = result.get("data") or {}
    chunks = data.get("chunks") or []

    sources = _extract_sources(data)

    metadata = result.get("metadata") or {}
    processing_info = metadata.get("processing_info") or {}

    retrieved_chunks = processing_info.get("final_chunks_count")

    if retrieved_chunks is None:
        retrieved_chunks = len(chunks)

    return {
        "answer": answer,
        "sources": sources,
        "metadata": {
            "method": "lightrag",
            "aircraft_id": aircraft_id,
            "conversation_id": conversation_id,
            "mode": mode,
            "retrieved_chunks": retrieved_chunks,
            "latency_ms": int(
                (time.perf_counter() - start) * 1000
            ),
        },
    }
