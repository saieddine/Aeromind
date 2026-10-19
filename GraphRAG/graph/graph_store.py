"""Portable JSON persistence for a NetworkX MultiDiGraph."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict
import networkx as nx

FORMAT_VERSION = 1

def save_graph(graph: nx.MultiDiGraph, path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload: Dict[str, Any] = {
        "format_version": FORMAT_VERSION, "directed": True, "multigraph": True,
        "nodes": [{"id": node_id, **dict(attrs)} for node_id, attrs in graph.nodes(data=True)],
        "edges": [{"source": u, "target": v, "key": k, **dict(attrs)}
                  for u, v, k, attrs in graph.edges(keys=True, data=True)],
    }
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return target

def load_graph(path: str | Path) -> nx.MultiDiGraph:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("format_version") != FORMAT_VERSION:
        raise ValueError(f"Unsupported graph format version: {payload.get('format_version')}")
    graph = nx.MultiDiGraph()
    for item in payload.get("nodes", []):
        attrs = dict(item)
        node_id = attrs.pop("id")
        graph.add_node(node_id, **attrs)
    for item in payload.get("edges", []):
        attrs = dict(item)
        source, target = attrs.pop("source"), attrs.pop("target")
        key = attrs.pop("key", None)
        graph.add_edge(source, target, key=key, **attrs)
    return graph
