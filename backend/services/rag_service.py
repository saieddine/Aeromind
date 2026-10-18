from functools import lru_cache

from rag.retrieval.database_aeromind import collection
from rag.ingestion.embedder_aeromind import generate_embedding
from rag.retrieval.qa_retriever_aeromind import qa_retrieve
from rag.assistant.rag_service import RAGService


@lru_cache(maxsize=1)
def get_rag_service() -> RAGService:
    """Create one shared RAG service for the FastAPI process."""
    return RAGService(
        retriever=qa_retrieve,
        embedder=generate_embedding,
        collection=collection,
        top_k=5,
    )
