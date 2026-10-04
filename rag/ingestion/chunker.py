def split_text_into_chunks(pages, chunk_size, overlap):
    """
    Split extracted document pages into overlapping text chunks.

    Each input page is expected to contain at least:
        {
            "text": "...",
            "page": 1
        }

    Additional metadata such as document_id, aircraft_id, section,
    concept, and content_type is preserved when available.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap < 0:
        raise ValueError("overlap cannot be negative")

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks = []
    chunk_index = 0

    for page in pages:
        text = page.get("text", "")
        page_number = page.get("page")

        if not text:
            continue

        words = text.split()
        start_position = 0

        while start_position < len(words):
            end_position = start_position + chunk_size
            chunk_words = words[start_position:end_position]
            chunk_text = " ".join(chunk_words)

            if not chunk_text:
                break

            chunk = {
                "text": chunk_text,
                "page": page_number,
                "chunk_index": chunk_index,
            }

            metadata_fields = [
                "document_id",
                "aircraft_id",
                "document",
                "section",
                "concept",
                "concept_index",
                "content_type",
            ]

            for field in metadata_fields:
                if field in page and page[field] is not None:
                    chunk[field] = page[field]

            chunks.append(chunk)
            chunk_index += 1
            start_position = end_position - overlap

    return chunks
