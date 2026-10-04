"""
AeroMind ingestion runner.

Run this file from the project root so that the `rag` package can be
imported correctly.

Flow:
    A320 PDF
        ↓
    ingestion/pipeline_aeromind.py
        ↓
    extraction → cleaning → concepts → chunks → embeddings
        ↓
    retrieval/database_aeromind.py
        ↓
    ChromaDB
"""

from pathlib import Path

from .pipeline_aeromind import process_pdf


# ---------------------------------------------------------------------
# AeroMind document configuration
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PDF_PATH = (
    PROJECT_ROOT
    / "data"
    / "documents"
    / "a320"
    / "AC_A320_0624.pdf"
)

AIRCRAFT_ID = "a320"
DOCUMENT_ID = "a320_ac_0624"


def main():
    """
    Run ingestion for the A320 technical document.
    """

    print("\n" + "=" * 70)
    print("AEROMIND INGESTION RUNNER")
    print("=" * 70)

    print("PDF:", PDF_PATH)
    print("Aircraft:", AIRCRAFT_ID)
    print("Document ID:", DOCUMENT_ID)

    if not PDF_PATH.exists():
        raise FileNotFoundError(
            f"A320 PDF not found:\n{PDF_PATH}"
        )

    result = process_pdf(
        input_pdf=PDF_PATH,
        aircraft_id=AIRCRAFT_ID,
        document_id=DOCUMENT_ID,
    )

    print("\n" + "=" * 70)
    print("RUNNER FINISHED")
    print("=" * 70)

    if result is None:
        print("Ingestion did not produce a stored result.")
    else:
        print("Ingestion completed successfully.")
        print("Stored result:", result)

    print("=" * 70)


if __name__ == "__main__":
    main()
