import os
import re
import sys
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import chromadb

BASE = Path(__file__).resolve().parent.parent
load_dotenv(BASE / ".env")

client_embed = OpenAI(api_key=os.getenv("EMBEDDING_BINDING_API_KEY"), base_url=os.getenv("EMBEDDING_BINDING_HOST"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
chroma_client = chromadb.PersistentClient(path=str(BASE / "graph_storage" / "vectors"))

CHUNK_PATTERN = re.compile(
    r"\[([^|]+)\|\s*Section\s+([^|]+)\|\s*PDF page\s+(\d+)\]\s*\n(.*?)(?=\n\[|\Z)",
    re.DOTALL,
)


def build_vectors(aircraft_id: str, txt_name: str):
    text = (BASE / "data" / txt_name).read_text(encoding="utf-8")
    collection = chroma_client.get_or_create_collection(name=aircraft_id)

    ids, docs, metas = [], [], []
    for i, m in enumerate(CHUNK_PATTERN.finditer(text)):
        doc_label, section, page, body = m.groups()
        ids.append(f"{aircraft_id}_page_{page.strip()}")
        docs.append(body.strip())
        metas.append({"section": section.strip(), "page": page.strip()})

    batch = 20
    for i in range(0, len(docs), batch):
        chunk_ids, chunk_docs, chunk_metas = ids[i:i+batch], docs[i:i+batch], metas[i:i+batch]
        embeddings = [d.embedding for d in client_embed.embeddings.create(
            model=EMBEDDING_MODEL, input=chunk_docs
        ).data]
        collection.upsert(ids=chunk_ids, documents=chunk_docs, embeddings=embeddings, metadatas=chunk_metas)
        print(f"Embedded {i} to {i+len(chunk_docs)}")

    print(f"Done: {collection.count()} vectors stored for {aircraft_id}")


if __name__ == "__main__":
    build_vectors(sys.argv[1], sys.argv[2])