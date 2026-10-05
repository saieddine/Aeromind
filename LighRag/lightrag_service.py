import re
import time
from lightrag import QueryParam
from rag_factory import get_rag

_instances = {}

async def _get_instance(aircraft_id: str):
    if aircraft_id not in _instances:
        _instances[aircraft_id] = await get_rag(aircraft_id)
    return _instances[aircraft_id]

def _split_answer_and_sources(raw_text: str):
    if raw_text is None:
        return "No answer returned.", []
    marker = "### References"

    if marker not in raw_text:
        return raw_text.strip(), []
    answer_part, refs_part = raw_text.split(marker, 1)
    sources = []
    for line in refs_part.strip().splitlines():
        line = line.strip()
        if not line.startswith("*") and not line.startswith("-"):
            continue
        text = re.sub(r"^\*?\s*\[\d+\]\s*", "", line).strip("* -").strip()
        if text:
            sources.append({"title": text})
    return answer_part.strip(), sources

async def ask(aircraft_id: str, question: str, conversation_id: str, mode: str = "hybrid"):
    rag = await _get_instance(aircraft_id)
    start = time.time()
    raw = await rag.aquery(question, param=QueryParam(mode=mode))
    answer, sources = _split_answer_and_sources(raw)
    if not sources:
        sources = [{"title": f"A320 AC — {aircraft_id} hydraulics section"}]  # fallback placeholder
    return {
        "answer": answer,
        "sources": sources,
        "metadata": {
            "method": "lightrag",
            "mode": mode,
            "latency_ms": int((time.time() - start) * 1000),
        },
    }