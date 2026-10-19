"""AeroMind semantic boundary detection utilities.

Uses the AeroMind embedding model to compare candidate page titles,
page bodies, and the currently active concept. The resulting signals help
concept_detector.py decide whether a page starts a new technical concept
or continues the previous one.
"""

import math

from rag.ingestion.embedder_aeromind import generate_embedding


# --------------------------------------------------
# V1 THRESHOLDS
# --------------------------------------------------

STRONG_BOUNDARY_GAP = 0.10

HIGH_TITLE_CONCEPT_SIMILARITY = 0.75

LOW_TITLE_CONCEPT_SIMILARITY = 0.70

MIN_TITLE_BODY_SIMILARITY = 0.75


# --------------------------------------------------
# COSINE SIMILARITY
# --------------------------------------------------

def cosine_similarity(
    vector_a,
    vector_b
):

    dot_product = sum(
        a * b
        for a, b in zip(
            vector_a,
            vector_b
        )
    )

    magnitude_a = math.sqrt(
        sum(
            a * a
            for a in vector_a
        )
    )

    magnitude_b = math.sqrt(
        sum(
            b * b
            for b in vector_b
        )
    )

    if (
        magnitude_a == 0
        or magnitude_b == 0
    ):
        return 0.0

    return (
        dot_product
        / (
            magnitude_a
            * magnitude_b
        )
    )


# --------------------------------------------------
# TEXT ↔ TEXT SIMILARITY
# --------------------------------------------------

def semantic_similarity(
    text_a,
    text_b
):

    if not text_a or not text_b:
        return None

    embedding_a = generate_embedding(
        text_a
    )

    embedding_b = generate_embedding(
        text_b
    )

    return cosine_similarity(
        embedding_a,
        embedding_b
    )


# --------------------------------------------------
# CALCULATE 3 SIGNALS
# --------------------------------------------------

def calculate_boundary_signals(
    title,
    body,
    current_concept_title,
    current_concept_prototype
):

    # Signal 1:
    # Does the title describe its own page?
    title_body = semantic_similarity(
        title,
        body
    )

    # Signal 2:
    # Does the page continue the old concept?
    continuity = semantic_similarity(
        body,
        current_concept_prototype
    )

    # Signal 3:
    # Is the candidate title basically
    # a subtopic/name variation of the old concept?
    title_concept = semantic_similarity(
        title,
        current_concept_title
    )

    return {
        "title_body": title_body,
        "continuity": continuity,
        "title_concept": title_concept
    }


# --------------------------------------------------
# DECIDE NEW CONCEPT OR CONTINUATION
# --------------------------------------------------

def starts_new_concept(
    title_body,
    continuity,
    title_concept
):

    if (
        title_body is None
        or continuity is None
        or title_concept is None
    ):
        return None


    boundary_gap = (
        title_body
        - continuity
    )


    # --------------------------------------------------
    # STRONG NEW CONCEPT
    # --------------------------------------------------

    if (
        boundary_gap
        >= STRONG_BOUNDARY_GAP
    ):
        return True


    # --------------------------------------------------
    # STRONG CONTINUATION
    # --------------------------------------------------

    if (
        boundary_gap
        <= -STRONG_BOUNDARY_GAP
    ):
        return False


    # --------------------------------------------------
    # UNCERTAIN ZONE
    # --------------------------------------------------

    # Candidate title is strongly related
    # to current concept.
    #
    # Example:
    # "this and super in Method References"
    # vs
    # "Method References"
    #
    # → continuation

    if (
        title_concept
        >= HIGH_TITLE_CONCEPT_SIMILARITY
    ):
        return False


    # Candidate title is different from
    # current concept, but strongly explains
    # its own page.
    #
    # Example:
    # "Private Interface Methods"
    # vs
    # "Resolving Default Method Conflicts"
    #
    # → new concept

    if (
        title_concept
        <= LOW_TITLE_CONCEPT_SIMILARITY
        and
        title_body
        >= MIN_TITLE_BODY_SIMILARITY
    ):
        return True


    # --------------------------------------------------
    # STILL UNCERTAIN
    # --------------------------------------------------

    return None