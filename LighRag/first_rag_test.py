import os
import asyncio
from dotenv import load_dotenv

from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import openai_complete_if_cache
from lightrag.llm.openai import openai_embed
from lightrag.utils import EmbeddingFunc


load_dotenv()


# ----------------------------------------
# LLM: Gemini through OpenRouter
# ----------------------------------------

async def llm_model_func(
    prompt,
    system_prompt=None,
    history_messages=None,
    **kwargs
):
    kwargs["max_tokens"] = 1000

    return await openai_complete_if_cache(
        model=os.getenv("LLM_MODEL"),
        prompt=prompt,
        system_prompt=system_prompt,
        history_messages=history_messages or [],
        api_key=os.getenv("LLM_BINDING_API_KEY"),
        base_url=os.getenv("LLM_BINDING_HOST"),
        **kwargs
    )


# ----------------------------------------
# Embeddings through OpenRouter
# ----------------------------------------

async def embedding_func(texts):
    return await openai_embed(
        texts,
        model=os.getenv("EMBEDDING_MODEL"),
        api_key=os.getenv("EMBEDDING_BINDING_API_KEY"),
        base_url=os.getenv("EMBEDDING_BINDING_HOST"),
    )


# ----------------------------------------
# Main
# ----------------------------------------

async def main():

    rag = LightRAG(
        working_dir="./rag_storage",
        llm_model_func=llm_model_func,
        embedding_func=EmbeddingFunc(
            embedding_dim=int(os.getenv("EMBEDDING_DIM")),
            max_token_size=8192,
            func=embedding_func,
        ),
    )

    await rag.initialize_storages()

    # ----------------------------------------
    # Tiny test document
    # ----------------------------------------

    text = """
    The Airbus A320 aircraft uses hydraulic systems
    to provide power to several important aircraft systems.

    Hydraulic power is used for flight controls,
    landing gear, brakes, and other aircraft functions.

    The hydraulic systems allow these components
    to operate using hydraulic pressure.
    """

    print("Inserting test document...")

    await rag.ainsert(text)

    print("Document inserted successfully!")

    # ----------------------------------------
    # Ask a question
    # ----------------------------------------

    question = "What are hydraulic systems used for on the Airbus A320?"

    print("\nQuestion:")
    print(question)

    response = await rag.aquery(
        question,
        param=QueryParam(mode="hybrid")
    )

    print("\nAnswer:")
    print(response)


if __name__ == "__main__":
    asyncio.run(main())