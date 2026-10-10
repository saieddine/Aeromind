"""AeroMind QA retrieval.

Retrieves relevant chunks from the aircraft knowledge base using:
1. strict semantic search scoped to an aircraft and document;
2. a lexical/semantic fallback when strict retrieval is insufficient.

This module contains retrieval policy. ChromaDB storage remains in
retrieval.database.
"""

import math

from .retrieval_utils_aeromind import (
    lexical_coverage,
    calculate_fallback_score,
    get_important_tokens,
    normalize_text
)

# ==================================================
# THRESHOLDS
# ==================================================

MAX_DISTANCE = 0.35

FALLBACK_MAX_DISTANCE = 0.50
FALLBACK_MIN_LEXICAL = 0.75


# ==================================================
# CONCEPT HINTS
# ==================================================

CONCEPT_HINTS = {
    "General Aircraft Dimensions": {
        "dimensions",
        "dimension",
        "wingspan",
        "wing span",
        "aircraft length",
        "overall length",
        "aircraft height",
        "overall height",
        "aircraft width",
        "overall width",
        "length of the aircraft",
        "height of the aircraft",
        "width of the aircraft",
    }
}


def get_concept_hint_score(query, concept):
    """
    Returns a concept relevance score between 0.0 and 1.0.

    This is intentionally conservative: it only boosts a concept
    when the user's question contains terminology strongly associated
    with that concept.
    """

    if not concept:
        return 0.0

    normalized_query = normalize_text(query)

    hints = CONCEPT_HINTS.get(concept, set())

    if not hints:
        return 0.0

    for hint in hints:
        if hint in normalized_query:
            return 1.0

    return 0.0


# ==================================================
# COSINE DISTANCE
# ==================================================

def cosine_distance(vector_a, vector_b):

    dot_product = sum(
        float(a) * float(b)
        for a, b in zip(vector_a, vector_b)
    )

    magnitude_a = math.sqrt(
        sum(float(a) * float(a) for a in vector_a)
    )

    magnitude_b = math.sqrt(
        sum(float(b) * float(b) for b in vector_b)
    )

    if magnitude_a == 0 or magnitude_b == 0:
        return 1.0

    similarity = dot_product / (magnitude_a * magnitude_b)

    return 1.0 - similarity


# ==================================================
# QA RETRIEVAL
# ==================================================

def qa_retrieve(
    collection,
    aircraft_id,
    document_id,
    query,
    question_embedding,
    top_k=5
):
    """
    AeroMind Retrieval Contract (v1)

    Public parameters:
        aircraft_id
        document_id
        query
        top_k

    Internal dependency:
        collection
        question_embedding

    NOTE:
        collection and question_embedding are temporary
        infrastructure dependencies until retrieval_service.py
        centralizes Chroma and embeddings.
    """

    # --------------------------------------------------
    # 1. STRICT SEMANTIC SEARCH
    # --------------------------------------------------

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=max(top_k * 4, 20),
        where={
            "$and": [
                {"aircraft_id": aircraft_id},
                {"document_id": document_id},
                
            ]
        }
    )

    chunks = []

    ids = results["ids"][0]
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for i in range(len(ids)):

        metadata = metadatas[i]

        chunk = {

            "chunk_id": ids[i],
            "text": documents[i],
            "page": metadata.get("page"),
            "aircraft_id": metadata.get("aircraft_id"),
            "document_id": metadata.get("document_id"),
            "concept": metadata.get("concept"),
            "document": metadata.get("document"),
            "section": metadata.get("section"),
            "concept_index": metadata.get("concept_index"),
            "chunk_index": metadata.get("chunk_index"),
            "content_type": metadata.get("content_type"),
            "distance": distances[i],
            "concept_hint_score": get_concept_hint_score(
                query,
                metadata.get("concept")
            )

        }

        chunks.append(chunk)

    # --------------------------------------------------
    # 2. NO RESULTS
    # --------------------------------------------------

    if not chunks:
        return []

    # --------------------------------------------------
    # 3. STRICT FILTER
    # --------------------------------------------------

    strict_chunks = []

    for chunk in chunks:

        if chunk["distance"] <= MAX_DISTANCE:

            semantic_score = 1.0 - chunk["distance"]

            lexical_score = lexical_coverage(
                query,
                chunk["text"]
            )

            concept_score = chunk["concept_hint_score"]

            final_score = (
                semantic_score * 0.55
                + lexical_score * 0.15
                + concept_score * 0.30
            )

            chunk["lexical_score"] = lexical_score
            chunk["final_score"] = final_score

            strict_chunks.append(chunk)

    strict_chunks.sort(
        key=lambda chunk: chunk["final_score"],
        reverse=True
    )

    # --------------------------------------------------
    # 4. STRICT SEARCH WORKED
    # --------------------------------------------------

    if strict_chunks:
        return strict_chunks[:top_k]

    # --------------------------------------------------
    # 5. STRICT FAILED
    # --------------------------------------------------

    return fallback_retrieve(
        collection=collection,
        query=query,
        question_embedding=question_embedding,
        aircraft_id=aircraft_id,
        document_id=document_id,
        top_k=top_k
    )


