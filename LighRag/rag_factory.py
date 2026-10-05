import os
import numpy as np
from pathlib import Path
from dotenv import load_dotenv
from openai import AsyncOpenAI

BASE = Path(__file__).resolve().parent.parent
load_dotenv(BASE / ".env")
STORAGE = BASE / "rag_storage"

LLM_MODEL = os.getenv("LLM_MODEL")
LLM_HOST = os.getenv("LLM_BINDING_HOST")
LLM_KEY = os.getenv("LLM_BINDING_API_KEY")

EMBED_MODEL = os.getenv("EMBEDDING_MODEL")
EMBED_HOST = os.getenv("EMBEDDING_BINDING_HOST")
EMBED_KEY = os.getenv("EMBEDDING_BINDING_API_KEY")
EMBED_DIM = int(os.getenv("EMBEDDING_DIM", "1536"))

from lightrag import LightRAG
from lightrag.kg.shared_storage import initialize_pipeline_status
from lightrag.utils import EmbeddingFunc


async def llm_model_func(prompt, system_prompt=None, history_messages=[], **kwargs):
    client = AsyncOpenAI(api_key=LLM_KEY, base_url=LLM_HOST, timeout=90, max_retries=5)
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.extend(history_messages)
    messages.append({"role": "user", "content": prompt})
    resp = await client.chat.completions.create(
        model=LLM_MODEL, messages=messages, max_tokens=2000
    )
    return resp.choices[0].message.content


async def embedding_func(texts: list[str]):
    client = AsyncOpenAI(api_key=EMBED_KEY, base_url=EMBED_HOST, timeout=90, max_retries=5)
    resp = await client.embeddings.create(model=EMBED_MODEL, input=texts)
    return np.array([d.embedding for d in resp.data], dtype=np.float32)


async def get_rag(aircraft_id: str) -> LightRAG:
    rag = LightRAG(
        working_dir=str(STORAGE / aircraft_id),
        llm_model_func=llm_model_func,
        llm_model_max_async=1,       # lower concurrency = fewer simultaneous connections = more stable on flaky networks
        embedding_func=EmbeddingFunc(
            embedding_dim=EMBED_DIM,
            max_token_size=8192,
            func=embedding_func,
        ),
    )
    await rag.initialize_storages()
    await initialize_pipeline_status()
    return rag