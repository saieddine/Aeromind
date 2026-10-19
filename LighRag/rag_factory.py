
import os
import re
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from openai import AsyncOpenAI

from rag.ingestion.embedder_aeromind import generate_embedding

from lightrag import LightRAG
from lightrag.kg.shared_storage import initialize_pipeline_status
from lightrag.utils import EmbeddingFunc


# --------------------------------------------------
# Project paths
# --------------------------------------------------

BASE = Path(__file__).resolve().parent.parent
STORAGE = BASE / "rag_storage"

# Reuse AeroMind's existing root .env
load_dotenv(BASE / ".env")


# --------------------------------------------------
# OpenRouter configuration
# --------------------------------------------------

LLM_MODEL = os.getenv("OPENROUTER_MODEL")
LLM_KEY = os.getenv("OPENROUTER_API_KEY")
LLM_HOST = "https://openrouter.ai/api/v1"


# --------------------------------------------------
# Existing AeroMind embedding configuration
# --------------------------------------------------

EMBED_DIM = 384


# --------------------------------------------------
# LightRAG LLM function
# --------------------------------------------------

async def llm_model_func(
    prompt,
    system_prompt=None,
    history_messages=None,
    **kwargs,
):
    messages = []

    if system_prompt:
        messages.append(
            {
                "role": "system",
                "content": system_prompt,
            }
        )

    messages.extend(history_messages or [])

    messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    async with AsyncOpenAI(
        api_key=LLM_KEY,
        base_url=LLM_HOST,
        timeout=90,
        max_retries=3,
    ) as client:

        request_kwargs = {
            "model": LLM_MODEL,
            "messages": messages,
            "max_tokens": 2000,
            "stream": False,
        }

        # Preserve structured-output requests from LightRAG.
        if kwargs.get("response_format") is not None:
            request_kwargs["response_format"] = kwargs[
                "response_format"
            ]

        response = await client.chat.completions.create(
            **request_kwargs
        )

    if not response.choices:
        raise RuntimeError(
            "OpenRouter returned no completion choices. "
            f"Model={response.model!r}"
        )

    choice = response.choices[0]
    content = choice.message.content

    # Provide useful diagnostics instead of a generic error.
    if not isinstance(content, str) or not content.strip():
        reasoning = getattr(
            choice.message,
            "reasoning",
            None,
        )

        usage = response.usage
        completion_tokens = (
            getattr(usage, "completion_tokens", None)
            if usage is not None
            else None
        )

        raise RuntimeError(
            "OpenRouter returned no usable text. "
            f"Model={response.model!r}, "
            f"finish_reason={choice.finish_reason!r}, "
            f"reasoning_present={bool(reasoning)}, "
            f"completion_tokens={completion_tokens!r}"
        )

    return content


# --------------------------------------------------
# AeroMind embedding function
# --------------------------------------------------

async def embedding_func(texts: list[str]):
    # Reuse AeroMind's existing local BGE-small model.
    vectors = [
        generate_embedding(text)
        for text in texts
    ]

    embeddings = np.asarray(
        vectors,
        dtype=np.float32,
    )

    if (
        embeddings.ndim != 2
        or embeddings.shape[1] != EMBED_DIM
    ):
        raise RuntimeError(
            f"Expected embedding dimension {EMBED_DIM}, "
            f"received shape {embeddings.shape}."
        )

    return embeddings


# --------------------------------------------------
# LightRAG instance factory
# --------------------------------------------------

async def get_rag(aircraft_id: str) -> LightRAG:
    if not isinstance(aircraft_id, str) or not re.fullmatch(
        r"[a-z][a-z0-9_]*",
        aircraft_id,
    ):
        raise ValueError(
            "aircraft_id must be a canonical lowercase "
            "aircraft identifier."
        )

    if not LLM_MODEL or not LLM_MODEL.strip():
        raise RuntimeError(
            "OPENROUTER_MODEL is missing from the "
            "project root .env."
        )

    if not LLM_KEY or not LLM_KEY.strip():
        raise RuntimeError(
            "OPENROUTER_API_KEY is missing from the "
            "project root .env."
        )

    aircraft_storage = STORAGE / aircraft_id
    aircraft_storage.mkdir(
        parents=True,
        exist_ok=True,
    )

    rag = LightRAG(
        working_dir=str(aircraft_storage),
        llm_model_func=llm_model_func,
        llm_model_max_async=1,
        embedding_func=EmbeddingFunc(
            embedding_dim=EMBED_DIM,
            max_token_size=512,
            func=embedding_func,
        ),
    )

    await rag.initialize_storages()
    await initialize_pipeline_status()

    return rag
