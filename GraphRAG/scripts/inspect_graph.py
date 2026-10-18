"""Inspect the saved graph; run from project root."""
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from GraphRAG.graph.graph_store import load_graph


def main():
    path = PROJECT_ROOT / "GraphRAG" / "storage" / "a320_ac_0624_graph.json"
    if not path.is_file():
        raise FileNotFoundError(f"Graph not found: {path}. Build it first.")
    graph = load_graph(path)
    print("Graph:", path)
    print("Nodes:", graph.number_of_nodes())
    print("Edges:", graph.number_of_edges())
    if graph.number_of_edges() == 0:
        print("No relationships extracted. Review extraction rules and source text.")
        return
    for i, (source, target, attrs) in enumerate(graph.edges(data=True)):
        print(f"{graph.nodes[source].get('name')} --[{attrs.get('predicate')}]--> {graph.nodes[target].get('name')}")
        print(f"  document={attrs.get('document_id')} page={attrs.get('page')} section={attrs.get('section')} chunk={attrs.get('chunk_id')}")
        print(f"  evidence={attrs.get('evidence')}")
        if i >= 19:
            print("Showing first 20 edges.")
            break


if __name__ == "__main__":
    main()
