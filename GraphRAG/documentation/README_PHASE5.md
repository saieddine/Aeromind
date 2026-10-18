# AeroMind hybrid GraphRAG update

## Contents
- `GraphRAG/catalogue/a320_curated_relations.json`: curated seed relations transcribed from reviewed A320 PDF passages and selected diagram labels. This is explicitly a partial v1 catalogue, not an exhaustive annotation of all 427 pages.
- `GraphRAG/graph/relation_extractor.py`: expanded conservative sentence-local deterministic rules.
- `GraphRAG/scripts/build_graph_from_chroma.py`: candidate builder, defaults to a new output path, reads Chroma only, supports optional LLM fallback capped at 100 unique chunks.

## Install/update
Copy these files into the corresponding paths in your shared project. Back up existing files first. The script expects the existing `GraphRAG/retrieval/chroma_reader.py`, `GraphRAG/graph/graph_store.py`, and `GraphRAG/graph/llm_relation_extractor.py` to remain present.

## Deterministic-only pilot
From the shared project root:
```powershell
python GraphRAG/scripts/build_graph_from_chroma.py --limit 50
```
This writes `GraphRAG/storage/a320_ac_0624_graph_candidate.json` and a `.report.json`; it does not overwrite the canonical graph.

## Full deterministic + curated candidate
```powershell
python GraphRAG/scripts/build_graph_from_chroma.py
```

## Optional LLM fallback, maximum 100 chunks
```powershell
python GraphRAG/scripts/build_graph_from_chroma.py --llm-fallback --llm-budget 100
```
Only chunks with no curated/rule-based match are eligible. This is a conservative first policy; later we can improve partial coverage detection.

## Important limitations
1. Catalogue is not exhaustive across the whole PDF; it contains reviewed seed facts from landing gear, exterior lighting, APU, and selected engine danger-area diagrams. Extend it section by section with exact evidence and source pages.
2. Exact quote validation proves only that text exists, not that a relation is interpreted correctly. Review the report and edges before promotion.
3. LLM fallback currently uses the existing extractor and may fail on models that do not return JSON; failures are logged, not fatal.
