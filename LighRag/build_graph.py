import re
import json
import sys
from pathlib import Path
import networkx as nx

BASE = Path(__file__).resolve().parent.parent  # Airbus folder
GRAPH_DIR = BASE / "graph_storage"

# Your project's canonical component vocabulary — extend as needed
KNOWN_COMPONENTS = [
    "fuselage", "cockpit", "left wing", "right wing", "engine 1", "engine 2",
    "landing gear", "tail", "hydraulic system", "pack", "zone controller",
    "pressurization", "outflow valve", "reservoir", "accumulator",
    "ground service", "access door",
]

CHUNK_PATTERN = re.compile(
    r"\[([^|]+)\|\s*Section\s+([^|]+)\|\s*PDF page\s+(\d+)\]\s*\n(.*?)(?=\n\[|\Z)",
    re.DOTALL,
)


def extract_concepts(text: str) -> list[str]:
    """Deterministic concept extraction: known-component matching + capitalized multi-word phrases."""
    found = set()
    lower = text.lower()
    for comp in KNOWN_COMPONENTS:
        if comp in lower:
            found.add(comp.title())
    # Capitalized multi-word technical terms, e.g. "Pack Flow Control Valve"
    for match in re.findall(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4})\b", text):
        if len(match.split()) >= 2:
            found.add(match)
    return list(found)


def build_graph(aircraft_id: str, txt_name: str):
    text = (BASE / "data" / txt_name).read_text(encoding="utf-8")
    G = nx.DiGraph()

    G.add_node(aircraft_id, type="aircraft")
    doc_id = f"{aircraft_id}_{txt_name}"
    G.add_node(doc_id, type="document", name=txt_name)
    G.add_edge(aircraft_id, doc_id, relation="has_document")

    chunk_count = 0
    for m in CHUNK_PATTERN.finditer(text):
        doc_label, section, page, body = m.groups()
        section = section.strip()
        page = page.strip()
        chunk_count += 1

        section_id = f"{aircraft_id}_section_{section}"
        if section_id not in G:
            G.add_node(section_id, type="section", name=section)
            G.add_edge(doc_id, section_id, relation="contains")

        page_id = f"{aircraft_id}_page_{page}"
        G.add_node(page_id, type="page", number=page, text=body.strip()[:2000])
        G.add_edge(section_id, page_id, relation="contains")

        concepts = extract_concepts(body)
        for concept in concepts:
            concept_id = f"{aircraft_id}_concept_{concept.lower().replace(' ', '_')}"
            if concept_id not in G:
                G.add_node(concept_id, type="concept", name=concept)
            G.add_edge(concept_id, page_id, relation="appears_on")
            G.add_edge(concept_id, aircraft_id, relation="belongs_to")

        # Co-occurrence: concepts on the same page are related
        for i, c1 in enumerate(concepts):
            for c2 in concepts[i+1:]:
                id1 = f"{aircraft_id}_concept_{c1.lower().replace(' ', '_')}"
                id2 = f"{aircraft_id}_concept_{c2.lower().replace(' ', '_')}"
                G.add_edge(id1, id2, relation="related_to")

    GRAPH_DIR.mkdir(exist_ok=True)
    out_path = GRAPH_DIR / f"{aircraft_id}.graphml"
    nx.write_graphml(G, out_path)
    print(f"Built graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges from {chunk_count} chunks")
    print(f"Saved to {out_path}")


if __name__ == "__main__":
    build_graph(sys.argv[1], sys.argv[2])