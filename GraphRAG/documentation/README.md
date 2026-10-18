# AeroMind GraphRAG FastAPI integration

## Files
- `backend/services/graphrag_service.py` — cached GraphRAG initialization and response adapter.
- `backend/routes/chat.py` — updated `/api/chat` method selection for `rag` and `graphrag`.

## Apply
Copy these files into the matching paths in the AeroMind-Shared project. Keep the existing
`backend/services/rag_service.py`, `backend/schemas/chat.py`, `main.py`, and normal RAG files unchanged.

Current GraphRAG configuration:
- aircraft ID: `a320`
- document ID: `a320_ac_0624`
- Chroma collection: `aeromind_knowledge`
- graph file: `GraphRAG/storage/a320_ac_0624_graph.json`

The integration does not create or modify the Chroma collection and does not rebuild the graph.
It preserves the existing response schema. The route continues to pass an empty conversation
history, matching current backend behavior; persistence/history is not added by this patch.

## Test
From the AeroMind-Shared project root, start the API with your existing command and send:

POST `/api/chat`
```json
{
  "aircraft_id": "a320",
  "question": "What are the dimensions of the A320?",
  "method": "graphrag"
}
```

Repeat with `"method": "rag"` to verify normal RAG still works.
