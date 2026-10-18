"""
AeroMind concept-aware technical-document chunker.

Keeps the existing public interface and the current 500-word / 100-word
retrieval granularity, while making each chunk explicitly aware of the
technical-manual section/concept that owns it.

The chunker remains page-preserving so every chunk can still be traced to its
source PDF page. Section/concept context is added to the embedded text while
the original metadata is preserved.
"""


def _build_context_prefix(page):
    """Build context using only metadata already present on the page."""

    parts = []

    document = page.get("document")
    section = page.get("section")
    concept = page.get("concept")
    page_number = page.get("page")

    if document is not None:
        parts.append(f"Document: {document}")

    if section is not None:
        parts.append(f"Section: {section}")

    if concept is not None:
        parts.append(f"Concept: {concept}")

    if page_number is not None:
        parts.append(f"Page: {page_number}")

    return " | ".join(parts)


def _build_chunk_text(page, chunk_text):
    """Add available technical-document context to embedded chunk text."""

    prefix = _build_context_prefix(page)

    if not prefix:
        return chunk_text

    return f"{prefix}\n\n{chunk_text}"


def split_text_into_chunks(pages, chunk_size, overlap):
    """
    Split extracted document pages into overlapping text chunks.

    Each input page is expected to contain at least:
        {
            "text": "...",
            "page": 1
        }

    Additional metadata such as document_id, aircraft_id, document, section,
    concept, concept_index, and content_type is preserved when available.

    AeroMind technical-manual behavior:
    - preserves source-page boundaries;
    - preserves section/concept metadata;
    - adds section/concept/page context to embedded text;
    - keeps fixed-size word chunking and overlap;
    - never merges unrelated aircraft-manual sections.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap < 0:
        raise ValueError("overlap cannot be negative")

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks = []
    chunk_index = 0

    metadata_fields = [
        "document_id",
        "aircraft_id",
        "document",
        "section",
        "concept",
        "concept_index",
        "content_type",
    ]

    for page in pages:
        text = page.get("text", "")
        page_number = page.get("page")

        if not text:
            continue

        words = text.split()

        if not words:
            continue

        start_position = 0

        while start_position < len(words):
            end_position = start_position + chunk_size
            chunk_words = words[start_position:end_position]
            raw_chunk_text = " ".join(chunk_words)

            if not raw_chunk_text:
                break

            chunk = {
                "text": _build_chunk_text(page, raw_chunk_text),
                "page": page_number,
                "chunk_index": chunk_index,
            }

            for field in metadata_fields:
                if field in page and page[field] is not None:
                    chunk[field] = page[field]

            chunks.append(chunk)
            chunk_index += 1

            # Preserve the existing overlap behavior.
            next_start = end_position - overlap

            # Safety guard against a non-advancing loop.
            if next_start <= start_position:
                break

            start_position = next_start

    return chunks