# ==================================================
# REAL FALLBACK RETRIEVAL
# ==================================================

def fallback_retrieve(
    collection,
    query,
    question_embedding,
    aircraft_id,
    document_id,
    top_k=5
):

    # --------------------------------------------------
    # 1. GET ALL CONCEPT CHUNKS
    # --------------------------------------------------

    results = collection.get(
        where={
            "$and": [
                {"aircraft_id": aircraft_id},
                {"document_id": document_id},
            ]
        },
        include=[
            "documents",
            "metadatas",
            "embeddings"
        ]
    )

    ids = results["ids"]
    documents = results["documents"]
    metadatas = results["metadatas"]
    embeddings = results["embeddings"]

    if not ids:
        return []

    candidates = []

    # --------------------------------------------------
    # PREPARE QUESTION TOKENS
    # --------------------------------------------------

    important_tokens = get_important_tokens(query)

    important_phrase = " ".join(important_tokens)

    # --------------------------------------------------
    # 2. CHECK EVERY CHUNK
    # --------------------------------------------------

    for i in range(len(ids)):

        document = documents[i]
        metadata = metadatas[i]
        stored_embedding = embeddings[i]

        # ----------------------------------------------
        # LEXICAL SCORE
        # ----------------------------------------------

        lexical_score = lexical_coverage(query, document)

        # ----------------------------------------------
        # SKIP ZERO MATCHES
        # ----------------------------------------------

        if lexical_score == 0:
            continue

        # ----------------------------------------------
        # SEMANTIC DISTANCE
        # ----------------------------------------------

        distance = cosine_distance(
            question_embedding,
            stored_embedding
        )

        # ----------------------------------------------
        # PHRASE MATCH
        # ----------------------------------------------

        candidate_normalized = normalize_text(document)

        phrase_match = (
            len(important_tokens) > 1
            and important_phrase in candidate_normalized
        )

        # ----------------------------------------------
        # RELEVANCE RULES
        # ----------------------------------------------

        strong_phrase_match = phrase_match

        reasonable_mixed_match = (
            lexical_score >= FALLBACK_MIN_LEXICAL
            and distance <= FALLBACK_MAX_DISTANCE
        )

        if not (
            strong_phrase_match
            or reasonable_mixed_match
        ):
            continue

        # ----------------------------------------------
        # FALLBACK SCORE
        # ----------------------------------------------

        fallback_score = calculate_fallback_score(
            distance,
            lexical_score
        )

        concept_hint_score = get_concept_hint_score(
            query,
            metadata.get("concept")
        )

        final_score = (
            fallback_score * 0.70
            + concept_hint_score * 0.30
        )

        # ----------------------------------------------
        # BUILD CANDIDATE
        # ----------------------------------------------

        candidate = {

            "chunk_id": ids[i],
            "text": document,
            "page": metadata.get("page"),
            "aircraft_id": metadata.get("aircraft_id"),
            "document_id": metadata.get("document_id"),
            "concept": metadata.get("concept"),
            "document": metadata.get("document"),
            "section": metadata.get("section"),
            "concept_index": metadata.get("concept_index"),
            "chunk_index": metadata.get("chunk_index"),
            "content_type": metadata.get("content_type"),
            "distance": distance,
            "lexical_score": lexical_score,
            "fallback_score": fallback_score,
            "concept_hint_score": concept_hint_score,
            "final_score": final_score

        }

        candidates.append(candidate)

    # --------------------------------------------------
    # 3. NOTHING FOUND
    # --------------------------------------------------

    if not candidates:
        return []

    # --------------------------------------------------
    # 4. SORT BEST → WORST
    # --------------------------------------------------

    candidates.sort(
        key=lambda candidate: candidate["final_score"],
        reverse=True
    )

    # --------------------------------------------------
    # 5. RETURN TOP K
    # --------------------------------------------------

    return candidates[:top_k]