# GraphRAG read-only Chroma adapter

Copy this `retrieval/` folder into the top-level `GraphRAG/` package created
in Phase 1.

The adapter expects this structure:

```text
AeroMind-Shared/
├── chroma_storage/
├── GraphRAG/
│   ├── graph/
│   └── retrieval/
└── rag/
```

`open_existing_collection()` resolves the database path relative to this
package's project root and calls `get_collection()`, never
`get_or_create_collection()`. It does not write to ChromaDB.

Example, from the `AeroMind-Shared` project root:

```python
from GraphRAG.retrieval.chroma_reader import open_existing_collection, read_chunks
from GraphRAG.graph.graph_builder import build_graph
from GraphRAG.graph.graph_store import save_graph

client, collection = open_existing_collection()
chunks = read_chunks(
    collection,
    aircraft_id="a320",
    document_id="a320_ac_0624",
)
graph = build_graph(chunks)
save_graph(graph, "GraphRAG/storage/a320_ac_0624_graph.json")
print("chunks:", len(chunks), "nodes:", graph.number_of_nodes(),
      "edges:", graph.number_of_edges())
```

Run the example only after confirming your existing collection contains the
expected aircraft/document metadata. The code only reads Chroma and writes a
separate JSON graph file.
