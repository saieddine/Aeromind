"""Build an LLM-extracted, evidence-validated graph from existing Chroma chunks.

Run from the shared project root:
  python GraphRAG/scripts/build_graph_with_llm.py
Optional:
  --limit 25       process only first N chunks (pilot/test)
  --no-archive     do not archive the current graph before replacing it
  --output PATH   custom output JSON path
This script reads Chroma only; it never modifies the original RAG collection.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass

from GraphRAG.retrieval.chroma_reader import open_existing_collection, read_chunks
from GraphRAG.graph.graph_store import save_graph
from GraphRAG.graph.llm_relation_extractor import OpenRouterRelationExtractor
import networkx as nx


def node_id(name: str) -> str:
    return hashlib.sha256(" ".join(name.casefold().split()).encode("utf-8")).hexdigest()[:24]


def build_llm_graph(chunks, extractor, checkpoint_path: Path):
    graph = nx.MultiDiGraph()
    graph.graph.update({
        "format": "aeromind_graphrag_llm_v1",
        "extraction_model": extractor.model,
        "extraction_method": "openrouter_llm_v1",
        "source_of_truth": "existing Chroma chunk text",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
    })
    errors = 0
    total_relations = 0
    for i, chunk in enumerate(chunks, start=1):
        try:
            relations = extractor.extract(chunk)
        except Exception as exc:
            errors += 1
            print(f"[WARN] chunk {i}/{len(chunks)} failed ({chunk.get('chunk_id')}): {exc}")
            continue
        for rel in relations:
            src, dst = node_id(rel["subject"]), node_id(rel["object"])
            if not graph.has_node(src):
                graph.add_node(src, name=rel["subject"], canonical_name=" ".join(rel["subject"].casefold().split()))
            if not graph.has_node(dst):
                graph.add_node(dst, name=rel["object"], canonical_name=" ".join(rel["object"].casefold().split()))
            graph.add_edge(
                src, dst, predicate=rel["predicate"], evidence=rel["evidence"],
                qualifier=rel["qualifier"], document_id=rel.get("document_id") or "",
                aircraft_id=rel.get("aircraft_id") or "", chunk_id=rel.get("chunk_id") or "",
                page=str(rel["page"]) if rel.get("page") is not None else "",
                section=rel.get("section") or "", extraction_method=rel["extraction_method"],
                evidence_validated=True,
            )
            total_relations += 1
        if i % 10 == 0 or i == len(chunks):
            print(f"Processed {i}/{len(chunks)} chunks; validated relationships: {total_relations}; failures: {errors}")
            # Save checkpoint outside the canonical graph path to prevent losing progress.
            save_graph(graph, checkpoint_path)
    graph.graph["entity_count"] = graph.number_of_nodes()
    graph.graph["relationship_count"] = graph.number_of_edges()
    graph.graph["chunks_processed"] = len(chunks)
    graph.graph["chunk_failures"] = errors
    return graph


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="only process first N chunks; 0 means all")
    parser.add_argument("--no-archive", action="store_true", help="do not archive current graph")
    parser.add_argument("--output", default="", help="optional output path relative to project root or absolute")
    args = parser.parse_args()

    client, collection = open_existing_collection(project_root=PROJECT_ROOT)
    print("Read-only Chroma collection:", collection.name, "| records:", collection.count())
    chunks = read_chunks(collection, aircraft_id="a320", document_id="a320_ac_0624")
    if args.limit > 0:
        chunks = chunks[:args.limit]
    if not chunks:
        raise RuntimeError("No matching chunks found; refusing to build an empty graph.")
    extractor = OpenRouterRelationExtractor()
    out = Path(args.output) if args.output else PROJECT_ROOT / "GraphRAG" / "storage" / "a320_ac_0624_graph.json"
    if not out.is_absolute():
        out = PROJECT_ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)

    # Preserve the legacy graph before the first LLM replacement. Subsequent
    # canonical builds are also timestamp-archived, so history is never lost.
    if out.exists() and not args.no_archive:
        archive_dir = PROJECT_ROOT / "GraphRAG" / "storage" / "archive"
        archive_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_path = archive_dir / f"{out.stem}_{stamp}_pre_llm.json"
        shutil.copy2(out, archive_path)
        print("Archived previous graph:", archive_path)

    checkpoint = out.with_name(out.stem + "_checkpoint.json")
    graph = build_llm_graph(chunks, extractor, checkpoint)
    if graph.number_of_edges() == 0:
        raise RuntimeError("No validated relationships extracted. Canonical graph was not replaced.")
    save_graph(graph, out)
    try:
        checkpoint.unlink(missing_ok=True)
    except OSError:
        pass
    print("\nLLM graph build complete.")
    print("Chunks processed:", len(chunks))
    print("Nodes:", graph.number_of_nodes())
    print("Validated edges:", graph.number_of_edges())
    print("Model:", extractor.model)
    print("Saved:", out)
    print("Note: evidence validation checks exact source text, not factual correctness; review samples before production use.")


if __name__ == "__main__":
    main()
