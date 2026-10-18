from rag.ingestion.embedder_aeromind import generate_embedding
from rag.retrieval.database_aeromind import collection
from rag.retrieval.qa_retriever_aeromind import qa_retrieve


AIRCRAFT_ID = "a320"
DOCUMENT_ID = "a320_ac_0624"

QUESTION = "What is the maximum aircraft length?"


def main():
    print("\n" + "=" * 70)
    print("AEROMIND RETRIEVAL TEST")
    print("=" * 70)

    print("Question:")
    print(QUESTION)

    print("\nGenerating question embedding...")
    question_embedding = generate_embedding(QUESTION)

    print("Embedding generated.")
    print("Embedding dimensions:", len(question_embedding))

    print("\nSearching ChromaDB...")

    results = qa_retrieve(
        collection=collection,
        aircraft_id=AIRCRAFT_ID,
        document_id=DOCUMENT_ID,
        query=QUESTION,
        question_embedding=question_embedding,
        top_k=5,
    )

    print("\n" + "=" * 70)
    print("RETRIEVAL RESULTS")
    print("=" * 70)

    if not results:
        print("No relevant chunks were found.")
        return

    print("Results found:", len(results))

    for i, result in enumerate(results, start=1):
        print("\n" + "-" * 70)
        print(f"RESULT {i}")
        print("-" * 70)

        print("Chunk ID:", result.get("chunk_id"))
        print("Page:", result.get("page"))
        print("Concept:", result.get("concept"))
        print("Section:", result.get("section"))
        print("Distance:", result.get("distance"))

        if "lexical_score" in result:
            print("Lexical score:", result.get("lexical_score"))

        if "fallback_score" in result:
            print("Fallback score:", result.get("fallback_score"))

        print("\nTEXT:")
        print(result.get("text", ""))

    print("\n" + "=" * 70)
    print("RETRIEVAL TEST FINISHED")
    print("=" * 70)


if __name__ == "__main__":
    main()