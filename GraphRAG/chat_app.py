"""Standalone local chat UI for AeroMind GraphRAG.

Run from the AeroMind-Shared project root:
    streamlit run GraphRAG/chat_app.py
"""
from pathlib import Path
import sys
import uuid

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from GraphRAG.retrieval.chroma_reader import open_existing_collection
from GraphRAG.retrieval.graph_retriever import GraphRetriever
from GraphRAG.retrieval.hybrid_retriever import HybridRetriever
from GraphRAG.qa.qa_service import GraphRAGQAService
from rag.assistant.llm.llm_client import LLM
from rag.ingestion.embedder_aeromind import generate_embedding


GRAPH_PATH = PROJECT_ROOT / "GraphRAG" / "storage" / "a320_ac_0624_graph.json"


@st.cache_resource(show_spinner="Connecting to AeroMind's existing GraphRAG components...")
def create_qa_service():
    """Initialize read-only retrieval and reuse AeroMind's existing models."""
    if not GRAPH_PATH.exists():
        raise FileNotFoundError(
            f"Graph file not found: {GRAPH_PATH}\n"
            "Build the graph first or update GRAPH_PATH to your saved graph."
        )

    _, collection = open_existing_collection(project_root=PROJECT_ROOT)
    graph = GraphRetriever(
        GRAPH_PATH,
        aircraft_id="a320",
        document_id="a320_ac_0624",
    )
    hybrid = HybridRetriever(
        graph,
        collection,
        generate_embedding,
        aircraft_id="a320",
        document_id="a320_ac_0624",
    )
    return GraphRAGQAService(hybrid, LLM(), aircraft_id="a320")


def start_new_chat():
    st.session_state.messages = []
    st.session_state.conversation_id = str(uuid.uuid4())


st.set_page_config(
    page_title="AeroMind GraphRAG Chat",
    page_icon="✈️",
    layout="centered",
)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = str(uuid.uuid4())

with st.sidebar:
    st.title("✈️ AeroMind")
    st.caption("Standalone GraphRAG chat")
    st.write("Aircraft: **A320**")
    if st.button("＋ New conversation", use_container_width=True):
        start_new_chat()
        st.rerun()
    st.divider()
    st.caption("This local interface uses the existing GraphRAG index, ChromaDB collection, embedding model, and LLM client.")
    st.caption("It does not connect to or modify the main AeroMind backend.")

st.title("AeroMind Assistant")
st.caption("Ask questions about the A320 technical documentation.")

# Render existing conversation as ordinary user/assistant messages.
for index, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and message.get("sources"):
            with st.expander(f"Sources ({len(message['sources'])})"):
                for source in message["sources"]:
                    document = source.get("document") or source.get("document_id") or "Document"
                    page = source.get("page") or "Unknown"
                    section = source.get("section") or "Unknown section"
                    st.markdown(f"- **{document}** — page {page} — section {section}")
                    excerpt = source.get("excerpt")
                    if excerpt:
                        st.caption(excerpt)

question = st.chat_input("Ask a question about the A320...")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            service = create_qa_service()
            # Pass prior turns only. The current question is passed separately.
            history = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in st.session_state.messages[:-1]
                if msg["role"] in ("user", "assistant")
            ]
            with st.spinner("Searching the aircraft documents and preparing an answer..."):
                result = service.answer(
                    question,
                    conversation_id=st.session_state.conversation_id,
                    conversation_history=history,
                )
            answer = result.get("answer", "The assistant returned no answer.")
            st.markdown(answer)
            sources = result.get("sources", [])
            if sources:
                with st.expander(f"Sources ({len(sources)})"):
                    for source in sources:
                        document = source.get("document") or source.get("document_id") or "Document"
                        page = source.get("page") or "Unknown"
                        section = source.get("section") or "Unknown section"
                        st.markdown(f"- **{document}** — page {page} — section {section}")
                        excerpt = source.get("excerpt")
                        if excerpt:
                            st.caption(excerpt)

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": sources,
            })
        except Exception as exc:
            error_message = (
                f"Sorry, I couldn't complete that request.\n\n"
                f"**Error:** `{type(exc).__name__}: {exc}`"
            )
            st.error(error_message)
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_message,
                "sources": [],
            })
