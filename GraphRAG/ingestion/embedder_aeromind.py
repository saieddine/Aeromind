"""AeroMind text embedding utilities.

This module converts document chunks and user queries into dense vectors
for semantic retrieval in the AeroMind RAG pipeline.

The embedding model is kept compatible with the existing NPU RAG
implementation while remaining independent of NPU-specific concepts.
"""

from sentence_transformers import SentenceTransformer


# BGE-small is suitable for English technical-document retrieval.
# The model is loaded once and reused for all embedding requests.
MODEL_NAME = "BAAI/bge-small-en-v1.5"

model = SentenceTransformer(
    MODEL_NAME,
    local_files_only=True,
)


def generate_embedding(text):
    """
    Generate a normalized embedding vector for a text string.

    Normalization is useful because AeroMind's vector database uses
    cosine similarity/distance for semantic retrieval.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    text = text.strip()

    if not text:
        raise ValueError("text cannot be empty")

    embedding = model.encode(
        text,
        normalize_embeddings=True,
    )

    return embedding.tolist()
