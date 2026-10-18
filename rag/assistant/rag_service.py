"""AeroMind RAG answer-generation service.

Phase 3 responsibilities:
    question -> embedding -> retrieval -> grounded prompt -> LLM answer
    -> clean API-ready answer + deduplicated sources
"""

from time import perf_counter

from .llm.llm_client import LLM


class RAGService:
    """Coordinates retrieval and grounded answer generation."""

    def __init__(self, retriever, embedder, collection, top_k=5, llm=None):
        self.retriever = retriever
        self.embedder = embedder
        self.collection = collection
        self.top_k = top_k
        self.llm = llm or LLM()

    @staticmethod
    def _build_prompt(aircraft_id, question, retrieved_chunks, conversation_history):
        if retrieved_chunks:
            source_blocks = []
            for index, chunk in enumerate(retrieved_chunks, start=1):
                source_blocks.append(
                    "\n".join(
                        [
                            f"SOURCE {index}",
                            f"Aircraft: {chunk.get('aircraft_id') or aircraft_id}",
                            f"Document: {chunk.get('document') or chunk.get('document_id') or 'Unknown'}",
                            f"Section: {chunk.get('section') or 'Unknown'}",
                            f"Concept: {chunk.get('concept') or 'Unknown'}",
                            f"Page: {chunk.get('page') or 'Unknown'}",
                            f"Content:\n{chunk.get('text', '')}",
                        ]
                    )
                )
            context = "\n\n".join(source_blocks)
            retrieval_status = "Relevant aircraft-document material was retrieved."
        else:
            context = "No sufficiently relevant aircraft-document material was retrieved."
            retrieval_status = "No sufficiently relevant aircraft-document material was retrieved."

        history_blocks = []
        for message in (conversation_history or [])[-6:]:
            role = str(message.get("role", "user")).upper()
            content = str(message.get("content", "")).strip()
            if content:
                history_blocks.append(f"{role}: {content}")
        history_text = "\n".join(history_blocks) or "No previous conversation."

        return f"""
You are AeroMind, a professional aircraft technical assistant.

Answer the user's question using the supplied aircraft-document evidence.

GROUNDING RULES
1. Aircraft-specific facts must come from the supplied evidence whenever evidence is available.
2. Never invent aircraft specifications, dimensions, weights, limits, procedures, configurations, or values.
3. If the evidence is insufficient, clearly say that you cannot answer confidently from the available aircraft documentation.
4. If the evidence contains different variants, weight variants, configurations, or conditions, keep them separate and name the relevant one.
5. If the question asks for a single value but the documentation provides multiple applicable values, explain the distinction instead of silently choosing one.
6. Do not combine values from different variants/configurations to create a new specification.
7. You may use general knowledge only to explain terminology or make the retrieved material easier to understand; do not use it to invent missing aircraft-specific facts.

ANSWER STYLE
1. Answer the question directly in the first sentence.
2. Be concise for simple factual questions.
3. Add a short clarification when variant/configuration/context matters.
4. Use bullets or a small table only when they genuinely improve clarity.
5. Use normal Markdown when useful, but do not output raw JSON.
6. Do not repeat the question.
7. Do not mention RAG, retrieval, embeddings, ChromaDB, chunks, prompts, OpenRouter, or internal implementation.
8. Do not mention source numbers such as SOURCE 1 or SOURCE 2.
9. Do not fabricate citations or page references inside the answer. Source information is returned separately by the API.
10. Do not say "according to the documentation" unless that wording is genuinely useful.

AIRCRAFT
{aircraft_id}

USER QUESTION
{question}

CONVERSATION HISTORY
{history_text}

RETRIEVAL STATUS
{retrieval_status}

RETRIEVED AIRCRAFT DOCUMENT MATERIAL
============================================================
{context}
============================================================

Return only the final answer to the user.
""".strip()

    @staticmethod
    def _build_sources(retrieved_chunks, document_id):
        """Return clean, deduplicated source references for the API."""
        sources = []
        seen = set()

        for chunk in retrieved_chunks:
            source = {
                "document_id": chunk.get("document_id") or document_id,
                "title": chunk.get("concept"),
                "section": chunk.get("section"),
                "page": chunk.get("page"),
                "chunk_id": chunk.get("chunk_id"),
            }

            # Keep repeated pages/chunks out of the public source list.
            key = (
                source["document_id"],
                source["section"],
                source["page"],
            )
            if key in seen:
                continue

            seen.add(key)
            sources.append(source)

        return sources

    def answer(self, aircraft_id, question, document_id=None, conversation_history=None):
        """Retrieve relevant aircraft material and generate a grounded answer."""
        if not aircraft_id or not aircraft_id.strip():
            raise ValueError("aircraft_id is required")

        if not question or not question.strip():
            raise ValueError("question is required")

        document_id = document_id or "a320_ac_0624"
        conversation_history = conversation_history or []

        started = perf_counter()

        question_embedding = self.embedder(question)

        retrieved_chunks = self.retriever(
            collection=self.collection,
            aircraft_id=aircraft_id,
            document_id=document_id,
            query=question,
            question_embedding=question_embedding,
            top_k=self.top_k,
        )

        prompt = self._build_prompt(
            aircraft_id=aircraft_id,
            question=question,
            retrieved_chunks=retrieved_chunks,
            conversation_history=conversation_history,
        )

        generated_answer = self.llm.generate(prompt)
        latency_ms = (perf_counter() - started) * 1000

        return {
            "answer": generated_answer,
            "sources": self._build_sources(retrieved_chunks, document_id),
            "metadata": {
                "method": "rag",
                "aircraft_id": aircraft_id,
                "document_id": document_id,
                "retrieved_chunks": len(retrieved_chunks),
                "latency_ms": round(latency_ms, 2),
            },
        }
