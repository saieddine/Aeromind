"""Integration smoke-test template; wire embed_query to the existing embedding implementation."""
from pathlib import Path
import sys
PROJECT_ROOT=Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path: sys.path.insert(0,str(PROJECT_ROOT))
from GraphRAG.retrieval.chroma_reader import open_existing_collection
from GraphRAG.retrieval.graph_retriever import GraphRetriever
from GraphRAG.retrieval.hybrid_retriever import HybridRetriever
from GraphRAG.qa.qa_service import GraphRAGQAService
from rag.assistant.llm.llm_client import LLM
from rag.ingestion.embedder_aeromind import generate_embedding

GRAPH_PATH=PROJECT_ROOT/"GraphRAG"/"storage"/"a320_ac_0624_graph.json"

def embed_query(question: str):
    """Use AeroMind's existing embedding model for query-time retrieval."""
    return generate_embedding(question)

def main():
    _,collection=open_existing_collection(project_root=PROJECT_ROOT)
    graph=GraphRetriever(GRAPH_PATH,aircraft_id="a320",document_id="a320_ac_0624")
    hybrid=HybridRetriever(graph,collection,embed_query,aircraft_id="a320",document_id="a320_ac_0624")
    service=GraphRAGQAService(hybrid,LLM(),aircraft_id="a320")
    result=service.answer("How is the nose landing gear retracted?")
    print("\n--- RETRIEVAL DEBUG ---")
    print(result.get("debug_retrieval", result.get("retrieval", "No debug data returned")))

    print("\n--- SOURCES ---")
    for source in result.get("sources", []):
            print(source)
    print(result["answer"])
    for source in result["sources"]:
        print(f'- {source["document"]} | page {source["page"]} | {source["chunk_id"]}')

if __name__=="__main__": main()
