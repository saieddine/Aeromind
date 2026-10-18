"""AeroMind PDF ingestion pipeline.

Converts an aircraft technical PDF into structured, searchable knowledge:

PDF → extraction → cleaning → structure/concept detection → page assignment
→ chunking → embeddings → ChromaDB.

This version removes NPU course/lesson assumptions and stores aircraft and
document identifiers in chunk metadata for AeroMind retrieval.
"""

from pathlib import Path

from .bidaya import text_extractor
from .clean_aeromind import clean_text
from .chunker import split_text_into_chunks
from .embedder_aeromind import generate_embedding

from .concept_detector_aeromind import (
    find_structure_pages,
    extract_structure_candidates,
    find_numbered_headings,
    build_concepts,
    build_fallback_concepts,
    merge_and_order_concepts,
    assign_concepts_to_pages,
)

from ..retrieval.database_aeromind import store


def process_pdf(
    input_pdf,
    aircraft_id,
    document_id=None,
):
    """
    Unified AeroMind aircraft-document ingestion pipeline.

    Converts a PDF into structured, searchable knowledge:

        PDF
        ↓
        extraction
        ↓
        cleaning
        ↓
        structure detection
        ↓
        numbered concepts
        ↓
        semantic fallback concepts
        ↓
        concept merge/order
        ↓
        page-level concept assignment
        ↓
        chunking
        ↓
        embeddings
        ↓
        ChromaDB

    The resulting knowledge base is shared by AeroMind retrieval methods.
    """

    # ======================================================
    # 1. PREPARE PDF
    # ======================================================

    pdf_path = Path(input_pdf)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    if not pdf_path.is_file():
        raise ValueError(
            f"Path is not a file: {pdf_path}"
        )

    document_name = pdf_path.name

    print("\n" + "=" * 70)
    print("STARTING PDF INGESTION")
    print("=" * 70)
    print("PDF:", pdf_path)
    print("Aircraft:", aircraft_id)
    print("Document ID:", document_id or document_name)

    # ======================================================
    # 2. EXTRACT PDF
    # ======================================================

    print("\n[1] Extracting PDF...")

    pages = text_extractor(
        pdf_path
    )

    if pages is None:
        print("Extraction failed.")
        return None

    if not pages:
        print("Extraction returned no pages.")
        return None

    print(
        "Pages extracted:",
        len(pages)
    )

    # ======================================================
    # 3. CLEAN PDF
    # ======================================================

    print("\n[2] Cleaning text...")

    cleaned_pages = clean_text(
        pages
    )

    if not cleaned_pages:
        print("Cleaning produced no pages.")
        return None

    print(
        "Pages after cleaning:",
        len(cleaned_pages)
    )

    # ======================================================
    # 4. STRUCTURE DETECTION
    # ======================================================
    #
    # This is mainly diagnostic information.
    # The final concept list is produced by:
    #
    #   numbered concepts
    #   +
    #   semantic fallback concepts
    #
    # and then merged below.
    # ======================================================

    print("\n[3] Detecting document structure...")

    structure_pages = (
        find_structure_pages(
            cleaned_pages
        )
    )

    structure_candidates = (
        extract_structure_candidates(
            structure_pages
        )
    )

    print(
        "Structure pages:",
        len(structure_pages)
    )

    print(
        "Structure candidates:",
        len(structure_candidates)
    )

    # ======================================================
    # 5. NUMBERED CONCEPT DETECTION
    # ======================================================

    print(
        "\n[4] Detecting numbered concepts..."
    )

    numbered_headings = (
        find_numbered_headings(
            cleaned_pages
        )
    )

    numbered_concepts = (
        build_concepts(
            numbered_headings
        )
    )

    print(
        "Numbered concepts:",
        len(numbered_concepts)
    )

    # ======================================================
    # 6. SEMANTIC FALLBACK CONCEPT DETECTION
    # ======================================================
    #
    # Uses:
    #
    #   layout_detector.py
    #   semantic_boundary.py
    #
    # to detect concept boundaries where numbered
    # headings are unavailable.
    # ======================================================

    print(
        "\n[5] Detecting semantic fallback concepts..."
    )

    fallback_concepts = (
        build_fallback_concepts(
            pages=cleaned_pages,
            numbered_concepts=numbered_concepts,
            pdf_path=pdf_path,
        )
    )

    print(
        "Fallback concepts:",
        len(fallback_concepts)
    )

    # ======================================================
    # 7. MERGE + ORDER CONCEPTS
    # ======================================================

    print(
        "\n[6] Merging and ordering concepts..."
    )

    concepts = (
        merge_and_order_concepts(
            numbered_concepts=numbered_concepts,
            fallback_concepts=fallback_concepts,
        )
    )

    print(
        "Final concept count:",
        len(concepts)
    )

    # ======================================================
    # 8. PRINT FINAL CONCEPT MAP
    # ======================================================

    print("\n" + "=" * 70)
    print("FINAL CONCEPT MAP")
    print("=" * 70)

    for concept in concepts:
        concept_type = (
            "FALLBACK"
            if concept.get(
                "is_fallback",
                False,
            )
            else "NUMBERED"
        )

        print(
            f"{concept['concept_index']:>3} "
            f"→ PAGE {concept['pages'][0]:>3} "
            f"→ {concept['concept']} "
            f"[{concept_type}]"
        )

    # ======================================================
    # 9. ASSIGN CONCEPTS TO ALL PAGES
    # ======================================================

    print(
        "\n[7] Assigning concepts to pages..."
    )

    pages_with_concepts = (
        assign_concepts_to_pages(
            cleaned_pages,
            concepts,
        )
    )

    if not pages_with_concepts:
        print(
            "Concept assignment produced no pages."
        )
        return None

    # ======================================================
    # 10. CHUNKING
    # ======================================================
    #
    # Keep the project's existing chunking configuration:
    #
    #   chunk size = 500 words
    #   overlap    = 100 words
    #
    # We are intentionally not changing retrieval
    # granularity until we have evidence from testing.
    # ======================================================

    print(
        "\n[8] Splitting pages into chunks..."
    )

    chunks = split_text_into_chunks(
        pages_with_concepts,
        500,
        100,
    )

    if not chunks:
        print("No chunks were created.")
        return None

    print(
        "Chunks created:",
        len(chunks)
    )

    # ======================================================
    # 11. PREPARE CHROMA DATA
    # ======================================================

    print(
        "\n[9] Preparing embeddings and metadata..."
    )

    ids = []
    documents = []
    metadatas = []
    embeddings = []

    # ======================================================
    # 12. PROCESS EACH CHUNK
    # ======================================================

    for chunk_number, chunk in enumerate(
        chunks
    ):
        chunk_text = chunk.get(
            "text",
            "",
        ).strip()

        if not chunk_text:
            continue

        # --------------------------------------------------
        # DOCUMENT
        # --------------------------------------------------

        documents.append(
            chunk_text
        )

        # --------------------------------------------------
        # CHUNK INDEX
        # --------------------------------------------------

        chunk_index = chunk.get(
            "chunk_index",
            chunk_number,
        )

        # --------------------------------------------------
        # CHUNK ID
        # --------------------------------------------------

        chunk_id = (
            f"{pdf_path.stem}"
            f"_chunk_"
            f"{chunk_index}"
        )

        ids.append(
            chunk_id
        )

        # --------------------------------------------------
        # EMBEDDING
        # --------------------------------------------------

        embeddings.append(
            generate_embedding(
                chunk_text
            )
        )

        # --------------------------------------------------
        # BASE METADATA
        # --------------------------------------------------

        metadata = {
            "document": document_name,
            "document_id": document_id or pdf_path.stem,
            "aircraft_id": aircraft_id,
            "page": chunk.get("page"),
            "chunk_index": chunk_index,
            "content_type": chunk.get(
                "content_type"
            ),
        }

        # --------------------------------------------------
        # OPTIONAL CONCEPT
        # --------------------------------------------------

        concept = chunk.get(
            "concept"
        )

        if concept is not None:
            metadata["concept"] = concept

        # --------------------------------------------------
        # OPTIONAL SECTION
        # --------------------------------------------------

        section = chunk.get(
            "section"
        )

        if section is not None:
            metadata["section"] = section

        # --------------------------------------------------
        # OPTIONAL CONCEPT INDEX
        # --------------------------------------------------

        concept_index = chunk.get(
            "concept_index"
        )

        if concept_index is not None:
            metadata["concept_index"] = (
                concept_index
            )

        metadatas.append(
            metadata
        )

    # ======================================================
    # 13. VALIDATE STORAGE DATA
    # ======================================================

    if not documents:
        print(
            "No valid chunk documents were produced."
        )
        return None

    if not (
        len(ids)
        == len(documents)
        == len(metadatas)
        == len(embeddings)
    ):
        raise RuntimeError(
            "Chroma data arrays have mismatched lengths."
        )

    print(
        "Valid chunks prepared:",
        len(documents)
    )

    # ======================================================
    # 14. STORE IN CHROMA
    # ======================================================

    print(
        "\n[10] Storing in ChromaDB..."
    )

    storing = store(
        ids,
        documents,
        embeddings,
        metadatas,
    )

    # ======================================================
    # 15. SUMMARY
    # ======================================================

    print("\n" + "=" * 70)
    print("INGESTION COMPLETE")
    print("=" * 70)

    print(
        "Document:",
        document_name
    )

    print(
        "Aircraft:",
        aircraft_id
    )

    print(
        "Document ID:",
        document_id or pdf_path.stem
    )

    print(
        "Pages:",
        len(cleaned_pages)
    )

    print(
        "Numbered concepts:",
        len(numbered_concepts)
    )

    print(
        "Fallback concepts:",
        len(fallback_concepts)
    )

    print(
        "Final concepts:",
        len(concepts)
    )

    print(
        "Chunks:",
        len(documents)
    )

    print("=" * 70)

    return storing