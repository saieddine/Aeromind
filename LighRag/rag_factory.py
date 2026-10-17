import os
import re
import numpy as np
from pathlib import Path
from dotenv import load_dotenv
from openai import AsyncOpenAI


BASE = Path(__file__).resolve().parent.parent

# Load LightRAG-specific API configuration
load_dotenv(Path(__file__).resolve().parent / ".env")

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


async def llm_model_func(prompt, system_prompt=None, history_messages=None, **kwargs):
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.extend(history_messages or [])
    messages.append({"role": "user", "content": prompt})
    async with AsyncOpenAI(
        api_key=LLM_KEY, base_url=LLM_HOST, timeout=90, max_retries=5
    ) as client:
        request_kwargs = {
            "model": LLM_MODEL,
            "messages": messages,
            "max_tokens": 2000,
            "stream": False,
        }
        if kwargs.get("response_format") is not None:
            request_kwargs["response_format"] = kwargs["response_format"]
        resp = await client.chat.completions.create(**request_kwargs)

    choices = getattr(resp, "choices", None)
    if not choices:
        # Some compatible providers return an error body with HTTP 200.
        # Report only its code, never the raw response or credentials.
        extra = getattr(resp, "model_extra", None) or {}
        error = extra.get("error")
        code = error.get("code") if isinstance(error, dict) else None
        raise RuntimeError(
            f"LightRAG LLM '{LLM_MODEL}' returned no completion choices "
            f"(provider code: {code}). Check provider quota and model availability."
        )

    choice = choices[0]
    content = getattr(getattr(choice, "message", None), "content", None)
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError(
            f"LightRAG LLM '{LLM_MODEL}' returned empty answer content "
            f"(finish reason: {getattr(choice, 'finish_reason', None)}). "
            "Check the provider response and model output limit."
        )
    return content


async def embedding_func(texts: list[str]):
    client = AsyncOpenAI(api_key=EMBED_KEY, base_url=EMBED_HOST, timeout=90, max_retries=5)
    resp = await client.embeddings.create(model=EMBED_MODEL, input=texts)
    return np.array([d.embedding for d in resp.data], dtype=np.float32)


async def get_rag(aircraft_id: str) -> LightRAG:
    if not isinstance(aircraft_id, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", aircraft_id):
        raise ValueError("aircraft_id must be a canonical lowercase aircraft identifier.")
    required = {
        "LLM_MODEL": LLM_MODEL,
        "LLM_BINDING_HOST": LLM_HOST,
        "LLM_BINDING_API_KEY": LLM_KEY,
        "EMBEDDING_MODEL": EMBED_MODEL,
        "EMBEDDING_BINDING_HOST": EMBED_HOST,
        "EMBEDDING_BINDING_API_KEY": EMBED_KEY,
    }
    missing = [name for name, value in required.items() if not value or not value.strip()]
    if missing:
        raise RuntimeError("Missing LightRAG configuration: " + ", ".join(missing))
    if EMBED_DIM <= 0:
        raise RuntimeError("EMBEDDING_DIM must be positive.")
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
