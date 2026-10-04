from functools import lru_cache

from rag.database_aeromind import collection
from rag.embedder_aeromind import generate_embedding
from rag.qa_retriever_aeromind import qa_retrieve
from rag.rag_service import RAGService


@lru_cache(maxsize=1)
def get_rag_service() -> RAGService:
    """
    Create one shared RAGService for the FastAPI process.
    """

    return RAGService(
        retriever=qa_retrieve,
        embedder=generate_embedding,
        collection=collection,
        top_k=5,
    )
