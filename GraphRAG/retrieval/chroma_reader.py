"""Read-only adapter for the existing AeroMind ChromaDB collection.

This module deliberately does not call upsert/delete or create a collection.
It resolves the project root from this file's location by default, so running
Python from another working directory does not silently select another DB.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import chromadb

DEFAULT_PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CHROMA_PATH = DEFAULT_PROJECT_ROOT / "chroma_storage"
DEFAULT_COLLECTION_NAME = "aeromind_knowledge"


def open_existing_collection(
    project_root: str | Path | None = None,
    collection_name: str = DEFAULT_COLLECTION_NAME,
):
    """Open an existing collection without creating it.

    Raises FileNotFoundError if the expected database directory is missing,
    and ValueError if the requested collection does not exist.
    """
    root = Path(project_root).resolve() if project_root else DEFAULT_PROJECT_ROOT
    chroma_path = root / "chroma_storage"

    if not chroma_path.is_dir():
        raise FileNotFoundError(
            f"ChromaDB directory not found: {chroma_path}. "
            "Pass the correct project_root; no database was created."
        )

    client = chromadb.PersistentClient(path=str(chroma_path))
    try:
        collection = client.get_collection(name=collection_name)
    except Exception as exc:
        # Chroma exception classes can vary by installed version. We re-raise
        # with a clearer message and never fall back to get_or_create_collection.
        raise ValueError(
            f"Existing Chroma collection '{collection_name}' was not found "
            f"under {chroma_path}. No collection was created."
        ) from exc

    return client, collection


def read_chunks(
    collection,
    *,
    aircraft_id: Optional[str] = None,
    document_id: Optional[str] = None,
    batch_size: int = 500,
) -> List[Dict[str, Any]]:
    """Read chunks and metadata without changing the collection.

    Returns chunk dictionaries compatible with graph_builder.build_graph().
    The Chroma record ID is preserved as chunk_id. Embeddings are intentionally
    not loaded because graph construction does not need them.
    """
    if batch_size < 1:
        raise ValueError("batch_size must be at least 1")

    where: Optional[Dict[str, Any]] = None
    filters = []
    if aircraft_id:
        filters.append({"aircraft_id": aircraft_id})
    if document_id:
        filters.append({"document_id": document_id})
    if len(filters) == 1:
        where = filters[0]
    elif len(filters) > 1:
        where = {"$and": filters}

    chunks: List[Dict[str, Any]] = []
    offset = 0

    while True:
        kwargs: Dict[str, Any] = {
            "limit": batch_size,
            "offset": offset,
            "include": ["documents", "metadatas"],
        }
        if where:
            kwargs["where"] = where

        result = collection.get(**kwargs)
        ids = result.get("ids") or []
        docs = result.get("documents") or []
        metadatas = result.get("metadatas") or []

        if not ids:
            break

        for i, chunk_id in enumerate(ids):
            metadata = metadatas[i] if i < len(metadatas) and metadatas[i] else {}
            text = docs[i] if i < len(docs) and docs[i] else ""
            chunks.append({
                "chunk_id": chunk_id,
                "text": text,
                "document_id": metadata.get("document_id"),
                "aircraft_id": metadata.get("aircraft_id"),
                "document": metadata.get("document"),
                "page": metadata.get("page"),
                "section": metadata.get("section"),
                "concept": metadata.get("concept"),
                "concept_index": metadata.get("concept_index"),
                "chunk_index": metadata.get("chunk_index"),
                "content_type": metadata.get("content_type"),
            })

        offset += len(ids)
        if len(ids) < batch_size:
            break

    return chunks
