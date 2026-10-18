# AeroMind GraphRAG Phase 4 — Relation extractor update

## What changed
- Adds explicit patterns for `consists_of`, `includes`, `comprises`, `located_in`,
  `equipped_with`, `connected_to`, `supplied_by`, and `mounted_on`.
- Trims long heading-plus-sentence prefixes and explanatory clauses to reduce
  oversized graph endpoints.
- Keeps evidence text and document/aircraft/page/section/chunk provenance.
- Does not create edges from co-occurrence alone.
- Does not change ChromaDB, the original RAG pipeline, or the existing graph builder.

## Apply
1. Back up `AeroMind-Shared/GraphRAG/graph/relation_extractor.py`.
2. Replace only that file with the one in this package.
3. From the project root, run:
   `python GraphRAG/scripts/build_graph_from_chroma.py`
4. Then run:
   `python GraphRAG/scripts/inspect_graph.py`

The build script will overwrite the GraphRAG JSON output file, not ChromaDB.
If you want to preserve the current graph snapshot, copy
`GraphRAG/storage/a320_ac_0624_graph.json` somewhere safe before rebuilding.

## Important validation
The new rules are still heuristic, not a validated aircraft ontology. Review the
sample evidence for every edge before using graph relationships in answers. A
higher edge count alone is not proof of better quality.
