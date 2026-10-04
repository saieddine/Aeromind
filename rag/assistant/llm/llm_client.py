import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


class LLMClient:
    """
    Single LLM client used by AeroMind.

    OpenRouter is used as the LLM provider.

    Configuration is read from the .env file:
        OPENROUTER_API_KEY
        OPENROUTER_MODEL

    The API key must never be hard-coded in source code.
    """

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY", "").strip()

        self.model = os.getenv(
            "OPENROUTER_MODEL",
            "openai/gpt-5-mini",
        )

        if not self.api_key:
            raise RuntimeError(
                "OPENROUTER_API_KEY is not set. "
                "Add it to your .env file before starting AeroMind."
            )

        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
    ) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            temperature=temperature,
        )

        return response.choices[0].message.content.strip()


llm_client = LLMClient()