"""Build a candidate GraphRAG graph from existing Chroma chunks and curated relations.

Chroma is read-only. Output defaults to a separate candidate graph. Source evidence must
match the assigned chunk (whitespace/punctuation-insensitive) before a relation is accepted.
LLM fallback is opt-in and capped at 100 chunks.
"""
from __future__ import annotations
import argparse, json, hashlib, shutil, sys, re
from pathlib import Path
from datetime import datetime, timezone
import networkx as nx

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from GraphRAG.retrieval.chroma_reader import open_existing_collection, read_chunks
from GraphRAG.graph.relation_extractor import extract_relations
from GraphRAG.graph.graph_store import save_graph

def node_id(name: str) -> str:
    return hashlib.sha256(" ".join(name.casefold().split()).encode()).hexdigest()[:24]

def norm_evidence(value: str) -> str:
    """Normalize case and remove whitespace/punctuation for robust OCR line-wrap checks."""
    return re.sub(r"[^a-z0-9]+", "", str(value or "").casefold())

def evidence_matches(evidence: str, text: str) -> bool:
    ev, src = norm_evidence(evidence), norm_evidence(text)
    return bool(ev and src and ev in src)

def add_relation(g, r, *, evidence_validated: bool):
    s, o = str(r.get("subject") or "").strip(), str(r.get("object") or "").strip()
    if not s or not o or s.casefold() == o.casefold():
        return False
    a, b = node_id(s), node_id(o)
    for nid, nm in ((a, s), (b, o)):
        if not g.has_node(nid):
            g.add_node(nid, name=nm, canonical_name=" ".join(nm.casefold().split()),
                       entity_types=["relation_endpoint"])
    attrs = {k: r.get(k, "") for k in (
        "predicate", "evidence", "document_id", "aircraft_id", "chunk_id",
        "page", "section", "extraction_method", "qualifier"
    )}
    attrs["evidence_validated"] = bool(evidence_validated)
    g.add_edge(a, b, **attrs)
    return True

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="GraphRAG/storage/a320_ac_0624_graph_candidate.json")
    ap.add_argument("--limit", type=int, default=0, help="Optional chunk limit for pilot; 0 means all chunks")
    ap.add_argument("--llm-fallback", action="store_true", help="Enable LLM only for chunks with zero accepted deterministic/catalogue matches")
    ap.add_argument("--llm-budget", type=int, default=100)
    ap.add_argument("--catalogue", default="GraphRAG/catalogue/a320_curated_relations.json")
    args = ap.parse_args()
    if args.limit < 0:
        raise SystemExit("--limit must be >= 0")
    if args.llm_budget < 0 or args.llm_budget > 100:
        raise SystemExit("--llm-budget must be between 0 and 100")

    _, collection = open_existing_collection(project_root=PROJECT_ROOT)
    chunks = read_chunks(collection, aircraft_id="a320", document_id="a320_ac_0624")
    if args.limit:
        chunks = chunks[:args.limit]
    if not chunks:
        raise RuntimeError("No matching chunks; refusing to build empty graph")

    catalogue_path = (PROJECT_ROOT / args.catalogue).resolve()
    catalogue = json.loads(catalogue_path.read_text(encoding="utf-8"))
    g = nx.MultiDiGraph()
    reports = []
    accepted_catalogue = 0
    rejected_catalogue = 0
    accepted_rules = 0
    matched_chunk_ids = set()
    relation_keys = set()
    chunks_by_page = {}
    for c in chunks:
        chunks_by_page.setdefault(str(c.get("page") or ""), []).append(c)

    # Catalogue facts only accepted when exact normalized evidence occurs in a chunk on source_page.
    for r0 in catalogue.get("relations", []):
        r = dict(r0)
        page = str(r.get("source_page", ""))
        page_chunks = chunks_by_page.get(page, [])
        if not page_chunks:
            rejected_catalogue += 1
            reports.append({"status": "catalogue_rejected", "subject": r.get("subject"), "predicate": r.get("predicate"),
                            "object": r.get("object"), "page": page, "reason": "source_page_not_in_chunk_set"})
            continue
        evidence = str(r.get("evidence") or "")
        source_chunk = next((c for c in page_chunks if evidence_matches(evidence, c.get("text", ""))), None)
        if source_chunk is None:
            rejected_catalogue += 1
            reports.append({"status": "catalogue_rejected", "subject": r.get("subject"), "predicate": r.get("predicate"),
                            "object": r.get("object"), "page": page, "reason": "evidence_not_found_on_source_page"})
            continue
        r.update({
            "chunk_id": source_chunk.get("chunk_id", ""), "page": source_chunk.get("page", page),
            "document_id": r.get("document_id") or source_chunk.get("document_id"),
            "aircraft_id": r.get("aircraft_id") or source_chunk.get("aircraft_id"),
            "section": r.get("section") or source_chunk.get("section") or "",
            "extraction_method": "curated_pdf_catalogue_v1"
        })
        key = (r["subject"].casefold(), r["predicate"], r["object"].casefold())
        if key in relation_keys:
            reports.append({"status": "catalogue_duplicate", "subject": r["subject"], "predicate": r["predicate"], "object": r["object"], "page": page})
            continue
        if add_relation(g, r, evidence_validated=True):
            accepted_catalogue += 1
            relation_keys.add(key)
            matched_chunk_ids.add(str(source_chunk.get("chunk_id") or ""))

    fallback = []
    for i, c in enumerate(chunks):
        cid = str(c.get("chunk_id") or f"chunk_{i}")
        rels = extract_relations(str(c.get("text") or ""), chunk_id=cid,
                                 document_id=c.get("document_id"), aircraft_id=c.get("aircraft_id"),
                                 page=c.get("page"), section=c.get("section"))
        accepted_this_chunk = False
        for r in rels:
            if not evidence_matches(r.get("evidence", ""), c.get("text", "")):
                reports.append({"status": "rule_rejected", "chunk_id": cid, "reason": "evidence_not_found_in_chunk",
                                "subject": r.get("subject"), "predicate": r.get("predicate"), "object": r.get("object")})
                continue
            key = (r["subject"].casefold(), r["predicate"], r["object"].casefold())
            if key in relation_keys:
                continue
            if add_relation(g, r, evidence_validated=True):
                accepted_rules += 1
                relation_keys.add(key)
                matched_chunk_ids.add(cid)
                accepted_this_chunk = True
        if not accepted_this_chunk and cid not in matched_chunk_ids:
            fallback.append(c)

    llm_used = 0
    llm_failures = 0
    if args.llm_fallback and fallback and args.llm_budget:
        from GraphRAG.graph.llm_relation_extractor import OpenRouterRelationExtractor
        extractor = OpenRouterRelationExtractor()
        for c in fallback[:args.llm_budget]:
            llm_used += 1
            try:
                cid = str(c.get("chunk_id") or "")
                for r in extractor.extract(c):
                    r["extraction_method"] = "openrouter_llm_fallback_v1"
                    if not evidence_matches(r.get("evidence", ""), c.get("text", "")):
                        reports.append({"status": "llm_relation_rejected", "chunk_id": cid, "reason": "evidence_not_found_in_chunk",
                                        "subject": r.get("subject"), "predicate": r.get("predicate"), "object": r.get("object")})
                        continue
                    key = (r["subject"].casefold(), r["predicate"], r["object"].casefold())
                    if key not in relation_keys and add_relation(g, r, evidence_validated=True):
                        relation_keys.add(key)
            except Exception as e:
                llm_failures += 1
                reports.append({"chunk_id": c.get("chunk_id"), "status": "llm_failed", "error": str(e)[:300]})

    g.graph.update({
        "format": "aeromind_graphrag_v1", "aircraft_id": "a320", "document_id": "a320_ac_0624",
        "build_time_utc": datetime.now(timezone.utc).isoformat(),
        "catalogue_version": catalogue.get("catalogue_version"),
        "llm_fallback_enabled": args.llm_fallback, "llm_budget": args.llm_budget,
        "chunks_processed": len(chunks), "evidence_validation": "normalized_substring_v1"
    })
    output = (PROJECT_ROOT / args.output).resolve()
    canonical = (PROJECT_ROOT / "GraphRAG/storage/a320_ac_0624_graph.json").resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    if output == canonical and canonical.exists():
        backup = canonical.with_name(canonical.stem + ".pre_quality_fix_backup_" + datetime.now().strftime("%Y%m%d_%H%M%S") + canonical.suffix)
        shutil.copy2(canonical, backup)
        print("Backed up previous canonical graph:", backup)
    save_graph(g, output)
    report = {
        "chunks_processed": len(chunks),
        "catalogue_relations_accepted": accepted_catalogue,
        "catalogue_relations_rejected": rejected_catalogue,
        "rule_relations_added": accepted_rules,
        "total_nodes": g.number_of_nodes(), "total_edges": g.number_of_edges(),
        "llm_fallback_candidates": len(fallback), "llm_chunks_called": llm_used, "llm_failures": llm_failures,
        "llm_budget": args.llm_budget, "output": str(output),
        "evidence_validation": "normalized_substring_v1",
        "rejected_or_duplicate_records": len(reports),
        "report_records": reports,
        "notes": "Candidate build only. Evidence must match source chunks; review candidate edges before promotion."
    }
    report_path = output.with_suffix(".report.json")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "report_records"}, ensure_ascii=False, indent=2))
    print("Report saved:", report_path)

if __name__ == "__main__":
    main()
