"""
============================================================
AeroMind Knowledge Store
============================================================

Current backend:
    ChromaDB

Purpose:
    Provide a clean storage boundary for the AI retrieval layer.

The rest of the AI system should interact with this module
rather than depending on Chroma configuration directly.

Future:
    The underlying storage can be changed or extended when
    the application/database layer is integrated.
"""

from pathlib import Path

import chromadb


# ============================================================
# CONFIGURATION
# ============================================================

CHROMA_PATH = Path("./chroma_storage")

# Collection used by AeroMind for aircraft-document chunks.

COLLECTION_NAME = "aeromind_knowledge"


# ============================================================
# CHROMA CLIENT
# ============================================================

client = chromadb.PersistentClient(
    path=str(CHROMA_PATH)
)


# ============================================================
# ACADEMIC KNOWLEDGE COLLECTION
# ============================================================

collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={
        "hnsw:space": "cosine"
    }
)


# ============================================================
# STORAGE OPERATIONS
# ============================================================

def store(
    ids,
    documents,
    embeddings,
    metadatas,
):
    """
    Store or update knowledge chunks.
    """

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    return collection.count()


def search(
    input_embedding,
    number=5,
):
    """
    Perform semantic search against the AeroMind
    knowledge collection.

    This is a low-level storage operation.
    Retrieval policies such as relevance thresholds
    belong to the retriever layer.
    """

    return collection.query(
        query_embeddings=[input_embedding],
        n_results=number,
    )


def get(
    where=None,
):
    """
    Retrieve stored knowledge records.

    Used when the system needs to inspect stored
    chunks rather than perform semantic search.
    """

    if where is None:
        return collection.get()

    return collection.get(
        where=where
    )


def count():
    """
    Return the number of stored knowledge chunks.
    """

    return collection.count()