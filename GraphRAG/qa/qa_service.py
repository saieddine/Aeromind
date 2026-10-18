"""Grounded GraphRAG QA service, separate from normal RAG."""
from __future__ import annotations

from typing import Any, Dict, List, Optional


class GraphRAGQAService:
    """Hybrid retrieval followed by one final call to the existing LLM."""

    def __init__(self, retriever, llm, *, aircraft_id="a320", method="graphrag"):
        if not hasattr(llm, "generate"):
            raise TypeError("llm must expose generate(prompt)")
        self.retriever = retriever
        self.llm = llm
        self.aircraft_id = aircraft_id
        self.method = method

    @staticmethod
    def _build_prompt(
        question: str,
        evidence: List[Dict[str, Any]],
        conversation_history=None,
        aircraft_id="a320",
    ):
        blocks = []
        for i, item in enumerate(evidence, 1):
            blocks.append("\n".join([
                f'SOURCE {i} ({item.get("kind", "evidence")})',
                f'Document: {item.get("document") or item.get("document_id") or "Unknown"}',
                f'Section: {item.get("section") or "Unknown"}',
                f'Page: {item.get("page") or "Unknown"}',
                f'Chunk ID: {item.get("chunk_id") or "Unknown"}',
                f'Evidence:\n{item.get("text") or ""}',
            ]))
        context = "\n\n".join(blocks) if blocks else "No relevant evidence was retrieved."

        history_lines = []
        for msg in (conversation_history or [])[-12:]:
            role = str(msg.get("role", "user")).upper()
            content = str(msg.get("content", "")).strip()
            if content:
                history_lines.append(f"{role}: {content}")
        history = "\n".join(history_lines) or "No previous conversation."

        return f"""You are AeroMind, an aircraft technical-document assistant.
Answer the user's current question using the supplied evidence.

GROUNDING RULES
1. Aircraft-specific facts, measurements, limits, configurations, and procedures must be supported by supplied evidence.
2. Do not invent facts or combine values from different variants or configurations.
3. Graph relationships are retrieval hints, not stronger evidence than original source passages.
4. If evidence is contradictory or insufficient, state that clearly.
5. Do not claim a source supports a statement unless its evidence does so.
6. Use the conversation history to interpret follow-up questions, but do not treat previous assistant answers as verified technical evidence.
7. Do not expose internal retrieval operations or graph-processing details to the user.
8. If no useful evidence was retrieved, say the available documentation is insufficient.

AIRCRAFT: {aircraft_id}

CONVERSATION HISTORY:
{history}

RETRIEVED EVIDENCE:
{context}

CURRENT USER QUESTION:
{question}

Answer naturally and directly. Include a short Sources list with document and page numbers when available."""

    def answer(
        self,
        question: str,
        *,
        conversation_id: Optional[str] = None,
        conversation_history=None,
        aircraft_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        question = (question or "").strip()
        if not question:
            raise ValueError("question must not be empty")

        aid = aircraft_id or self.aircraft_id
        retrieval = self.retriever.retrieve(question)
        evidence = retrieval.get("evidence", [])
        prompt = self._build_prompt(question, evidence, conversation_history, aid)
        answer = self.llm.generate(prompt)

        sources = []
        seen = set()
        for item in evidence:
            key = (item.get("document_id"), item.get("page"), item.get("chunk_id"))
            if key in seen:
                continue
            seen.add(key)
            sources.append({
                "document_id": item.get("document_id"),
                "document": item.get("document") or item.get("document_id"),
                "section": item.get("section"),
                "page": item.get("page"),
                "excerpt": (item.get("text") or "")[:700],
                "chunk_id": item.get("chunk_id"),
                "kind": item.get("kind"),
            })

        return {
            "conversation_id": conversation_id,
            "message_id": None,
            "answer": answer.strip() if isinstance(answer, str) else str(answer),
            "sources": sources,
            "metadata": {
                "method": self.method,
                "aircraft_id": aid,
                "graph_edges_retrieved": len(retrieval.get("graph_edges", [])),
                "vector_chunks_retrieved": len(retrieval.get("vector_chunks", [])),
                "evidence_items": len(evidence),
            },
            "debug": {
                "graph_edges": retrieval.get("graph_edges", []),
                "vector_chunks": retrieval.get("vector_chunks", []),
            },
        }
