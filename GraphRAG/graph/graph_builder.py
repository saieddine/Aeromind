"""Build a provenance-preserving directed graph from existing chunks."""
from __future__ import annotations
import hashlib
from typing import Any, Dict, Iterable
import networkx as nx
from .entity_extractor import extract_entities
from .relation_extractor import extract_relations

def _node_id(name: str) -> str:
    normalized = " ".join(name.casefold().split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:24]

def build_graph(chunks: Iterable[Dict[str, Any]]) -> nx.MultiDiGraph:
    """Build graph from chunk dictionaries; never infer edges from co-occurrence."""
    graph = nx.MultiDiGraph()
    for index, chunk in enumerate(chunks):
        text = str(chunk.get("text") or "").strip()
        if not text:
            continue
        chunk_id = str(chunk.get("chunk_id") or f"chunk_{index}")
        document_id, aircraft_id = chunk.get("document_id"), chunk.get("aircraft_id")
        page, section = chunk.get("page"), chunk.get("section")
        for entity in extract_entities(text):
            node_id = _node_id(entity["canonical_name"])
            if graph.has_node(node_id):
                types = set(graph.nodes[node_id].get("entity_types", []))
                types.add(entity["entity_type"])
                graph.nodes[node_id]["entity_types"] = sorted(types)
            else:
                graph.add_node(node_id, name=entity["name"],
                               canonical_name=entity["canonical_name"],
                               entity_types=[entity["entity_type"]])
        for rel in extract_relations(text, chunk_id=chunk_id, document_id=document_id,
                                     aircraft_id=aircraft_id, page=page, section=section):
            source, target = _node_id(rel["subject"]), _node_id(rel["object"])
            for node_id, name in ((source, rel["subject"]), (target, rel["object"])):
                if not graph.has_node(node_id):
                    graph.add_node(node_id, name=name,
                                   canonical_name=" ".join(name.casefold().split()),
                                   entity_types=["relation_endpoint"])
            graph.add_edge(source, target, predicate=rel["predicate"],
                           evidence=rel["evidence"], document_id=rel["document_id"] or "",
                           aircraft_id=rel["aircraft_id"] or "", chunk_id=rel["chunk_id"],
                           page=str(rel["page"]) if rel["page"] is not None else "",
                           section=rel["section"] or "",
                           extraction_method=rel["extraction_method"])
    graph.graph["format"] = "aeromind_graphrag_v1"
    graph.graph["entity_count"] = graph.number_of_nodes()
    graph.graph["relationship_count"] = graph.number_of_edges()
    return graph
