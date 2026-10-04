import time

from .context_builder import ContextBuilder
from .source_formatter import SourceFormatter
from .llm.llm_client import llm_client
from .prompts.assistant_prompt import AssistantPrompt


class RAGService:
    """
    Main AeroMind RAG orchestration layer.

    It connects:
        embedding -> retrieval -> context -> LLM -> sources
    """

    def __init__(
        self,
        retriever,
        embedder,
        collection,
        top_k: int = 5,
    ):
        self.retriever = retriever
        self.embedder = embedder
        self.collection = collection
        self.top_k = top_k

        self.context_builder = ContextBuilder()
        self.source_formatter = SourceFormatter()

    def answer(
        self,
        aircraft_id: str,
        question: str,
        document_id: str | None = None,
        conversation_history: list[dict] | None = None,
    ) -> dict:
        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        start = time.perf_counter()
        question = question.strip()

        question_embedding = self.embedder(question)

        chunks = self.retriever(
            collection=self.collection,
            aircraft_id=aircraft_id,
            document_id=document_id,
            question=question,
            question_embedding=question_embedding,
            top_k=self.top_k,
        )

        chunks = chunks or []

        context = self.context_builder.build(chunks)

        system_prompt = AssistantPrompt.build_system_prompt()
        user_prompt = AssistantPrompt.build_user_prompt(
            question=question,
            context=context,
            conversation_history=conversation_history,
        )

        answer = llm_client.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.0,
        )

        latency_ms = round((time.perf_counter() - start) * 1000, 2)

        return {
            "answer": answer,
            "sources": self.source_formatter.format(chunks),
            "metadata": {
                "method": "rag",
                "aircraft_id": aircraft_id,
                "document_id": document_id,
                "retrieved_chunks": len(chunks),
                "latency_ms": latency_ms,
            },
        }
