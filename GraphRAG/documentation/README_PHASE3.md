# GraphRAG Phase 3 — build graph from Chroma

The database read test found 449 records for the A320 document.

Copy `scripts/` into your existing `GraphRAG/` folder without overwriting
existing files. From the `AeroMind-Shared` root run:

```powershell
python GraphRAG/scripts/build_graph_from_chroma.py
```

This reads existing Chroma records and writes a separate JSON graph at
`GraphRAG/storage/a320_ac_0624_graph.json`. It does not write to Chroma or
rerun PDF ingestion.

Then inspect the graph:

```powershell
python GraphRAG/scripts/inspect_graph.py
```

Relationships are rule-based candidates. Verify their source evidence, page,
and chunk ID against the PDF before relying on them.
