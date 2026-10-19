# AeroMind GraphRAG QA starter

## Added files
- `GraphRAG/retrieval/graph_retriever.py`: loads the persisted graph once; retrieves graph relationships with provenance.
- `GraphRAG/retrieval/hybrid_retriever.py`: combines graph results with read-only Chroma vector retrieval.
- `GraphRAG/qa/__init__.py`
- `GraphRAG/qa/qa_service.py`: grounded prompt and one final `LLM.generate(prompt)` call.
- `GraphRAG/scripts/test_qa_service.py`: integration smoke-test template.

## Apply
1. Unzip at the AeroMind project root and merge the `GraphRAG` folder. Do not replace the whole existing folder.
2. Keep normal RAG, `rag/retrieval/database_aeromind.py`, `rag/assistant/rag_service.py`, the ingestion pipeline, and the existing LLM client unchanged.
3. Ensure the graph is saved at `GraphRAG/storage/a320_ac_0624_graph.json`.
4. Connect `embed_query()` in the test script to the exact existing BAAI/bge-small-en-v1.5 embedding implementation. It must return the same 384-dimensional query embedding used for Chroma indexing. The script deliberately raises `NotImplementedError` rather than guessing the embedder's API.
5. From project root run:
   `python -m py_compile GraphRAG/retrieval/graph_retriever.py GraphRAG/retrieval/hybrid_retriever.py GraphRAG/qa/qa_service.py GraphRAG/scripts/test_qa_service.py`
6. Once the embedder is connected, run `python GraphRAG/scripts/test_qa_service.py`.

## Notes
- Chroma is queried only; this package never creates or mutates the collection.
- The graph is loaded once, not rebuilt per question.
- Graph retrieval uses transparent lexical overlap as a first baseline, not semantic graph search.
- Edges lacking `evidence_validated=True` are excluded by default.
- Graph edges and original vector chunks are separately labeled in the prompt. Graph relationships are treated as retrieval hints, not stronger than the original manual passages.
- This is not yet wired to FastAPI. Integrate the API only after the smoke test passes.
- The LLM import path in the smoke test should be adjusted only if your actual checked-out branch uses a different path.
