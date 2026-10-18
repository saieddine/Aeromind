"""OpenRouter LLM client for AeroMind."""

import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


class LLM:
    """Small OpenAI-compatible client for OpenRouter."""

    def __init__(self):
        api_key = os.getenv("OPENROUTER_API_KEY")
        model = os.getenv("OPENROUTER_MODEL")

        if not api_key:
            raise RuntimeError(
                "OPENROUTER_API_KEY is not set. Add it to the AeroMind .env file."
            )

        if not model:
            raise RuntimeError(
                "OPENROUTER_MODEL is not set. Add the OpenRouter model name to the AeroMind .env file."
            )

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
        )
        self.model = model

    def generate(self, prompt: str) -> str:
        """Generate a text response from a complete prompt."""
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("prompt cannot be empty")

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": prompt,
                }
            ],
        )

        content = response.choices[0].message.content

        if not content:
            raise RuntimeError("The LLM returned an empty response.")

        return content.strip()
