"""Read-only retrieval over AeroMind's persisted NetworkX graph."""
from __future__ import annotations
import json, re
from pathlib import Path
from typing import Any, Dict, List, Optional
import networkx as nx

def _tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", (text or "").casefold()) if len(t) > 1}

def _load_graph(path: Path) -> nx.MultiDiGraph:
    try:
        from GraphRAG.graph.graph_store import load_graph
        graph = load_graph(path)
        if graph is not None:
            return graph
    except (ImportError, AttributeError, TypeError, ValueError, KeyError):
        pass
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "nodes" in data and ("edges" in data or "links" in data):
        try:
            return nx.node_link_graph(data, directed=True, multigraph=True, edges="edges")
        except TypeError:
            return nx.node_link_graph(data, directed=True, multigraph=True)
    raise ValueError(f"Unsupported graph JSON format: {path}")

class GraphRetriever:
    """Loads graph once; returns matching relationships and source provenance."""
    def __init__(self, graph_path: str | Path, *, aircraft_id: Optional[str]="a320",
                 document_id: Optional[str]="a320_ac_0624", max_edges: int=12,
                 include_unvalidated: bool=False):
        self.graph_path = Path(graph_path)
        if not self.graph_path.is_file():
            raise FileNotFoundError(f"Graph not found: {self.graph_path}. Build it first.")
        self.graph = _load_graph(self.graph_path)
        self.aircraft_id, self.document_id = aircraft_id, document_id
        self.max_edges = max(1, int(max_edges))
        self.include_unvalidated = include_unvalidated

    def retrieve(self, question: str, top_k: Optional[int]=None) -> List[Dict[str, Any]]:
        q = _tokens(question)
        if not q: return []
        found = []
        for source, target, key, attrs in self.graph.edges(keys=True, data=True):
            if not self.include_unvalidated and attrs.get("evidence_validated") is not True: continue
            if self.aircraft_id and attrs.get("aircraft_id") not in (None, "", self.aircraft_id): continue
            if self.document_id and attrs.get("document_id") not in (None, "", self.document_id): continue
            sn = str(self.graph.nodes[source].get("name") or self.graph.nodes[source].get("canonical_name") or source)
            tn = str(self.graph.nodes[target].get("name") or self.graph.nodes[target].get("canonical_name") or target)
            pred, evidence = str(attrs.get("predicate") or ""), str(attrs.get("evidence") or "")
            overlap = len(q & _tokens(" ".join((sn, tn, pred.replace("_"," "), evidence))))
            entity_overlap = len(q & (_tokens(sn) | _tokens(tn)))
            if overlap == 0: continue
            found.append({"source_entity":sn,"target_entity":tn,"predicate":pred,"evidence":evidence,
                "document_id":attrs.get("document_id"),"aircraft_id":attrs.get("aircraft_id"),
                "document":attrs.get("document"),"section":attrs.get("section"),"page":attrs.get("page"),
                "chunk_id":attrs.get("chunk_id"),"extraction_method":attrs.get("extraction_method"),
                "evidence_validated":attrs.get("evidence_validated") is True,
                "score":2*entity_overlap+overlap/max(1,len(q)),"edge_id":str(key)})
        found.sort(key=lambda x:(x["score"],bool(x["evidence"])), reverse=True)
        results, seen = [], set()
        for item in found:
            k=(item["source_entity"].casefold().strip(),item["predicate"].casefold().strip(),item["target_entity"].casefold().strip())
            if k in seen: continue
            seen.add(k); results.append(item)
            if len(results) >= max(1,int(top_k or self.max_edges)): break
        return results
