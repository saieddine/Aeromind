# AeroMind GraphRAG — Phase 1

This is a starter for graph construction only. It does not alter normal RAG or
integrate with the API yet.

Install the dependency:

```bash
pip install networkx
```

Modules:
- `graph/entity_extractor.py`: conservative candidate entity extraction.
- `graph/relation_extractor.py`: limited explicit relation patterns with evidence.
- `graph/graph_builder.py`: builds a `networkx.MultiDiGraph` from chunk dictionaries.
- `graph/graph_store.py`: JSON graph persistence.

The relation rules are intentionally narrow. A graph with few edges is better
than fabricated relationships. Inspect extracted edges against the source PDF.

The next phase should read existing Chroma records with real chunk IDs and
metadata, then pass them to `build_graph()`. Do not rerun ingestion through the
current shared Chroma configuration until storage paths are explicitly checked.
