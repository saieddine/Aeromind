# AeroMind GraphRAG — LLM relation extraction

## What this adds
- An OpenRouter-powered relation extractor with aircraft-manual-specific prompts.
- Strict JSON output and validation that quoted evidence occurs verbatim in the source chunk.
- Provenance for document, aircraft, page, section, chunk, extraction method, and condition/qualifier.
- Checkpointing during long runs and timestamped archival of the previous graph before replacing it.
- Reads existing Chroma chunks only. It does not write to Chroma or modify normal RAG.

## Before running
1. Ensure the shared project root contains `.env` with:
   `OPENROUTER_API_KEY=...`
   `OPENROUTER_MODEL=...`
2. Install dependencies in the project's active environment:
   `pip install openai python-dotenv networkx chromadb`
3. Put these files in the existing `AeroMind-Shared/GraphRAG/` directory, preserving the folder structure.
4. Test only 20 chunks first:
   `python GraphRAG/scripts/build_graph_with_llm.py --limit 20 --output GraphRAG/storage/a320_llm_pilot.json`
   Review the pilot graph before the full build. This custom output path does not replace the canonical graph.
5. If pilot results are good, build the full canonical graph:
   `python GraphRAG/scripts/build_graph_with_llm.py`

## Persistence and correction policy
- The canonical graph is saved to `GraphRAG/storage/a320_ac_0624_graph.json`.
- Before replacement, the old graph is copied to `GraphRAG/storage/archive/` with a timestamp. Never delete the archive casually.
- A successful build replaces the canonical graph with only the new LLM-extracted edges; legacy rule-generated false positives do not carry over.
- If the extraction run yields zero edges, the canonical graph is not replaced.
- Checkpoint is temporary and removed after successful completion.

## Prompt design
The system prompt explicitly targets A320 technical manuals. It instructs the model to ignore OCR/diagram debris and headers, require explicit support, preserve variant/condition, return concise endpoints, and quote exact evidence. The source chunk and metadata are supplied separately.

## Important limitations
Exact quote matching proves only that the evidence exists in the chunk; it does not prove that the relation interpretation is correct. Review a pilot graph and sampled evidence before using it to answer safety-critical aircraft questions. Keep a separate reviewed/approved graph if this becomes a production safety tool.
