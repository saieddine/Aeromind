import os
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import chromadb
import networkx as nx

BASE = Path(__file__).resolve().parent.parent
load_dotenv(BASE / ".env")

client_embed = OpenAI(api_key=os.getenv("EMBEDDING_BINDING_API_KEY"), base_url=os.getenv("EMBEDDING_BINDING_HOST"))
client_llm = OpenAI(api_key=os.getenv("LLM_BINDING_API_KEY"), base_url=os.getenv("LLM_BINDING_HOST"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
LLM_MODEL = os.getenv("LLM_MODEL")

chroma_client = chromadb.PersistentClient(path=str(BASE / "graph_storage" / "vectors"))
_graphs = {}


def _load_graph(aircraft_id: str):
    if aircraft_id not in _graphs:
        path = BASE / "graph_storage" / f"{aircraft_id}.graphml"
        _graphs[aircraft_id] = nx.read_graphml(path)
    return _graphs[aircraft_id]


def _graph_lookup(aircraft_id: str, query: str, limit=5):
    """No LLM: just substring-match the question against concept node names."""
    G = _load_graph(aircraft_id)
    q_lower = query.lower()
    matched_pages = set()
    for node, data in G.nodes(data=True):
        if data.get("type") == "concept" and data.get("name", "").lower() in q_lower:
            for neighbor in G.successors(node):
                if G.nodes[neighbor].get("type") == "page":
                    matched_pages.add(G.nodes[neighbor].get("text", ""))
            for related in G.successors(node):
                if G.edges[node, related].get("relation") == "related_to":
                    for n2 in G.successors(related):
                        if G.nodes.get(n2, {}).get("type") == "page":
                            matched_pages.add(G.nodes[n2].get("text", ""))
    return list(matched_pages)[:limit]


def ask(aircraft_id: str, question: str, conversation_id: str, top_k=4):
    start = time.time()
    collection = chroma_client.get_or_create_collection(name=aircraft_id)

    # Vector retrieval (embedding call only, not generative)
    q_embedding = client_embed.embeddings.create(model=EMBEDDING_MODEL, input=[question]).data[0].embedding
    vec_results = collection.query(query_embeddings=[q_embedding], n_results=top_k)
    vec_chunks = vec_results["documents"][0]
    vec_metas = vec_results["metadatas"][0]

    # Graph retrieval (zero LLM calls, deterministic lookup)
    graph_chunks = _graph_lookup(aircraft_id, question)

    combined = vec_chunks + [c for c in graph_chunks if c not in vec_chunks]
    context = "\n\n---\n\n".join(combined)

    # ONE LLM call — final answer generation only
    prompt = f"""Answer the question using only the context below. If the context doesn't contain the answer, say so clearly.

Context:
{context}

Question: {question}"""
    resp = client_llm.chat.completions.create(
        model=LLM_MODEL, messages=[{"role": "user", "content": prompt}], max_tokens=2000,
    )
    answer = resp.choices[0].message.content

    sources = [{"title": f"A320 AC — Section {m.get('section','?')}, p.{m.get('page','?')}"} for m in vec_metas]

    return {
        "answer": answer,
        "sources": sources,
        "metadata": {
            "method": "lightrag",
            "latency_ms": int((time.time() - start) * 1000),
        },
    }


if __name__ == "__main__":
    question = input("Ask a question about the A320: ")
    result = ask("a320", question, "conversation_001")
    print(json.dumps(result, indent=2))